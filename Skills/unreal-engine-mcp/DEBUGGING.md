# Debugging & Troubleshooting Guide

This guide addresses the most common issues users encounter when setting up and using the Unreal Engine MCP Server.

## Common Setup Issues

### 1. Claude Desktop Configuration Errors

**Problem**: Following the video tutorial to edit `claude_desktop_config.json` causes Claude Desktop to show errors.

**Symptoms**:
- Claude Desktop displays error messages related to configuration
- The application may fail to start properly
- MCP server connection fails

If the file doesn't exist, create it with the following content:

```json
{
  "mcpServers": {
    "unreal-advanced": {
      "command": "python",
      "args": [
        "C:\\Path\\To\\Your\\unreal-engine-mcp\\Python\\unreal_mcp_server_advanced.py"
      ]
    }
  }
}
```

**Important**: Replace `"C:\\Path\\To\\Your\\"` with your actual path to the unreal-engine-mcp directory.

### 2. Python MCP Module Not Found

**Problem**: Getting `ModuleNotFoundError: No module named 'mcp'` when trying to run the server.

**Symptoms**:
```
Traceback (most recent call last):
  File "C:\Users\...\unreal-engine-mcp\Python\unreal_mcp_server_advanced.py", line 14, in <module>
    from mcp.server.fastmcp import FastMCP
ModuleNotFoundError: No module named 'mcp'
```

**Root Cause**: The MCP package is not installed in your Python environment.

**Solution**:

1. **Identify your Python installation path** from the error logs (it will show something like `C:\Python311\python.exe`)

2. **Install the MCP package** using the full path to your Python executable:
   ```bash
   C:\Python311\python.exe -m pip install mcp
   ```

   Or if you're using Python 3.12+ as recommended:
   ```bash
   python -m pip install mcp
   ```

3. **Update pip** if you encounter installation issues:
   ```bash
   C:\Python311\python.exe -m pip install --upgrade pip
   ```

4. **Restart Claude Desktop** after installation

### 3. FastMCP Version Compatibility Issues

**Problem**: Getting errors related to `FastMCP` description field or version incompatibilities.

**Symptoms**:
- Server fails to start with FastMCP-related errors
- Description field causing parsing issues

**Solution**:

1. **Open the server file**: `Python/unreal_mcp_server_advanced.py`

2. **Comment out or remove the description field** around line 15-20:
   ```python
   # Remove or comment out this line if you get FastMCP errors:
   # description="...",
   ```

3. **Restart Claude Desktop** after making changes


### Check MCP Installation
```bash
python -c "import mcp; print('MCP installed successfully')"
```

### Check Server Logs
When Claude Desktop starts, check the developer console/logs for:
- Successful MCP server connection
- Any error messages
- Server initialization logs

```
