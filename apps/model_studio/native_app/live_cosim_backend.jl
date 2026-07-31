module LiveCosimBackend

const RESPONSE_FIELDS = [
    "accepted",
    "connection_ok",
    "reason_code",
    "profile_id",
    "profile_hash",
    "rt0_status",
    "output_rate_hz",
    "latency_p99_ms",
    "requested_rate_hz",
    "target_host",
    "rt1_udp_port",
    "ros_master_reachable",
    "rt1_reachable",
    "rtt_p95_ms",
    "payload_bytes_per_s",
    "wire_bytes_per_s",
]

function project_root(appfile)
    configured = strip(get(ENV, "MOSIM_ROOT", ""))
    if !isempty(configured) && isfile(joinpath(configured, "Scripts", "agent", "codex_cli_agent_server.py"))
        return normpath(configured)
    end
    current = normpath(dirname(appfile))
    for _ in 1:8
        isfile(joinpath(current, "Scripts", "agent", "codex_cli_agent_server.py")) && return current
        parent = dirname(current)
        parent == current && break
        current = parent
    end
    return normpath(joinpath(dirname(appfile), "..", "..", ".."))
end

function profile_key(label)
    return occursin("awff", lowercase(label)) ? "official_pid_awff" : "official_pid"
end

function request(appfile, action, label; host="127.0.0.1", port=49020, ros_master_uri="http://127.0.0.1:11311", local_advertised_ip="auto", rate_hz=200)
    root = project_root(appfile)
    backend = joinpath(root, "Scripts", "mworks_live", "model_studio_live_backend.py")
    command = `python $backend $action --profile $(profile_key(label)) --format tsv --host $host --port $port --ros-master-uri $ros_master_uri --local-advertised-ip $local_advertised_ip --rate-hz $rate_hz`
    try
        raw = chomp(read(command, String))
        values = split(raw, '\t'; keepempty=true)
        if length(values) != length(RESPONSE_FIELDS)
            return Dict("accepted" => "false", "reason_code" => "live_backend_malformed_response")
        end
        return Dict(RESPONSE_FIELDS[index] => String(values[index]) for index in eachindex(RESPONSE_FIELDS))
    catch error
        return Dict("accepted" => "false", "reason_code" => "live_backend_unavailable:" * string(typeof(error)))
    end
end

end
