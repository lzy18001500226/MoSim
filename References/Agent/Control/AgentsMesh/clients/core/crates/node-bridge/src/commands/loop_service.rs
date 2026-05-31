use napi_derive::napi;
use crate::AppState;

#[napi]
impl AppState {
    #[napi]
    pub async fn loop_svc_loops_json(&self) -> napi::Result<String> {
        let svc = self.loop_svc.lock().await;
            Ok(svc.loops_json())
    }

    #[napi]
    pub async fn loop_svc_current_loop_json(&self) -> napi::Result<String> {
        let svc = self.loop_svc.lock().await;
            Ok(svc.current_loop_json().unwrap_or_default())
    }

    #[napi]
    pub async fn loop_svc_runs_json(&self) -> napi::Result<String> {
        let svc = self.loop_svc.lock().await;
            Ok(svc.runs_json())
    }

    #[napi]
    pub async fn loop_svc_get_loop_by_slug_json(&self, slug: String) -> napi::Result<String> {
        let svc = self.loop_svc.lock().await;
            Ok(svc.get_loop_by_slug_json(&slug).unwrap_or_default())
    }

    #[napi]
    pub async fn loop_svc_set_loops(&self, json: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.set_loops(&json);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_set_current_loop(&self, json: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.set_current_loop(&json);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_update_loop_local(&self, slug: String, json: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.update_loop_local(&slug, &json);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_add_run(&self, json: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.add_run(&json);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_set_runs(&self, json: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.set_runs(&json);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_append_runs(&self, json: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.append_runs(&json);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_update_run_status(&self, run_id: i64, status: String) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.update_run_status(run_id, &status);
            Ok(())
    }

    #[napi]
    pub async fn loop_svc_clear_runs(&self) -> napi::Result<()> {
        let svc = self.loop_svc.lock().await;
            svc.clear_runs();
            Ok(())
    }
}
