# MCP Video Downloader

A Model Context Protocol (MCP) server that provides video downloading capabilities using yt-dlp. This server allows AI assistants like Claude to download videos from various platforms directly to your local filesystem using Docker volumes.

## Features

- 🎥 Download videos from 100+ platforms (YouTube, Vimeo, TikTok, etc.)
- 📐 Quality selection (best, 720p, 480p, 360p)
- 💾 Direct filesystem access via Docker volumes
- 🐳 Containerized for easy deployment
- 🔧 Claude Desktop integration ready

## Quick Start

### 1. Build the Docker Image

```bash
git clone <repository-url>
cd mcp-video-downloader
docker build -t mcp-video-downloader .
```

### 2. Test the Setup

Run the comprehensive test suite:

```bash
# Quick test (recommended)
./run_tests.sh --quick

# Full test suite
./run_tests.sh

# Test specific URL
make test-url URL=https://example.com/video.mp4
```

### 3. Configure Claude Desktop

See the detailed setup guide: **[CLAUDE_DESKTOP_SETUP.md](./CLAUDE_DESKTOP_SETUP.md)**

### 4. Example Usage

Once configured, you can ask Claude to download videos:

```
Download this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

```
Download this video in 480p quality: https://www.youtube.com/watch?v=VIDEO_ID
```

## Architecture

The MCP server runs in a Docker container and downloads videos to a `/downloads` directory, which is mounted as a volume to your local filesystem. This approach provides:

- ✅ Direct file system access
- ✅ No file size limitations
- ✅ No base64 encoding overhead
- ✅ Immediate file availability
- ✅ Secure isolated environment

## Configuration Options

### Video Quality

- `best` - Highest available quality
- `worst` - Lowest available quality
- `720p` - Maximum 720p resolution (default)
- `480p` - Maximum 480p resolution
- `360p` - Maximum 360p resolution

## Manual Testing

You can test the server manually without Claude Desktop:

```bash
# Create downloads directory
mkdir -p ~/Downloads/mcp-videos

# Run the container
docker run --rm -it \
  --volume "~/Downloads/mcp-videos:/downloads" \
  mcp-video-downloader
```

## Supported Platforms

Thanks to yt-dlp, this server supports hundreds of video platforms including:

- YouTube
- Vimeo
- Twitch
- Facebook
- Instagram
- TikTok
- Dailymotion
- And many more...

For a complete list, see the [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Requirements

- Docker
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
├── uv.lock               # Dependency lock file
├── README.md             # This file
└── CLAUDE_DESKTOP_SETUP.md # Claude Desktop configuration guide
```

## Development

### Testing

The project includes a comprehensive testing suite:

```bash
# Run all available tests
./run_tests.sh

# Quick test for basic functionality
./run_tests.sh --quick

# Verbose output for debugging
./run_tests.sh --verbose

# Test specific functionality
make test                    # Quick setup verification
make test-comprehensive      # Full video download tests
make test-manual            # Manual MCP client test
make test-url URL=<url>     # Test specific video URL
```

#### Available Test Files

- `run_tests.sh` - Main test runner with comprehensive checks
- `test-setup.sh` - Basic setup and Docker verification
- `test_video_download.py` - Comprehensive MCP protocol and download testing
- `minimal_mcp_client.py` - Simple MCP client for manual testing
- `Makefile` - Convenient test commands
- `docker-compose.test.yml` - Docker Compose testing setup

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

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure your downloads directory has write permissions
2. **Docker Not Running**: Start Docker Desktop or Docker daemon
3. **Volume Mount Issues**: Check that the local path exists and uses absolute paths

### Debugging

Enable verbose logging:

```bash
docker run --rm -it \
  --volume "/path/to/downloads:/downloads" \
  mcp-video-downloader \
  python -m mcp_video_downloader
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Claude Desktop
5. Submit a pull request

## License

[License information here]

## Support

- 📚 [Setup Guide](./CLAUDE_DESKTOP_SETUP.md)
- 🐛 [Issues](../../issues)
- 💬 [Discussions](../../discussions)
