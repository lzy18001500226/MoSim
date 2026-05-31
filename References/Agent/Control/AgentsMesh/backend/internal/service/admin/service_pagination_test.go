package admin

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNormalizePagination(t *testing.T) {
	tests := []struct {
		name           string
		page           int
		pageSize       int
		total          int64
		expectedPage   int
		expectedSize   int
		expectedOffset int
		expectedPages  int
	}{
		{
			name:           "normal case",
			page:           1,
			pageSize:       20,
			total:          100,
			expectedPage:   1,
			expectedSize:   20,
			expectedOffset: 0,
			expectedPages:  5,
		},
		{
			name:           "page less than 1 normalizes to 1",
			page:           0,
			pageSize:       20,
			total:          50,
			expectedPage:   1,
			expectedSize:   20,
			expectedOffset: 0,
			expectedPages:  3,
		},
		{
			name:           "negative page normalizes to 1",
			page:           -5,
			pageSize:       10,
			total:          30,
			expectedPage:   1,
			expectedSize:   10,
			expectedOffset: 0,
			expectedPages:  3,
		},
		{
			name:           "pageSize less than 1 defaults to 20",
			page:           1,
			pageSize:       0,
			total:          100,
			expectedPage:   1,
			expectedSize:   20,
			expectedOffset: 0,
			expectedPages:  5,
		},
		{
			name:           "pageSize over 100 caps at 100",
			page:           1,
			pageSize:       200,
			total:          500,
			expectedPage:   1,
			expectedSize:   100,
			expectedOffset: 0,
			expectedPages:  5,
		},
		{
			name:           "page 2 calculates correct offset",
			page:           2,
			pageSize:       20,
			total:          100,
			expectedPage:   2,
			expectedSize:   20,
			expectedOffset: 20,
			expectedPages:  5,
		},
		{
			name:           "partial last page",
			page:           1,
			pageSize:       20,
			total:          45,
			expectedPage:   1,
			expectedSize:   20,
			expectedOffset: 0,
			expectedPages:  3,
		},
		{
			name:           "zero total",
			page:           1,
			pageSize:       20,
			total:          0,
			expectedPage:   1,
			expectedSize:   20,
			expectedOffset: 0,
			expectedPages:  0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := normalizePagination(tt.page, tt.pageSize, tt.total)
			assert.Equal(t, tt.expectedPage, result.Page)
			assert.Equal(t, tt.expectedSize, result.PageSize)
			assert.Equal(t, tt.expectedOffset, result.Offset)
			assert.Equal(t, tt.expectedPages, result.TotalPages)
		})
	}
}
