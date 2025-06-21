# MCP Video Downloader

A Model Context Protocol (MCP) server that provides video downloading capabilities 
using yt-dlp. This server allows AI assistants like Claude to download videos from 
various platforms directly to your local filesystem using Docker volumes.

## Features

- 🎥 Download videos from 100+ platforms (YouTube, Vimeo, TikTok, etc.)
- 📐 Quality selection (best, 720p, 480p, 360p)
- 💾 Direct filesystem access via Docker volumes
- ✅ No file size limitations
- 🐳 Containerized for easy deployment and secure isolated environment
- 🔧 Claude Desktop integration ready

## Configuration Options

### Video Quality

- `best` - Highest available quality
- `worst` - Lowest available quality
- `720p` - Maximum 720p resolution (default)
- `480p` - Maximum 480p resolution
- `360p` - Maximum 360p resolution

## Prerequisites

- Docker installed and running
- Basic knowledge of file system paths
- Claude Desktop (for MCP integration)
- ~200MB disk space for the Docker image

## File Structure

```
mcp-video-downloader/
├── src/mcp_video_downloader/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py          # Main MCP server implementation
├── Dockerfile             # Container configuration
├── pyproject.toml         # Python dependencies
├── uv.lock                # Dependency lock file
└── README.md              # This file
```

## Quick Start
This guide shows you how to configure the MCP Video Downloader server with 
Claude Desktop using Docker volumes for file access.

### Step 1: Choose Your Downloads Directory

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

### Step 2: Build the Docker Image

Navigate to the MCP Video Downloader project directory and build the Docker image:

```bash
git clone <repository-url>
cd mcp-video-downloader
docker build -t mcp-video-downloader .
```

### Step 3: Configure Claude Desktop

Edit your Claude Desktop MCP configuration file:

#### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

#### Configuration Content

Add the following configuration to your `claude_desktop_config.json` file:

##### For macOS/Linux:

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume",
        "/Users/yourusername/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

##### For Windows:

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume",
        "C:\\Users\\yourusername\\Downloads\\mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

**Important**: Replace `yourusername` with your actual username and adjust the path to match your chosen downloads directory.

##### Configuration Explanation

- `--rm`: Automatically removes the container when it stops
- `-i`: Keeps STDIN open for MCP communication
- `--volume`: Mounts your local directory to `/downloads` in the container
- `--safe-mode`: Uses the JSON-safe output wrapper for MCP protocol

### Step 4: Complete Example Configurations

#### macOS Example

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume",
        "/Users/jane-doe/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

#### Windows Example

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume",
        "C:\\Users\\jane-doe\\Downloads\\mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

#### Linux Example

```json
{
  "mcpServers": {
    "mcp-video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--volume",
        "/home/jane-doe/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader",
        "--safe-mode"
      ]
    }
  }
}
```

### Step 5: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely:

1. Quit Claude Desktop
2. Wait a few seconds
3. Restart Claude Desktop

### Step 6: Test the Setup

In a new Claude Desktop conversation, try downloading a video:

```
Please download this YouTube video: https://www.youtube.com/watch?v=VIDEO_ID
```

Claude should be able to use the download_video tool, and the downloaded file will appear in your configured downloads directory.

### Tool Usage Examples

#### Download a video in 720p quality (default)

```
Download this video: https://www.youtube.com/watch?v=VIDEO_ID
```

#### Download in specific quality

```
Download this video in 480p quality: https://www.youtube.com/watch?v=VIDEO_ID
```

#### Download best quality available

```
Download this video in best quality: https://www.youtube.com/watch?v=VIDEO_ID
```

### Local Development

```bash
# Install dependencies with uv
uv sync

# Run the server locally
uv run python -m mcp_video_downloader
```

### Docker Development

```bash
# Build development image
docker build -t mcp-video-downloader:dev .

# Run with volume mount
docker run --rm -it \
  --volume "/path/to/downloads:/downloads" \
  mcp-video-downloader:dev
```

### Troubleshooting

#### Docker Permission Issues (Linux)

If you encounter permission issues on Linux, you may need to run Docker commands with `sudo` or add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.

#### Downloads Directory Permissions

Ensure the downloads directory has proper write permissions:

```bash
# macOS/Linux
chmod 755 ~/Downloads/mcp-videos

# Windows - usually not needed
```

#### MCP Server Not Starting

1. Check that Docker is running
2. Verify the Docker image was built successfully:
   ```bash
   docker images | grep mcp-video-downloader
   ```
3. Test the Docker container manually:
   ```bash
   docker run --rm -it --volume "/path/to/your/downloads:/downloads" mcp-video-downloader --safe-mode
   ```

#### Files Not Appearing

1. Check that the volume mount path is correct in your configuration
2. Verify the downloads directory exists and has write permissions
3. Test with a simple video download to ensure the tool is working

### Security Considerations

- The MCP server only has access to the specific directory you mount
- Downloaded files are saved with standard file permissions
- The Docker container runs with default user privileges
- Consider using a dedicated downloads directory for MCP videos

### Supported Platforms

The MCP Video Downloader supports hundreds of video platforms through yt-dlp, including:

- YouTube
- Vimeo
- Twitch
- Facebook
- Instagram
- TikTok
- And many more

For a complete list, see the [yt-dlp supported sites documentation](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Claude Desktop
5. Submit a pull request

## License
This project is licensed under the MIT License.
