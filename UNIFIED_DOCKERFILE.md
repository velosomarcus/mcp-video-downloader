# Unified Dockerfile Guide

## Overview

The MCP Video Downloader now uses a **single unified Dockerfile** that includes both normal operation and JSON-safe mode for Claude IDE compatibility. This eliminates the need for separate `Dockerfile.wrapper` and wrapper scripts.

## Unified Dockerfile Features

### Built-in Modes

The unified Dockerfile provides two execution modes:

1. **Normal Mode** (default): `docker run -i --rm mcp-video-downloader`
2. **Safe Mode** (for Claude IDE): `docker run -i --rm mcp-video-downloader --safe-mode`

### What's Included

- ✅ **Main application build** with uv and Python dependencies
- ✅ **FFmpeg installation** for video processing
- ✅ **Built-in wrapper script** for stderr suppression
- ✅ **Flexible entry point** that supports both modes
- ✅ **Environment optimization** for JSON protocol compliance

## Architecture

```dockerfile
# Multi-stage build with uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv
# ... dependency installation ...

FROM python:3.12-slim-bookworm
# ... final image setup ...

# Built-in wrapper script creation
RUN echo '#!/bin/bash\nexec python -m mcp_video_downloader 2>/dev/null' > /usr/local/bin/mcp_wrapper.sh

# Flexible entry point script
RUN echo '#!/bin/bash\nif [ "$1" = "--safe-mode" ]; then\n  exec /usr/local/bin/mcp_wrapper.sh\nelse\n  exec mcp-video-downloader "$@"\nfi' > /usr/local/bin/mcp_entrypoint.sh

ENTRYPOINT ["/usr/local/bin/mcp_entrypoint.sh"]
```

## Claude IDE Configuration

### Option 1: Normal Mode (try first)

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

### Option 2: Safe Mode (if JSON errors occur)

```json
{
  "mcpServers": {
    "video-downloader-safe": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader", "--safe-mode"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

### Option 3: Both Modes (recommended)

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader"],
      "env": { "PYTHONUNBUFFERED": "1" }
    },
    "video-downloader-safe": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader", "--safe-mode"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

## Building and Testing

### Build the unified image:

```bash
docker build -t mcp-video-downloader .
```

### Test normal mode:

```bash
echo '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"clientInfo":{"name":"test","version":"1.0.0"}}}' | docker run -i --rm mcp-video-downloader
```

### Test safe mode:

```bash
echo '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"clientInfo":{"name":"test","version":"1.0.0"}}}' | docker run -i --rm mcp-video-downloader --safe-mode
```

### Automated testing:

```bash
python3 fix_claude_json.py
```

## Migration from Previous Setup

### Before (multiple files):

- `Dockerfile` - Main application
- `Dockerfile.wrapper` - Wrapper image
- `mcp_wrapper.sh` - Wrapper script
- Multiple Docker images to build

### After (unified):

- `Dockerfile` - Everything included
- Single Docker image
- Built-in mode switching
- Simplified configuration

### Migration steps:

1. **Remove old files** (optional cleanup):

   ```bash
   rm -f Dockerfile.wrapper mcp_wrapper.sh
   docker rmi mcp-video-downloader-wrapper 2>/dev/null || true
   ```

2. **Rebuild with unified Dockerfile**:

   ```bash
   docker build -t mcp-video-downloader .
   ```

3. **Update Claude Desktop config** to use unified configuration

4. **Test both modes** to ensure compatibility

## Troubleshooting

### If normal mode has JSON errors:

- Switch to safe mode: add `--safe-mode` to the Docker args
- Safe mode redirects stderr to `/dev/null` to prevent JSON contamination

### If both modes fail:

- Check Docker image build: `docker build -t mcp-video-downloader .`
- Test manually: `docker run -i --rm mcp-video-downloader --help`
- Check Claude Desktop logs for additional error details

### For debugging:

- Use the debug script: `python3 debug_mcp_json.py`
- Check container logs: `docker logs <container_id>`
- Test with minimal JSON: Use the test commands above

## Benefits of Unified Approach

- ✅ **Single Dockerfile** - Easier maintenance and building
- ✅ **Flexible modes** - Switch between normal and safe mode as needed
- ✅ **Built-in solutions** - No need for external wrapper files
- ✅ **Simplified deployment** - One image for all use cases
- ✅ **Better documentation** - All options clearly defined
- ✅ **Easier debugging** - Consistent build and test process

The unified Dockerfile provides all the functionality of the previous multi-file approach while being much simpler to use and maintain!
