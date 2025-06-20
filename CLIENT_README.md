# MCP Video Downloader Client

A simple MCP (Model Context Protocol) client designed to test the video downloader server in this repository.

## Overview

This client connects to the MCP video downloader server running in Docker and provides a convenient interface to test the video downloading functionality:

- **download_video** - A comprehensive video downloading tool using yt-dlp

## Features

- **Automated Testing**: Runs predefined tests to verify server functionality
- **Interactive Mode**: Allows manual testing with custom URLs and parameters
- **Comprehensive Error Handling**: Provides detailed error messages and debugging information
- **Progress Tracking**: Shows download progress and results
- **Multiple Quality Options**: Supports various video quality settings
- **Audio Extraction**: Can download audio-only versions of videos

## Prerequisites

1. **Docker**: The MCP server runs in a Docker container
2. **Python 3.10+**: For running the client
3. **Built Docker Image**: The video downloader server image must be built first

## Building the Server

Before using the client, build the MCP video downloader server:

```bash
# Build the Docker image
docker build --no-cache -t mcp-video-downloader .
```

## Usage

### Basic Demo Mode

Run the client with predefined test cases:

```bash
python video_downloader_client.py
```

This will:

1. Connect to the MCP server
2. List available tools
3. Attempt to download a test video
4. Test audio-only extraction

### Interactive Mode

For manual testing with custom URLs:

```bash
python video_downloader_client.py --interactive
```

Interactive mode provides a menu-driven interface where you can:

- Download videos with custom URLs
- Choose video quality (best/720p/480p/360p)
- Extract audio-only versions
- List available tools

## Client Features

### Connection Management

- Automatic Docker container startup
- MCP protocol initialization
- Graceful connection cleanup

### Tool Testing

- **Video Download Tool**: Tests video downloading with various parameters

### Error Handling

- Network connectivity issues
- Invalid URLs
- Server errors
- Docker container problems

### Output Formatting

- Color-coded status messages
- Structured result display
- Progress indicators
- Detailed error reporting

## Example Output

```
🚀 Starting MCP Video Downloader Server: docker run -i --rm mcp-video-downloader
🔌 Initializing MCP connection...
✅ Server capabilities: {'tools': {}}
🎉 MCP connection established!

====================================
 Available Tools
====================================
🛠️  Available tools:
   • download_video: Download videos from various platforms (YouTube, Vimeo, etc.) using yt-dlp.

====================================
 Testing Video Download Tool
====================================
📹 Downloading video from: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   Quality: 360p, Audio only: False
📋 Result:
✅ Video downloaded successfully!

📹 Title: Rick Astley - Never Gonna Give You Up (Official Music Video)
👤 Uploader: Rick Astley
⏱️ Duration: 3.5 minutes
📁 File: /tmp/Rick Astley - Never Gonna Give You Up (Official Music Video).mp4
💾 Size: 15.2 MB
🔧 Mode: Video
```

## Supported Video Platforms

The server uses yt-dlp, which supports hundreds of video platforms including:

- YouTube
- Vimeo
- TikTok
- Twitter/X
- Instagram
- Facebook
- And many more

## Quality Options

- **best**: Highest available quality
- **720p**: Maximum 720p resolution
- **480p**: Maximum 480p resolution
- **360p**: Maximum 360p resolution
- **worst**: Lowest available quality

## Audio Extraction

When `audio_only=True`:

- Extracts audio track from the video
- Converts to MP3 format (192 kbps)
- Smaller file size and faster download

## Troubleshooting

### Common Issues

1. **Docker image not found**

   ```bash
   docker build -t mcp-video-downloader .
   ```

2. **Network connectivity issues**

   - Check internet connection
   - Verify video URL is accessible
   - Some videos may be geo-restricted

3. **Permission errors**

   - Ensure Docker has proper permissions
   - Check write permissions for temp directory

4. **Video unavailable**
   - URL may be invalid or expired
   - Video might be private or deleted
   - Platform may block automated downloads

### Debug Mode

For additional debugging information:

- Check Docker container logs
- The client shows stderr output on errors
- Use shorter test videos for faster debugging

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│  Python Client  │◄──►│  Docker Container│◄──►│   yt-dlp Core   │
│                 │    │   MCP Server     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
   JSON-RPC over              MCP Protocol              Video Download
   stdin/stdout              Implementation               & Processing
```

## Development

To modify or extend the client:

1. **Add new test cases**: Modify the `main()` function
2. **Add new tools**: Extend the client methods
3. **Improve error handling**: Update exception handling
4. **Add new features**: Follow the existing pattern

## License

This client is provided as an example for testing the MCP video downloader server. Use in accordance with your local laws and the terms of service of video platforms.
