module AgentIntegration

using Base64
using Dates

const DEFAULT_HOST = "127.0.0.1"
const DEFAULT_PORT = 8765
const server_process = Ref{Any}(nothing)

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

function runtime_log(appfile, event, detail="")
    normalized = replace(replace(string(detail), '\n' => " | "), '\r' => " ")
    try
        path = joinpath(project_root(appfile), "Results", "ui_platform", "model_studio_assistant_runtime.log")
        mkpath(dirname(path))
        open(path, "a") do io
            timestamp = Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS")
            println(io, timestamp * "\tagent\t" * string(event) * "\t" * normalized)
        end
    catch
        # Logging must never block the assistant request path.
    end
end

function python_executable()
    return get(ENV, "MOSIM_PYTHON", get(ENV, "PYTHON", "python"))
end

function server_script(root)
    return joinpath(root, "Scripts", "agent", "codex_cli_agent_server.py")
end

function client_script(root)
    return joinpath(root, "Scripts", "agent", "mworks_analysis_agent_client.py")
end

function agent_command(root, arguments)
    return Cmd(Cmd(vcat([python_executable(), client_script(root)], arguments)); dir=root)
end

function decode_field(value)
    isempty(value) && return ""
    try
        return String(base64decode(value))
    catch
        return ""
    end
end

function health(appfile)
    root = project_root(appfile)
    isfile(client_script(root)) || return (ok=false, configured=false, detail="助手客户端脚本不存在")
    try
        raw = chomp(read(agent_command(root, ["health", "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT)]), String))
        fields = split(raw, '\t'; keepempty=true)
        length(fields) == 2 && fields[1] == "health" || return (ok=false, configured=false, detail="助手健康检查返回格式错误")
        payload = decode_field(fields[2])
        configured = occursin(r"\"configured\"\s*:\s*true", payload)
        return (ok=occursin(r"\"status\"\s*:\s*\"ok\"", payload), configured=configured, detail=payload)
    catch error
        return (ok=false, configured=false, detail=sprint(showerror, error))
    end
end

function start_agent_service(appfile)
    root = project_root(appfile)
    script = server_script(root)
    runtime_log(appfile, "service_start_requested", script)
    if !isfile(script)
        runtime_log(appfile, "service_script_missing", script)
        return (ok=false, configured=false, detail="助手服务脚本不存在")
    end
    current = health(appfile)
    if current.ok
        runtime_log(appfile, "service_already_ready", current.detail)
        return current
    end
    try
        server_process[] = run(
            Cmd(Cmd([python_executable(), script, "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT)]); dir=root);
            wait=false,
        )
    catch error
        detail = "启动助手服务失败：" * sprint(showerror, error)
        runtime_log(appfile, "service_start_error", detail)
        return (ok=false, configured=false, detail=detail)
    end
    for _ in 1:20
        sleep(0.15)
        current = health(appfile)
        if current.ok
            runtime_log(appfile, "service_ready", current.detail)
            return current
        end
    end
    runtime_log(appfile, "service_start_timeout", current.detail)
    return (ok=false, configured=false, detail="助手服务启动超时")
end

function ensure_agent_service(appfile)
    current = health(appfile)
    return current.ok ? current : start_agent_service(appfile)
end

function query_mworks_agent(appfile, question::AbstractString, context_text::AbstractString; model="", attachments=String[])
    root = project_root(appfile)
    ready = ensure_agent_service(appfile)
    ready.ok || return (
        ok=false,
        answer="助手服务不可用：" * ready.detail,
        tools=String[],
        request_id="",
        error_code="agent_service_unavailable",
        configured=false,
    )
    question_b64 = base64encode(String(question))
    context_b64 = base64encode(String(context_text))
    attachments_b64 = base64encode(join(String.(attachments), "\n"))
    command_args = [
        "query", "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT),
        "--question-b64", question_b64, "--context-b64", context_b64,
        "--model", String(model), "--attachments-b64", attachments_b64,
    ]
    try
        raw = chomp(read(
            agent_command(root, command_args),
            String,
        ))
        fields = split(raw, '\t'; keepempty=true)
        if length(fields) == 6 && fields[1] == "query"
            tools = filter(item -> !isempty(item), strip.(split(decode_field(fields[4]), ',')))
            return (
                ok=fields[2] == "1",
                answer=decode_field(fields[3]),
                tools=tools,
                request_id=decode_field(fields[5]),
                error_code=decode_field(fields[6]),
                configured=ready.configured,
            )
        elseif length(fields) >= 3 && fields[1] == "error"
            return (
                ok=false,
                answer="助手请求失败：" * decode_field(fields[3]),
                tools=String[],
                request_id="",
                error_code="agent_client_error",
                configured=ready.configured,
            )
        end
        return (
            ok=false,
            answer="助手客户端返回格式错误。",
            tools=String[],
            request_id="",
            error_code="agent_client_malformed_response",
            configured=ready.configured,
        )
    catch error
        return (
            ok=false,
            answer="助手请求失败：" * sprint(showerror, error),
            tools=String[],
            request_id="",
            error_code="agent_client_unavailable",
            configured=ready.configured,
        )
    end
end

function turn_failure(detail; configured=false, error_code="agent_client_error")
    return (
        ok=false,
        status="failed",
        answer=String(detail),
        partial_answer="",
        activities=String[],
        request_id="",
        error_code=error_code,
        codex_thread_id="",
        error=String(detail),
        configured=configured,
    )
end

function parse_turn_response(raw, configured)
    fields = split(raw, '\t'; keepempty=true)
    if length(fields) == 10 && fields[1] == "turn"
        activities = filter(item -> !isempty(item), strip.(split(decode_field(fields[6]), ',')))
        return (
            ok=fields[2] == "1",
            status=decode_field(fields[3]),
            answer=decode_field(fields[4]),
            partial_answer=decode_field(fields[5]),
            activities=activities,
            request_id=decode_field(fields[7]),
            error_code=decode_field(fields[8]),
            codex_thread_id=decode_field(fields[9]),
            error=decode_field(fields[10]),
            configured=configured,
        )
    elseif length(fields) >= 3 && fields[1] == "error"
        return turn_failure("助手请求失败：" * decode_field(fields[3]); configured=configured)
    end
    return turn_failure("助手客户端返回格式错误。"; configured=configured, error_code="agent_client_malformed_response")
end

function run_turn_client(appfile, arguments)
    root = project_root(appfile)
    runtime_log(appfile, "client_request", isempty(arguments) ? "" : string(arguments[1]))
    ready = ensure_agent_service(appfile)
    if !ready.ok
        runtime_log(appfile, "client_service_unavailable", ready.detail)
        return turn_failure("助手服务不可用：" * ready.detail; configured=false, error_code="agent_service_unavailable")
    end
    try
        raw = chomp(read(agent_command(root, arguments), String))
        result = parse_turn_response(raw, ready.configured)
        runtime_log(appfile, "client_response", "status=" * string(result.status) * "; request_id=" * string(result.request_id))
        return result
    catch error
        runtime_log(appfile, "client_error", sprint(showerror, error))
        return turn_failure("助手请求失败：" * sprint(showerror, error); configured=ready.configured, error_code="agent_client_unavailable")
    end
end

function start_mworks_turn(
    appfile,
    question::AbstractString,
    context_text::AbstractString;
    model="",
    attachments=String[],
    codex_thread_id="",
)
    runtime_log(appfile, "turn_start", "question_chars=" * string(length(String(question))))
    question_b64 = base64encode(String(question))
    context_b64 = base64encode(String(context_text))
    attachments_b64 = base64encode(join(String.(attachments), "\n"))
    return run_turn_client(appfile, [
        "turn-start", "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT),
        "--question-b64", question_b64, "--context-b64", context_b64,
        "--model", String(model), "--attachments-b64", attachments_b64,
        "--thread-id", String(codex_thread_id), "--timeout", "15",
    ])
end

function poll_mworks_turn(appfile, request_id::AbstractString)
    runtime_log(appfile, "turn_poll", "request_id=" * String(request_id))
    isempty(strip(String(request_id))) && return turn_failure("缺少会话请求编号。"; error_code="missing_request_id")
    return run_turn_client(appfile, [
        "turn-status", "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT),
        "--request-id", String(request_id), "--timeout", "15",
    ])
end

function cancel_mworks_turn(appfile, request_id::AbstractString)
    isempty(strip(String(request_id))) && return turn_failure("缺少会话请求编号。"; error_code="missing_request_id")
    return run_turn_client(appfile, [
        "turn-cancel", "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT),
        "--request-id", String(request_id), "--timeout", "15",
    ])
end

function stop_agent_service()
    process = server_process[]
    server_process[] = nothing
    process === nothing && return
    try
        process_running(process) && kill(process)
    catch
        # A server may have exited or been started by a prior Studio session.
    end
end

atexit(stop_agent_service)

end
