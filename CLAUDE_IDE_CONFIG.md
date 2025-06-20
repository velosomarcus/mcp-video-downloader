# Claude IDE Configuration for Streaming MCP Video Downloader

## Overview

This guide shows how to configure the streaming MCP Video Downloader to work with Claude IDE (Claude Desktop). The streaming approach is much simpler than the volume mount approach because it doesn't require Docker volume configuration.

## Configuration Options

### Option 1: Direct Python Execution (Recommended for Development)

If you have Python and the dependencies installed locally:

**Claude Desktop Config Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "python",
      "args": ["-m", "mcp_video_downloader"],
      "cwd": "/path/to/your/mcp-video-downloader"
    }
  }
}
```

### Option 2: Docker Streaming (Recommended for Production)

Using Docker without volume mounts:

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader"]
    }
  }
}
```

### Option 3: uv Python Environment

If you're using uv for dependency management:

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_video_downloader"],
      "cwd": "/path/to/your/mcp-video-downloader"
    }
  }
}
```

## Key Differences from Volume Mount Approach

### Old Volume Mount Config (Complex):

```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/Users/username/Downloads/mcp-videos:/downloads", // Volume mount required
        "mcp-video-downloader"
      ]
    }
  }
}
```

### New Streaming Config (Simple):

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "mcp-video-downloader" // No volume mount needed!
      ]
    }
  }
}
```

## How It Works with Claude IDE

1. **Claude IDE** connects to the MCP server using the configured command
2. **MCP Server** (streaming version) downloads videos to temporary directories
3. **Server** encodes file content as base64 and includes it in the response
4. **Claude IDE** receives the response with embedded file data
5. **Files are automatically available** in Claude's context without manual file management

## Setup Steps

### Step 1: Build the Docker Image (if using Docker)

```bash
cd /path/to/your/mcp-video-downloader
docker build -t mcp-video-downloader .
```

### Step 2: Update Claude Desktop Configuration

1. Open Claude Desktop configuration file:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. Add the streaming configuration (choose one option above)

3. Save the file

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

### Step 4: Test the Integration

In Claude IDE, you can now ask:

- "Download this video: https://youtu.be/VIDEO_ID"
- "Download the audio from this video: https://youtu.be/VIDEO_ID"
- "Download this video in 720p quality: https://youtu.be/VIDEO_ID"

## Complete Example Configuration

Here's a complete Claude Desktop configuration with the streaming video downloader:

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## File Handling in Claude IDE

### How Files Are Handled:

1. **Server Response**: Contains base64-encoded file data
2. **Claude Processing**: Claude receives the file data in the tool response
3. **File Access**: Files are available in Claude's context for further processing

### Example Claude Conversation:

```
You: "Download this video: https://youtu.be/dQw4w9WgXcQ"

Claude: I'll download that video for you.

[Uses video-downloader-streaming tool]

Claude: ✅ Video downloaded successfully!

📹 Title: Rick Astley - Never Gonna Give You Up
👤 Uploader: Rick Astley
⏱️ Duration: 3.5 minutes
👀 Views: 1,400,000,000

📁 File Details:
• Name: Rick Astley - Never Gonna Give You Up.mp4
• Size: 8.2 MB
• Type: video/mp4

The video has been downloaded and is now available. The file data has been streamed directly through the MCP protocol.
```

## Troubleshooting

### Common Issues:

1. **Docker not found**:

   - Make sure Docker is installed and running
   - Verify with: `docker --version`

2. **Permission errors**:

   - Make sure Docker daemon is running
   - Check Docker permissions

3. **Server not responding**:

   - Check Claude Desktop logs for errors
   - Verify the MCP server starts correctly: `docker run -i --rm mcp-video-downloader`

4. **File size limitations**:
   - Very large files may hit memory limits
   - Consider using lower quality settings for large videos

### Debugging:

To test the MCP server manually:

```bash
# Test Docker container
docker run -i --rm mcp-video-downloader

# Test Python module
python -m mcp_video_downloader
```

## Advantages of Streaming Approach with Claude IDE

1. **Simplified Setup**: No volume mount configuration needed
2. **Portable**: Works on any system with Docker
3. **Secure**: Files don't persist in containers
4. **Integrated**: Files are directly available in Claude's context
5. **Cross-platform**: Same configuration works everywhere

## Migration from Volume Mount

If you're currently using the volume mount approach, simply:

1. Replace your existing configuration with the streaming version
2. Remove the `-v` volume mount arguments
3. Restart Claude Desktop

The streaming approach provides the same functionality with much simpler setup!
