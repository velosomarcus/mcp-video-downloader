# Claude Desktop MCP Video Downloader Setup

This guide shows you how to configure the MCP Video Downloader server with Claude Desktop using Docker volumes for file access.

## Overview

The MCP Video Downloader server runs in a Docker container and downloads videos to a `/downloads` directory inside the container. This directory is mounted as a Docker volume to your local filesystem, allowing you to access downloaded files directly from your computer.

## Prerequisites

- Docker installed and running
- Claude Desktop installed
- Basic knowledge of file system paths

## Step 1: Choose Your Downloads Directory

First, decide where on your local machine you want downloaded videos to be saved. For example:

- **macOS/Linux**: `/Users/yourusername/Downloads/mcp-videos` or `~/Downloads/mcp-videos`
- **Windows**: `C:\Users\yourusername\Downloads\mcp-videos`

Create this directory if it doesn't exist:

```bash
# macOS/Linux
mkdir -p ~/Downloads/mcp-videos

# Windows (PowerShell)
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\Downloads\mcp-videos" -Force
```

## Step 2: Build the Docker Image

Navigate to the MCP Video Downloader project directory and build the Docker image:

```bash
cd /path/to/mcp-video-downloader
docker build -t mcp-video-downloader .
```

## Step 3: Configure Claude Desktop

Edit your Claude Desktop MCP configuration file:

### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

### Configuration Content

Add the following configuration to your `claude_desktop_config.json` file:

#### For macOS/Linux:

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume", "/Users/yourusername/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

#### For Windows:

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume", "C:\\Users\\yourusername\\Downloads\\mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

**Important**: Replace `yourusername` with your actual username and adjust the path to match your chosen downloads directory.

### Configuration Explanation

- `--rm`: Automatically removes the container when it stops
- `-i`: Keeps STDIN open for MCP communication
- `--volume`: Mounts your local directory to `/downloads` in the container
- `--safe-mode`: Uses the JSON-safe output wrapper for MCP protocol

## Step 4: Complete Example Configurations

### macOS Example

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume", "/Users/john/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

### Windows Example

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume", "C:\\Users\\john\\Downloads\\mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

### Linux Example

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume", "/home/john/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

## Step 5: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely:

1. Quit Claude Desktop
2. Wait a few seconds
3. Restart Claude Desktop

## Step 6: Test the Setup

In a new Claude Desktop conversation, try downloading a video:

```
Please download this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Claude should be able to use the download_video tool, and the downloaded file will appear in your configured downloads directory.

## Tool Usage Examples

### Download a video in 720p quality (default)

```
Download this video: https://www.youtube.com/watch?v=VIDEO_ID
```

### Download only audio

```
Extract the audio from this video: https://www.youtube.com/watch?v=VIDEO_ID
```

### Download in specific quality

```
Download this video in 480p quality: https://www.youtube.com/watch?v=VIDEO_ID
```

## Troubleshooting

### Docker Permission Issues (Linux)

If you encounter permission issues on Linux, you may need to run Docker commands with `sudo` or add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.

### Downloads Directory Permissions

Ensure the downloads directory has proper write permissions:

```bash
# macOS/Linux
chmod 755 ~/Downloads/mcp-videos

# Windows - usually not needed
```

### MCP Server Not Starting

1. Check that Docker is running
2. Verify the Docker image was built successfully:
   ```bash
   docker images | grep mcp-video-downloader
   ```
3. Test the Docker container manually:
   ```bash
   docker run --rm -it --volume "/path/to/your/downloads:/downloads" mcp-video-downloader --safe-mode
   ```

### Files Not Appearing

1. Check that the volume mount path is correct in your configuration
2. Verify the downloads directory exists and has write permissions
3. Test with a simple video download to ensure the tool is working

## Security Considerations

- The MCP server only has access to the specific directory you mount
- Downloaded files are saved with standard file permissions
- The Docker container runs with default user privileges
- Consider using a dedicated downloads directory for MCP videos

## Supported Platforms

The MCP Video Downloader supports hundreds of video platforms through yt-dlp, including:

- YouTube
- Vimeo
- Twitch
- Facebook
- Instagram
- TikTok
- And many more

For a complete list, see the [yt-dlp supported sites documentation](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).
