use std::sync::Arc;

use agentsmesh_persistence::{RunnerRepo, StorageBackend};
use agentsmesh_types::proto_runner_api_v1::Runner;

// Runner status comes off the proto wire as a string ("online" / "offline" /
// "registering" etc.). State cache stores the wire string verbatim; callers
// compare against these constants.
pub mod runner_status {
    pub const ONLINE: &str = "online";
    pub const OFFLINE: &str = "offline";
    pub const REGISTERING: &str = "registering";
    pub const ERROR: &str = "error";
    pub const UNKNOWN: &str = "unknown";
}

pub struct RunnerState {
    runners: Vec<Runner>,
    available_runners: Vec<Runner>,
    current_runner: Option<Runner>,
    repo: Option<RunnerRepo>,
}

impl RunnerState {
    pub fn new() -> Self {
        Self { runners: Vec::new(), available_runners: Vec::new(), current_runner: None, repo: None }
    }

    pub fn with_storage(backend: Arc<dyn StorageBackend>) -> Self {
        let repo = RunnerRepo::new(backend);
        let runners = repo.list_all().unwrap_or_default();
        Self { runners, available_runners: Vec::new(), current_runner: None, repo: Some(repo) }
    }

    pub fn runners(&self) -> &[Runner] { &self.runners }
    pub fn available_runners(&self) -> &[Runner] { &self.available_runners }
    pub fn current_runner(&self) -> Option<&Runner> { self.current_runner.as_ref() }

    pub fn set_runners(&mut self, runners: Vec<Runner>) {
        self.runners = runners;
        if let Some(repo) = &self.repo {
            for r in &self.runners { let _ = repo.save(r); }
        }
    }

    pub fn set_available_runners(&mut self, runners: Vec<Runner>) {
        self.available_runners = runners;
    }

    pub fn set_current_runner(&mut self, runner: Option<Runner>) {
        self.current_runner = runner;
    }

    pub fn get_runner(&self, id: i64) -> Option<&Runner> {
        self.runners.iter().find(|r| r.id == id)
    }

    pub fn update_runner(&mut self, id: i64, runner: Runner) {
        if let Some(r) = self.runners.iter_mut().find(|r| r.id == id) {
            *r = runner.clone();
            if let Some(repo) = &self.repo { let _ = repo.save(r); }
        }
        if let Some(r) = self.available_runners.iter_mut().find(|r| r.id == id) {
            *r = runner.clone();
        }
        if self.current_runner.as_ref().is_some_and(|c| c.id == id) {
            self.current_runner = Some(runner);
        }
    }

    pub fn update_runner_status(&mut self, id: i64, status: &str) {
        for r in &mut self.runners {
            if r.id == id {
                r.status = status.to_string();
            }
        }

        if status != runner_status::ONLINE {
            self.available_runners.retain(|r| r.id != id);
        } else {
            for r in &mut self.available_runners {
                if r.id == id { r.status = status.to_string(); }
            }
        }

        if let Some(ref mut cur) = self.current_runner {
            if cur.id == id { cur.status = status.to_string(); }
        }

        if let Some(repo) = &self.repo {
            if let Some(r) = self.runners.iter().find(|r| r.id == id) {
                let _ = repo.save(r);
            }
        }
    }

    pub fn remove_runner(&mut self, id: i64) {
        self.runners.retain(|r| r.id != id);
        self.available_runners.retain(|r| r.id != id);
        if let Some(ref cur) = self.current_runner {
            if cur.id == id { self.current_runner = None; }
        }
        if let Some(repo) = &self.repo { let _ = repo.delete(id); }
    }

    pub fn can_accept_pods(runner: &Runner) -> bool {
        runner.is_enabled
            && runner.status == runner_status::ONLINE
            && runner.current_pods < runner.max_concurrent_pods
    }
}

impl Default for RunnerState {
    fn default() -> Self { Self::new() }
}
