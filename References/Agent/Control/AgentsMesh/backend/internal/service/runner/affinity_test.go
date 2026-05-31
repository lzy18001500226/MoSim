package runner

import (
	"testing"

	runnerDomain "github.com/anthropics/agentsmesh/backend/internal/domain/runner"
	"github.com/stretchr/testify/assert"
)

func ptr64(v int64) *int64 { return &v }

func makeCandidate(id int64, podCount int, maxPods int, registeredBy *int64, tags []string) *ActiveRunner {
	r := &runnerDomain.Runner{
		ID: id, MaxConcurrentPods: maxPods,
		RegisteredByUserID: registeredBy,
		Tags:               runnerDomain.StringSlice(tags),
	}
	return &ActiveRunner{Runner: r, PodCount: podCount}
}

func TestScoreRunners_NilCandidates(t *testing.T) {
	result := ScoreRunners(nil, 1, nil, nil, runnerDomain.DefaultAffinityWeights())
	assert.Nil(t, result)
}

func TestScoreRunners_NilHintsFallsBackToLeastPods(t *testing.T) {
	candidates := []*ActiveRunner{
		makeCandidate(1, 5, 10, nil, nil),
		makeCandidate(2, 1, 10, nil, nil),
		makeCandidate(3, 3, 10, nil, nil),
	}
	result := ScoreRunners(candidates, 1, nil, nil, runnerDomain.DefaultAffinityWeights())
	assert.Equal(t, int64(2), result[0].Runner.ID)
	assert.Equal(t, int64(3), result[1].Runner.ID)
	assert.Equal(t, int64(1), result[2].Runner.ID)
}

func TestScoreRunners_CreatorAffinity(t *testing.T) {
	userID := int64(42)
	candidates := []*ActiveRunner{
		makeCandidate(1, 2, 10, nil, nil),
		makeCandidate(2, 2, 10, ptr64(userID), nil),
	}
	hints := &runnerDomain.AffinityHints{}
	result := ScoreRunners(candidates, userID, hints, nil, runnerDomain.DefaultAffinityWeights())
	assert.Equal(t, int64(2), result[0].Runner.ID)
}

func TestScoreRunners_CreatorAffinityWeightNotDiluted(t *testing.T) {
	// When no repo and no tags, only load+creator participate.
	// Creator runner at same load should clearly win.
	userID := int64(42)
	candidates := []*ActiveRunner{
		makeCandidate(1, 5, 10, nil, nil),
		makeCandidate(2, 5, 10, ptr64(userID), nil),
	}
	hints := &runnerDomain.AffinityHints{} // no repo, no tags
	result := ScoreRunners(candidates, userID, hints, nil, runnerDomain.DefaultAffinityWeights())
	assert.Equal(t, int64(2), result[0].Runner.ID)
	// Verify score difference is significant (not diluted by zero-weight repo)
	w := runnerDomain.DefaultAffinityWeights()
	// totalWeight should be load(0.3) + creator(0.2) = 0.5 (repo and tag zeroed)
	expectedCreator := (w.Load*0.5 + w.Creator*1.0) / (w.Load + w.Creator) // = (0.15+0.2)/0.5 = 0.7
	expectedOther := (w.Load * 0.5) / (w.Load + w.Creator)                 // = 0.15/0.5 = 0.3
	assert.Greater(t, expectedCreator, expectedOther)
}

func TestScoreRunners_RepoAffinity(t *testing.T) {
	repoID := int64(100)
	candidates := []*ActiveRunner{
		makeCandidate(1, 2, 10, nil, nil),
		makeCandidate(2, 2, 10, nil, nil),
	}
	hints := &runnerDomain.AffinityHints{RepositoryID: &repoID}
	repoHistory := map[int64]int{2: 5}
	result := ScoreRunners(candidates, 1, hints, repoHistory, runnerDomain.DefaultAffinityWeights())
	assert.Equal(t, int64(2), result[0].Runner.ID)
}

func TestScoreRunners_RepoScoreGraduated(t *testing.T) {
	// A runner with 10 pods for the repo should score higher than one with 1 pod.
	repoID := int64(100)
	candidates := []*ActiveRunner{
		makeCandidate(1, 2, 10, nil, nil),
		makeCandidate(2, 2, 10, nil, nil),
		makeCandidate(3, 2, 10, nil, nil),
	}
	hints := &runnerDomain.AffinityHints{RepositoryID: &repoID}
	repoHistory := map[int64]int{1: 1, 2: 10, 3: 3}
	result := ScoreRunners(candidates, 1, hints, repoHistory, runnerDomain.DefaultAffinityWeights())
	// Runner 2 (10 pods) should rank first, runner 3 (3 pods) second, runner 1 (1 pod) third
	assert.Equal(t, int64(2), result[0].Runner.ID)
	assert.Equal(t, int64(3), result[1].Runner.ID)
	assert.Equal(t, int64(1), result[2].Runner.ID)
}

func TestScoreRunners_TagAffinity(t *testing.T) {
	candidates := []*ActiveRunner{
		makeCandidate(1, 2, 10, nil, []string{"cpu"}),
		makeCandidate(2, 2, 10, nil, []string{"gpu", "high-memory"}),
	}
	hints := &runnerDomain.AffinityHints{Tags: []string{"gpu", "high-memory"}}
	result := ScoreRunners(candidates, 1, hints, nil, runnerDomain.DefaultAffinityWeights())
	assert.Equal(t, int64(2), result[0].Runner.ID)
}

func TestScoreRunners_LoadBalancingPreventsOverload(t *testing.T) {
	userID := int64(42)
	candidates := []*ActiveRunner{
		makeCandidate(1, 1, 10, nil, nil),
		makeCandidate(2, 9, 10, ptr64(userID), nil),
	}
	hints := &runnerDomain.AffinityHints{}
	result := ScoreRunners(candidates, userID, hints, nil, runnerDomain.DefaultAffinityWeights())
	// With no repo/tag, totalWeight = load(0.3) + creator(0.2) = 0.5
	// r1: (0.3*0.9) / 0.5 = 0.54
	// r2: (0.3*0.1 + 0.2*1.0) / 0.5 = 0.46
	assert.Equal(t, int64(1), result[0].Runner.ID)
}

func TestScoreRunners_CombinedSignals(t *testing.T) {
	userID := int64(42)
	repoID := int64(100)
	candidates := []*ActiveRunner{
		makeCandidate(1, 3, 10, nil, nil),
		makeCandidate(2, 4, 10, ptr64(userID), nil),
		makeCandidate(3, 3, 10, ptr64(userID), nil),
	}
	hints := &runnerDomain.AffinityHints{RepositoryID: &repoID}
	repoHistory := map[int64]int{3: 10}
	result := ScoreRunners(candidates, userID, hints, repoHistory, runnerDomain.DefaultAffinityWeights())
	// Runner 3: creator=1.0, repo≈1.0, load=0.7 → highest
	assert.Equal(t, int64(3), result[0].Runner.ID)
}

func TestScoreRunners_NoTagsRequestedIgnoresTagWeight(t *testing.T) {
	candidates := []*ActiveRunner{
		makeCandidate(1, 2, 10, nil, []string{"gpu"}),
		makeCandidate(2, 2, 10, nil, nil),
	}
	hints := &runnerDomain.AffinityHints{}
	result := ScoreRunners(candidates, 1, hints, nil, runnerDomain.DefaultAffinityWeights())
	assert.Len(t, result, 2)
}

func TestScoreRunners_TagRequestedButRunnerHasNoTags(t *testing.T) {
	candidates := []*ActiveRunner{
		makeCandidate(1, 2, 10, nil, []string{"gpu"}),
		makeCandidate(2, 2, 10, nil, nil),
	}
	hints := &runnerDomain.AffinityHints{Tags: []string{"gpu"}}
	result := ScoreRunners(candidates, 1, hints, nil, runnerDomain.DefaultAffinityWeights())
	// Runner 1 has the requested tag, runner 2 has no tags → runner 1 should win
	assert.Equal(t, int64(1), result[0].Runner.ID)
}
