# MCP Video Downloader

A Model Context Protocol (MCP) server that provides video downloading capabilities using yt-dlp. This server allows AI assistants like Claude to download videos from various platforms directly to your local filesystem using Docker volumes.

## Features

- 🎥 Download videos from 100+ platforms (YouTube, Vimeo, TikTok, etc.)
- 🎵 Extract audio-only files (MP3 format)
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

### 2. Configure Claude Desktop

See the detailed setup guide: **[CLAUDE_DESKTOP_SETUP.md](./CLAUDE_DESKTOP_SETUP.md)**

### 3. Example Usage

Once configured, you can ask Claude to download videos:

```
Download this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

```
Extract audio from this video: https://www.youtube.com/watch?v=VIDEO_ID
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

### Audio Extraction

Set `audio_only: true` to extract MP3 audio files instead of video.

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
