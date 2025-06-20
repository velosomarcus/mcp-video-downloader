# MCP Video Downloader with Streaming Transfer 📹

A robust Model Context Protocol (MCP) server that provides intelligent video downloading capabilities with **streaming file transfer** and **seamless client integration**.

## 🎯 Key Features

- **� Streaming Transfer**: Files streamed directly to client as base64-encoded data
- **🎬 Multi-Platform Support**: YouTube, Vimeo, and many other platforms via yt-dlp
- **⚙️ Quality Options**: Choose video quality or extract audio-only
- **📊 Progress Tracking**: Real-time download progress and detailed feedback
- **🧹 Auto Cleanup**: Temporary files automatically cleaned up after transfer
- **🔧 Simple Setup**: No volume mounting or file system configuration needed

## 🚀 Quick Start

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
      "args": ["run", "-i", "--rm", "mcp-video-downloader"]
    }
  }
}
```

### 3. Start Using!

Ask Claude:

> "Download this video for me: https://youtube.com/watch?v=example"

The video will be streamed directly to Claude as base64-encoded data!

## 📊 Enhanced User Experience

When downloading, you'll receive comprehensive information:

```
✅ Video downloaded successfully!

📹 Title: Amazing Tutorial
👤 Uploader: TechChannel
⏱️ Duration: 15.2 minutes

� File Data:
  • File Name: Amazing Tutorial.mp4
  • Size: 45.2 MB
  • MIME Type: video/mp4
  • Base64 encoded: Yes

📡 Transfer Status:
  • Streamed to client: Yes
  • Temporary files cleaned: Yes
  • Ready for client processing: Yes
```

## 🎬 Video Download Tool

### Supported Parameters

- **url** (required): Video URL from supported platforms
- **format_selector** (optional): Quality selector like `best[height<=720]`, `worst`, `bestaudio` (default: `best[height<=720]`)
- **extract_audio** (optional): Extract MP3 audio only (default: `false`)

### Supported Platforms

- YouTube, YouTube Music
- Vimeo, Dailymotion
- SoundCloud, Bandcamp
- And [1000+ more via yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## 🔧 Manual Usage

### Direct Docker Usage

```bash
# Simple streaming approach - no volume mount needed
docker run -i --rm mcp-video-downloader
```

### Alternative Configurations

**Using wrapper script:**

```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "/path/to/run-mcp-video-downloader.sh",
      "args": []
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
- ✅ Ensure Docker is running and accessible

**Stream processing issues?**

- � Files are streamed as base64 data to the client
- � No local file system access needed
- � Check client's ability to process base64 encoded files

**Connection errors?**

- 🔐 Verify Docker daemon is running
- 🔐 Check MCP client can execute Docker commands
- 🔐 Ensure no firewall blocking Docker communication

### Debug Mode

Set environment variable for verbose logging:

```bash
docker run -i --rm -e DEBUG=1 mcp-video-downloader
```

## 🏗️ Dependencies

- **[mcp](https://github.com/modelcontextprotocol/python-sdk)**: Model Context Protocol framework
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: Powerful video downloader
- **[pydantic](https://pydantic.dev)**: Data validation and settings
- **Docker**: Container runtime

## 📄 License

This project is open source. See individual dependencies for their respective licenses.

## 🤝 Contributing

Issues and pull requests welcome! This project demonstrates practical MCP server implementation with streaming file transfer.

## 📚 Documentation

- **[📖 Universal Setup Guide](UNIVERSAL_SETUP.md)** - Comprehensive setup and usage guide
- **[� Streaming Examples](streaming_usage_examples.py)** - Code examples for streaming approach

## 🛠️ Technical Architecture

- **🔄 Async Operations**: Non-blocking video downloads
- **🛡️ Error Handling**: Comprehensive validation and error reporting
- **� Streaming Transfer**: Direct base64 file content delivery
- **🧹 Auto Cleanup**: Automatic temporary file management
- **📊 Progress Feedback**: Real-time download status
