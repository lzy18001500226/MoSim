FROM ghcr.io/gh05tcrew/pentestagent:latest

RUN git clone https://github.com/Wh0am123/MCP-Kali-Server.git

WORKDIR /app/MCP-Kali-Server/

RUN git checkout 61272cde048c236cc61c75e2fac3c06243c633dd

WORKDIR /app

RUN pip install --no-cache-dir -r MCP-Kali-Server/requirements.txt

COPY --chown=pentestagent:pentestagent mcp_servers.json /app/pentestagent/mcp/

# Expose any needed ports
EXPOSE 8080

# Default command
CMD ["python", "-m", "pentestagent"]