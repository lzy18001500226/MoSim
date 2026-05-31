#[uniffi::export(callback_interface)]
pub trait StorageCallback: Send + Sync {
    fn get(&self, key: String) -> Option<String>;
    fn set(&self, key: String, value: String);
    fn remove(&self, key: String);
}

#[uniffi::export(callback_interface)]
pub trait OutputCallback: Send + Sync {
    fn on_output(&self, pod_key: String, data: Vec<u8>);
}

#[uniffi::export(callback_interface)]
pub trait StatusCallback: Send + Sync {
    fn on_status_change(&self, pod_key: String, status: String);
}

#[uniffi::export(callback_interface)]
pub trait EventCallback: Send + Sync {
    fn on_event(&self, event_json: String);
}
