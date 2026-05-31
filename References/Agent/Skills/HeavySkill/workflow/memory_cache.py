"""Memory Cache for storing and managing reasoning trajectories."""

import random
from collections import Counter
from typing import List, Optional

from .utils import estimate_token_count, extract_boxed_answer


class MemoryCache:
    """Stores parallel reasoning trajectories and supports selection strategies."""

    def __init__(self, trajectories: Optional[List[str]] = None):
        self.trajectories: List[str] = trajectories or []
        self.deliberation_history: List[str] = []

    def add_trajectories(self, trajectories: List[str]):
        self.trajectories.extend(trajectories)

    def add_deliberation(self, summary: str):
        self.deliberation_history.append(summary)

    def select(self, k: int, strategy: str = "random") -> List[str]:
        """Select k trajectories from cache using the given strategy."""
        if len(self.trajectories) <= k:
            selected = list(self.trajectories)
        elif strategy == "random":
            selected = random.sample(self.trajectories, k)
        elif strategy == "max_answer_num":
            selected = self._select_by_answer_frequency(k)
        elif strategy == "max_diversity":
            selected = self._select_by_diversity(k)
        else:
            selected = random.sample(self.trajectories, k)

        random.shuffle(selected)
        return selected

    def _select_by_answer_frequency(self, k: int) -> List[str]:
        """Select trajectories whose answers appear most frequently."""
        answer_map = {}
        for traj in self.trajectories:
            answer = extract_boxed_answer(traj)
            if answer not in answer_map:
                answer_map[answer] = []
            answer_map[answer].append(traj)

        freq = Counter({a: len(ts) for a, ts in answer_map.items()})
        selected = []
        for answer, _ in freq.most_common():
            for traj in answer_map[answer]:
                if len(selected) >= k:
                    break
                selected.append(traj)
            if len(selected) >= k:
                break
        return selected[:k]

    def _select_by_diversity(self, k: int) -> List[str]:
        """Select trajectories that maximize answer diversity."""
        answer_map = {}
        for traj in self.trajectories:
            answer = extract_boxed_answer(traj)
            if answer not in answer_map:
                answer_map[answer] = []
            answer_map[answer].append(traj)

        selected = []
        answers = list(answer_map.keys())
        idx = 0
        while len(selected) < k and answers:
            answer = answers[idx % len(answers)]
            if answer_map[answer]:
                selected.append(answer_map[answer].pop(0))
            else:
                answers.remove(answer)
                if not answers:
                    break
                continue
            idx += 1
        return selected[:k]

    def get_all_for_deliberation(self) -> List[str]:
        """Get trajectories plus prior deliberation results for iterative refinement."""
        return self.trajectories + self.deliberation_history

    @property
    def total_token_estimate(self) -> int:
        return sum(estimate_token_count(t) for t in self.trajectories)

    def __len__(self) -> int:
        return len(self.trajectories)
