package v1

type listLoopsQuery struct {
	Status        string `form:"status"`
	ExecutionMode string `form:"execution_mode"`
	CronEnabled   *bool  `form:"cron_enabled"`
	Query         string `form:"query"`
	Limit         int    `form:"limit"`
	Offset        int    `form:"offset"`
}

type listRunsQuery struct {
	Status string `form:"status"`
	Limit  int    `form:"limit"`
	Offset int    `form:"offset"`
}
