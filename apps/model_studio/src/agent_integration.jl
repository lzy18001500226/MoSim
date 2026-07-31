module AgentIntegration

using Base64

const DEFAULT_HOST = "127.0.0.1"
const DEFAULT_PORT = 8765
const server_process = Ref{Any}(nothing)

function project_root(appfile)
    return normpath(joinpath(dirname(appfile), "..", "..", ".."))
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
    isfile(script) || return (ok=false, configured=false, detail="助手服务脚本不存在")
    current = health(appfile)
    current.ok && return current
    try
        server_process[] = run(
            Cmd(Cmd([python_executable(), script, "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT)]); dir=root);
            wait=false,
        )
    catch error
        return (ok=false, configured=false, detail="启动助手服务失败：" * sprint(showerror, error))
    end
    for _ in 1:20
        sleep(0.15)
        current = health(appfile)
        current.ok && return current
    end
    return (ok=false, configured=false, detail="助手服务启动超时")
end

function ensure_agent_service(appfile)
    current = health(appfile)
    return current.ok ? current : start_agent_service(appfile)
end

function query_mworks_agent(appfile, question::String, context_text::String)
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
    question_b64 = base64encode(question)
    context_b64 = base64encode(context_text)
    try
        raw = chomp(read(
            agent_command(root, [
                "query", "--host", DEFAULT_HOST, "--port", string(DEFAULT_PORT),
                "--question-b64", question_b64, "--context-b64", context_b64,
            ]),
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
