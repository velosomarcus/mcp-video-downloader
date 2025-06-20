# MCP Server with Video Download Tool

This module implements a Model Context Protocol (MCP) server that provides a tool to download video files.

- **download_video**
  - A video download tool using yt-dlp for downloading videos from various platforms

The server uses the MCP framework to expose this tool to AI assistants, allowing them to 
download videos from supported platforms like YouTube, Vimeo, etc.

## Architecture:
- Uses async/await pattern for non-blocking operations
- Implements proper error handling and validation
- Provides detailed progress feedback for video downloads
- Supports various video formats and quality options


## Building the image

Use the command below to build the image to Docker:
```bash
docker build -f Dockerfile mcp-video-downloader:latest .
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using docker</summary>

```json
"mcpServers": {
  "fetch": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "--pull=always", "mcp/fetch"]
  }
}
```
</details>



## Dependencies:
- mcp: Model Context Protocol framework
- yt-dlp: YouTube-dl fork for video downloading
- pydantic: Data validation and settings management
