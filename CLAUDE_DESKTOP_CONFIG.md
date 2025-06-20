# Claude Desktop Configuration for MCP Video Downloader

## Quick Setup for Claude Desktop

This configuration uses the **streaming-based architecture** with direct file transfer via MCP protocol.

### 📝 MCP Configuration

Update your Claude Desktop MCP configuration file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration**:

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

### 🎯 What This Does

1. **Lightweight Container**: No volume mounting or persistent storage needed

2. **Streaming Transfer**: The server automatically:
   - Downloads videos using yt-dlp
   - Encodes files as base64 data
   - Transfers content directly via MCP protocol
   - Cleans up temporary files

### 📱 User Experience

When you ask Claude to download a video, you'll receive the file directly:

````
✅ Video downloaded and transferred successfully!

📁 File Information:
  • Filename: example_video.mp4
  • Size: 25.4 MB
  • Format: MP4 (720p)
  • Duration: 5:32

📤 Transfer Status:
  • Method: Base64 streaming
  • File received: Yes
  • Ready for use: Yes
### 🎯 Key Benefits

- **� Zero Configuration**: No volume mounting or directory setup required
- **⚡ Instant Access**: Files are immediately available in your Claude session
- **🧹 Clean Operation**: No persistent files or cleanup needed
- **📤 Direct Transfer**: Files streamed directly via MCP protocol

### 🔧 Advanced Usage

**Quality Options:**
You can specify download preferences when asking Claude:

- `"Download this video in best quality"`
- `"Download this video in 720p"`
- `"Extract audio only from this video"`

**Multiple Formats:**
The server supports various output formats and will automatically select the best available option.

## 🚨 Troubleshooting Connection Issues

### "Server transport closed unexpectedly" Error

If you see this error, try these solutions:

#### 🔧 **Solution 1: Rebuild Docker Image**

Ensure you have the latest image:

```bash
docker build -t mcp-video-downloader .
````

#### 🔧 **Solution 2: Check Docker Permissions**

Verify Docker is running and accessible:

```bash
docker run --rm hello-world
```

mkdir -p ~/Downloads/mcp-videos

````

Then use the absolute path configuration above.

#### 🔧 **Solution 3: Test Docker Permissions**

Verify Docker is running and accessible:

```bash
# Test basic Docker functionality
docker run --rm hello-world
````

If this fails, check Docker Desktop settings and ensure Docker is running properly.

#### 🔧 **Solution 4: Test Basic Configuration**

Try the standard streaming configuration to test connectivity:

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

✅ **Note**: This uses the streaming approach - files are transferred directly to Claude as base64 data.

#### 🔧 **Solution 5: Check Log Output**

Check Claude's logs for specific error messages. On macOS, logs are typically in:

- `~/Library/Logs/Claude/`
- Console app under "Claude"

#### 🔧 **Solution 6: Verify Docker Installation**

Ensure Docker is properly installed and running:

```bash
docker --version
docker run --rm hello-world
```

#### 🔧 **Solution 7: Debug Mode**

Enable debug output to see detailed error messages:

```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--env", "DEBUG=1", "mcp-video-downloader"]
    }
  }
}
```

### 🧪 **Testing Your Configuration**

Before updating Claude Desktop, test your Docker command manually:

```bash
# 1. Test Docker image exists
docker images mcp-video-downloader

# 2. Test manual execution
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | \
docker run -i --rm mcp-video-downloader

# You should see a JSON response with protocolVersion
```

### 📋 **Step-by-Step Diagnosis**

1. **Check Docker Installation**:

   ```bash
   docker --version
   docker run --rm hello-world
   ```

2. **Verify Image Exists**:

   ```bash
   docker images | grep mcp-video-downloader
   ```

   If missing, rebuild: `docker build -t mcp-video-downloader .`

3. **Test MCP Server**:

   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | \
   docker run -i --rm mcp-video-downloader
   ```

4. **Check Claude Desktop Logs** (if available):
   - Look for detailed error messages in Claude Desktop's console/logs

### ✅ **Working Configuration Template**

Use this simple, tested configuration:

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

**Common usernames**: Check with `whoami` command or `echo $HOME`

### 🆘 Troubleshooting

**Videos Not Appearing Locally?**

1. Check your Docker Desktop is running
   ]
   }
   }
   }

```

### 🔍 **Common Issues and Solutions**

1. **Image Not Found**: Run `docker build -t mcp-video-downloader .` in the project directory
2. **Protocol Errors**: Ensure you're using the latest version of the server
3. **Permission Issues**: Verify Docker has proper permissions on your system

### ✅ Benefits

- **Zero Configuration**: No volume mounting or directory setup required
- **Direct Transfer**: Files transferred immediately via MCP protocol
- **Clean Operation**: No persistent files or cleanup needed
- **Universal Compatibility**: Works with any MCP client
- **Lightweight**: Minimal container footprint

This streaming-based approach provides the simplest and most reliable experience for Claude Desktop users!
```
