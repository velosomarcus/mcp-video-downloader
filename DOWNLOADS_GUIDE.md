# Video Downloads Location

## Overview

The MCP Video Downloader client has been modified to automatically save downloaded videos to your local machine instead of keeping them inside the Docker container.

## Downloads Directory

**Default Location**: `~/Downloads/mcp-videos/`

All downloaded videos will be saved to this directory on your local machine.

## How It Works

1. **Automatic Directory Creation**: The client automatically creates the downloads directory if it doesn't exist
2. **Volume Mounting**: The Docker container is automatically configured with a volume mount to map the container's `/downloads` directory to your local downloads folder
3. **Persistent Storage**: Videos remain on your machine even after the Docker container exits

## Modified Docker Command

The client automatically transforms:

```bash
docker run -i --rm mcp-video-downloader
```

Into:

```bash
docker run -v /Users/mveloso/Downloads/mcp-videos:/downloads -i --rm mcp-video-downloader
```

## Customizing Download Location

You can specify a custom downloads directory when creating the client:

```python
from video_downloader_client import MCPVideoDownloaderClient

# Use custom directory
client = MCPVideoDownloaderClient(
    docker_cmd="docker run -i --rm mcp-video-downloader",
    local_downloads_dir="/path/to/your/custom/directory"
)
```

## Accessing Downloaded Files

### Via Code:

```python
# Get the downloads directory path
downloads_path = client.get_downloads_directory()
print(f"Files saved to: {downloads_path}")
```

### Via Finder (macOS):

```bash
open ~/Downloads/mcp-videos
```

### Via Terminal:

```bash
ls -la ~/Downloads/mcp-videos
```

## File Organization

Downloaded files will have names based on the video title:

- **Videos**: `Video Title.mp4` (or other video format)
- **Audio Only**: `Video Title.mp3`

## Benefits

1. ✅ **Persistent Storage**: Files don't disappear when container exits
2. ✅ **Easy Access**: Files are in your standard Downloads folder
3. ✅ **Automatic Setup**: No manual configuration required
4. ✅ **Customizable**: Can specify different download locations
5. ✅ **Organized**: All video downloads in one dedicated folder
