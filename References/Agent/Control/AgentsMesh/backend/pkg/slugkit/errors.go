package slugkit

import "errors"

var (
	ErrEmpty              = errors.New("slug: empty")
	ErrTooShort           = errors.New("slug: too short")
	ErrTooLong            = errors.New("slug: too long")
	ErrInvalidFormat      = errors.New("slug: invalid format")
	ErrReserved           = errors.New("slug: reserved word")
	ErrCollisionExhausted = errors.New("slug: unable to find unique slug after retries")
)
