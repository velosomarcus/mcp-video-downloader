# MCP Video Downloader with Docker Volumes 📹

A robust Model Context Protocol (MCP) server that provides intelligent video downloading capabilities with **persistent storage** and **enhanced path reporting**.

## 🎯 Key Features

- **📁 Persistent Storage**: Downloads saved to your local machine via Docker volumes
- **🧠 Smart Path Detection**: Automatically detects volume mounts and reports local file paths
- **🎬 Multi-Platform Support**: YouTube, Vimeo, and many other platforms via yt-dlp
- **⚙️ Quality Options**: Choose video quality or extract audio-only
- **📊 Progress Tracking**: Real-time download progress and detailed feedback
- **🔍 Enhanced Reporting**: Complete file location information for users

## 🚀 Quick Start (Recommended: Solution 1)

### 1. Build the Docker Image

```bash
docker build -t mcp-video-downloader .
```

### 2. Configure Claude Desktop

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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
        "~/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader"
      ]
    }
  }
}
```

### 3. Start Using!

Ask Claude:

> "Download this video for me: https://youtube.com/watch?v=example"

Videos appear in: `~/Downloads/mcp-videos/`

## 📊 Enhanced User Experience

When downloading, you'll receive comprehensive information:

```
✅ Video downloaded successfully!

📹 Title: Amazing Tutorial
👤 Uploader: TechChannel
⏱️ Duration: 15.2 minutes

📁 File Locations:
  • Container: /downloads/Amazing Tutorial.mp4
  • Local: /Users/yourname/Downloads/mcp-videos/Amazing Tutorial.mp4
💾 Size: 45.2 MB

🎯 Volume Mount Status:
  • Using Docker volume: Yes
  • Local directory: /Users/yourname/Downloads/mcp-videos
  • File accessible on host: Yes
```

## 🎬 Video Download Tool

### Supported Parameters

- **url** (required): Video URL from supported platforms
- **output_path** (optional): Custom output directory
- **quality** (optional): `best`, `worst`, `720p`, `480p`, `360p` (default: `720p`)
- **audio_only** (optional): Extract MP3 audio only (default: `false`)

### Supported Platforms

- YouTube, YouTube Music
- Vimeo, Dailymotion
- SoundCloud, Bandcamp
- And [1000+ more via yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## 🔧 Manual Usage

### Direct Docker Usage

```bash
# With volume mount (recommended)
docker run -i --rm -v ~/Downloads/mcp-videos:/downloads mcp-video-downloader

# Without volume mount (temporary storage)
docker run -i --rm mcp-video-downloader
```

### Alternative Configurations

**Custom Download Directory:**

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
        "~/Movies/Downloaded Videos:/downloads",
        "mcp-video-downloader"
      ]
    }
  }
}
```

## 🆘 Troubleshooting

### Common Issues

**Videos not appearing locally?**

- ✅ Verify Docker Desktop is running
- ✅ Check MCP configuration syntax
- ✅ Restart Claude Desktop after changes
- ✅ Ensure Docker has file system permissions

**Path confusion?**

- 📁 Look for "Local" path in download response
- 📁 Files appear in `~/Downloads/mcp-videos/` by default
- 📁 Server reports both container and local paths

**Permission errors?**

- 🔐 Grant Docker Desktop file system access
- 🔐 Create download directory manually: `mkdir -p ~/Downloads/mcp-videos`

### Debug Mode

Set environment variable for verbose logging:

```bash
docker run -i --rm -e DEBUG=1 -v ~/Downloads/mcp-videos:/downloads mcp-video-downloader
```

## 🏗️ Dependencies

- **[mcp](https://github.com/modelcontextprotocol/python-sdk)**: Model Context Protocol framework
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: Powerful video downloader
- **[pydantic](https://pydantic.dev)**: Data validation and settings
- **Docker**: Container runtime

## 📄 License

This project is open source. See individual dependencies for their respective licenses.

## 🤝 Contributing

Issues and pull requests welcome! This project demonstrates practical MCP server implementation with Docker integration.

## 📚 Documentation

- **[📖 Solution 1 Guide](SOLUTION_1_DOCKER_VOLUMES.md)** - Comprehensive implementation details
- **[⚙️ Claude Desktop Setup](CLAUDE_DESKTOP_CONFIG.md)** - Quick configuration guide
- **[🐳 Multiple Solutions](DOCKER_CONTAINER_SOLUTIONS.md)** - All available approaches

## 🛠️ Technical Architecture

- **🔄 Async Operations**: Non-blocking video downloads
- **🛡️ Error Handling**: Comprehensive validation and error reporting
- **📁 Volume Intelligence**: Automatic Docker volume detection
- **🎯 Path Translation**: Container-to-local path mapping
- **📊 Progress Feedback**: Real-time download status
