package policy

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// --- Subject helpers ---

func member(orgID, userID int64) Subject  { return NewSubject(orgID, userID, "member") }
func admin(orgID, userID int64) Subject   { return NewSubject(orgID, userID, "admin") }
func owner(orgID, userID int64) Subject   { return NewSubject(orgID, userID, "owner") }
func apikey(orgID, userID int64) Subject  { return NewSubject(orgID, userID, "apikey") }

// --- NewSubject ---

func TestNewSubject(t *testing.T) {
	s := NewSubject(5, 7, "admin")
	assert.Equal(t, int64(5), s.OrgID)
	assert.Equal(t, int64(7), s.UserID)
	assert.Equal(t, "admin", s.Role)
}

// --- Typed constructors ---

func TestPodResource(t *testing.T) {
	rc := PodResource(1, 10)
	assert.Equal(t, int64(1), rc.OrgID)
	assert.Equal(t, int64(10), rc.OwnerID)
	assert.Empty(t, rc.Visibility)
}

func TestVisibleResource_NilOwner(t *testing.T) {
	rc := VisibleResource(1, nil, VisibilityPrivate)
	assert.Equal(t, int64(1), rc.OrgID)
	assert.Equal(t, int64(0), rc.OwnerID)
	assert.Equal(t, VisibilityPrivate, rc.Visibility)
}

func TestVisibleResource_NonNilOwner(t *testing.T) {
	uid := int64(42)
	rc := VisibleResource(1, &uid, VisibilityOrganization)
	assert.Equal(t, int64(42), rc.OwnerID)
	assert.Equal(t, VisibilityOrganization, rc.Visibility)
}

func TestWithGrants(t *testing.T) {
	original := PodResource(1, 10)
	granted := original.WithGrants([]int64{20, 30})
	assert.Nil(t, original.GrantedUserIDs, "original unchanged")
	assert.Equal(t, []int64{20, 30}, granted.GrantedUserIDs)
}

// --- AllowRead: ReadOwnerOnly (PodPolicy) ---

func TestAllowRead_OwnerOnly(t *testing.T) {
	p := PodPolicy
	res := PodResource(1, 10)

	cases := []struct {
		name string
		sub  Subject
		want bool
	}{
		{"member own pod", member(1, 10), true},
		{"member other pod", member(1, 99), false},
		{"admin other pod", admin(1, 99), true},
		{"owner role other pod", owner(1, 99), true},
		{"apikey any pod", apikey(1, 42), true},
		{"wrong org", admin(2, 10), false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, p.AllowRead(tc.sub, res))
		})
	}
}

// --- AllowRead: ReadVisibility (RunnerPolicy) ---

func TestAllowRead_Visibility_Organization(t *testing.T) {
	p := RunnerPolicy
	uid := int64(10)
	res := VisibleResource(1, &uid, "organization")

	cases := []struct {
		name string
		sub  Subject
		want bool
	}{
		{"member", member(1, 42), true},
		{"admin", admin(1, 99), true},
		{"apikey", apikey(1, 55), true},
		{"wrong org", member(2, 10), false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, p.AllowRead(tc.sub, res))
		})
	}
}

func TestAllowRead_Visibility_Private(t *testing.T) {
	p := RunnerPolicy
	uid := int64(10)
	res := VisibleResource(1, &uid, "private")

	cases := []struct {
		name string
		sub  Subject
		want bool
	}{
		{"owner", member(1, 10), true},
		{"other member", member(1, 42), false},
		{"admin (no bypass)", admin(1, 99), false},
		{"apikey (no bypass)", apikey(1, 55), false},
		{"wrong org", admin(2, 10), false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, p.AllowRead(tc.sub, res))
		})
	}
}

// --- AllowRead: grants within mode ---

func TestAllowRead_Grant_OwnerOnly(t *testing.T) {
	p := PodPolicy
	res := PodResource(1, 10).WithGrants([]int64{20})

	assert.True(t, p.AllowRead(member(1, 10), res), "owner")
	assert.True(t, p.AllowRead(member(1, 20), res), "granted user")
	assert.False(t, p.AllowRead(member(1, 30), res), "non-granted member")
}

func TestAllowRead_Grant_Visibility_Private(t *testing.T) {
	p := RunnerPolicy
	uid := int64(10)
	res := VisibleResource(1, &uid, "private").WithGrants([]int64{20})

	assert.True(t, p.AllowRead(member(1, 10), res), "owner of private runner")
	assert.True(t, p.AllowRead(member(1, 20), res), "granted user on private runner")
	assert.False(t, p.AllowRead(member(1, 30), res), "non-granted member")
	assert.False(t, p.AllowRead(admin(1, 99), res), "admin still blocked on private")
}

// --- AllowWrite: WriteCreatorAdmin (PodPolicy) ---

func TestAllowWrite_CreatorAdmin(t *testing.T) {
	p := PodPolicy
	res := PodResource(1, 10)

	cases := []struct {
		name string
		sub  Subject
		want bool
	}{
		{"creator", member(1, 10), true},
		{"other member", member(1, 42), false},
		{"admin", admin(1, 99), true},
		{"owner role", owner(1, 99), true},
		{"wrong org", admin(2, 10), false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, p.AllowWrite(tc.sub, res))
		})
	}
}

func TestAllowWrite_CreatorAdmin_WithGrants(t *testing.T) {
	p := PodPolicy
	res := PodResource(1, 10).WithGrants([]int64{20})

	assert.True(t, p.AllowWrite(member(1, 10), res), "creator")
	assert.True(t, p.AllowWrite(member(1, 20), res), "granted user can write")
	assert.False(t, p.AllowWrite(member(1, 30), res), "non-granted member cannot write")
}

// --- AllowWrite: WriteAdminOnly (RunnerPolicy) ---

func TestAllowWrite_AdminOnly(t *testing.T) {
	p := RunnerPolicy
	uid := int64(10)
	res := VisibleResource(1, &uid, "organization")

	cases := []struct {
		name string
		sub  Subject
		want bool
	}{
		{"admin", admin(1, 99), true},
		{"owner role", owner(1, 99), true},
		{"creator member", member(1, 10), false},
		{"other member", member(1, 42), false},
		{"wrong org", admin(2, 10), false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, p.AllowWrite(tc.sub, res))
		})
	}
}

// --- AllowAdmin ---

func TestAllowAdmin(t *testing.T) {
	assert.True(t, AllowAdmin(admin(1, 7), 1))
	assert.True(t, AllowAdmin(owner(1, 7), 1))
	assert.False(t, AllowAdmin(member(1, 7), 1))
	assert.False(t, AllowAdmin(apikey(1, 7), 1))
	assert.False(t, AllowAdmin(admin(2, 7), 1), "wrong org")
}

// --- ListFilter ---

func TestListFilter_OwnerOnly(t *testing.T) {
	p := PodPolicy
	f := p.ListFilter(member(1, 7))
	assert.Equal(t, int64(7), f.OwnerOnly)
	assert.Equal(t, int64(7), f.GrantUserID, "member gets grant filter")
	assert.Equal(t, int64(0), f.VisibilityUserID)

	f = p.ListFilter(admin(1, 7))
	assert.Equal(t, int64(0), f.OwnerOnly, "admin: no owner filter")
	assert.Equal(t, int64(0), f.GrantUserID, "admin: no grant filter needed")

	f = p.ListFilter(apikey(1, 7))
	assert.Equal(t, int64(0), f.OwnerOnly, "apikey: no owner filter")
}

func TestListFilter_Visibility(t *testing.T) {
	p := RunnerPolicy
	f := p.ListFilter(member(1, 7))
	assert.Equal(t, int64(0), f.OwnerOnly)
	assert.Equal(t, int64(7), f.VisibilityUserID)
	assert.Equal(t, int64(7), f.GrantUserID, "member gets grant filter")

	// Admin also gets visibility filtering (no admin bypass for ReadVisibility)
	f = p.ListFilter(admin(1, 7))
	assert.Equal(t, int64(7), f.VisibilityUserID, "admin also filtered")
	assert.Equal(t, int64(7), f.GrantUserID, "admin also gets grant filter for list")
}

func TestListFilter_OrgOpen(t *testing.T) {
	p := ResourcePolicy{Read: ReadOrgOpen, Write: WriteOrgOpen}
	f := p.ListFilter(member(1, 7))
	assert.Equal(t, int64(0), f.OwnerOnly)
	assert.Equal(t, int64(0), f.VisibilityUserID)
}
