#[cfg(test)]
mod api_pod_runner_tests {
    // Pod + runner REST mocks removed after R5-7 (list_runner_pods now
    // forwards to ListPods Connect) and R5-8 (get_runner_auth_status +
    // authorize_runner moved to proto.runner_api.v1). Connect handler
    // coverage lives under backend/internal/api/connect/{pod,runner}.
}
