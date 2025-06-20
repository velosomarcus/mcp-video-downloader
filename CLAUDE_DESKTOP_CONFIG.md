# Claude Desktop Configuration for Solution 1

## Quick Setup for Claude Desktop

This configuration uses **Solution 1: Docker Default Volume** with enhanced path reporting.

### 📝 MCP Configuration

Update your Claude Desktop MCP configuration file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration**:

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

### 🎯 What This Does

1. **Volume Mount**: `-v ~/Downloads/mcp-videos:/downloads`

   - Maps your local `~/Downloads/mcp-videos/` directory to container's `/downloads`
   - Creates the local directory automatically if it doesn't exist

2. **Smart Server**: The enhanced server automatically:
   - Detects the volume mount
   - Uses `/downloads` for persistent storage
   - Reports both container and local file paths
   - Provides clear volume status information

### 📱 User Experience

When you ask Claude to download a video, you'll receive comprehensive information:

```
✅ Video downloaded successfully!

📹 Title: Introduction to Machine Learning
👤 Uploader: DataScienceChannel
⏱️ Duration: 12.5 minutes

📁 File Locations:
  • Container: /downloads/Introduction to Machine Learning.mp4
  • Local: /Users/yourname/Downloads/mcp-videos/Introduction to Machine Learning.mp4
💾 Size: 156.3 MB
🔧 Mode: Video

🎯 Volume Mount Status:
  • Using Docker volume: Yes
  • Local directory: /Users/yourname/Downloads/mcp-videos
  • File accessible on host: Yes

Progress Log:
  • Downloading Introduction to Machine Learning.mp4: 100% at 2.1MiB/s
```

### 📂 File Access

After downloading, your videos will be available at:

- **Local Path**: `~/Downloads/mcp-videos/`
- **Full Path**: `/Users/yourname/Downloads/mcp-videos/VideoTitle.mp4`

### 🔧 Customization Options

**Change Local Directory:**

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

**Multiple Quality Options:**
The server supports quality parameters you can mention to Claude:

- `"Download this video in best quality"`
- `"Download this video in 720p"`
- `"Extract audio only from this video"`

## 🚨 Troubleshooting Connection Issues

### "Server transport closed unexpectedly" Error

If you see this error, try these solutions in order:

#### 🔧 **Solution 1: Use Absolute Path**

Claude Desktop may not expand `~` properly. Use the full path:

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
        "/Users/YOUR_USERNAME/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader"
      ]
    }
  }
}
```

**Replace `YOUR_USERNAME` with your actual username.**

#### 🔧 **Solution 2: Create Directory First**

Manually create the downloads directory:

```bash
mkdir -p ~/Downloads/mcp-videos
```

Then use the absolute path configuration above.

#### 🔧 **Solution 3: Test Docker Permissions**

Verify Docker can access your file system:

```bash
# Test basic Docker functionality
docker run --rm hello-world

# Test volume mounting
docker run --rm -v ~/Downloads:/test alpine:latest ls /test
```

If these fail, check Docker Desktop settings:

1. Open Docker Desktop
2. Go to Settings → Resources → File Sharing
3. Ensure your home directory is shared

#### 🔧 **Solution 4: Simplified Configuration**

Try without volume mount first to test basic connectivity:

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

⚠️ **Note**: This saves files inside the container (temporary storage).

#### 🔧 **Solution 5: Alternative Volume Syntax**

Try different volume mount syntax:

```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--volume",
        "/Users/YOUR_USERNAME/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader"
      ]
    }
  }
}
```

#### 🔧 **Solution 6: Debug Mode**

Enable Docker logging to see detailed error messages:

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
        "/Users/YOUR_USERNAME/Downloads/mcp-videos:/downloads",
        "--env",
        "DEBUG=1",
        "mcp-video-downloader"
      ]
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
docker run -i --rm -v ~/Downloads/mcp-videos:/downloads mcp-video-downloader

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

3. **Test Volume Mount**:

   ```bash
   mkdir -p ~/Downloads/mcp-videos
   docker run --rm -v ~/Downloads/mcp-videos:/downloads alpine:latest touch /downloads/test.txt
   ls ~/Downloads/mcp-videos/  # Should show test.txt
   rm ~/Downloads/mcp-videos/test.txt
   ```

4. **Test MCP Server**:

   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | \
   docker run -i --rm -v ~/Downloads/mcp-videos:/downloads mcp-video-downloader
   ```

5. **Check Claude Desktop Logs** (if available):
   - Look for detailed error messages in Claude Desktop's console/logs

### ✅ **Working Configuration Template**

Once you identify your username, use this template:

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
        "/Users/YOUR_USERNAME/Downloads/mcp-videos:/downloads",
        "mcp-video-downloader"
      ]
    }
  }
}
```

**Common usernames**: Check with `whoami` command or `echo $HOME`

### 🆘 Troubleshooting

**Videos Not Appearing Locally?**

1. Check your Docker Desktop is running
2. Verify the configuration file path and syntax
3. Restart Claude Desktop after configuration changes
4. Check that Docker has permission to access your Downloads folder

**Path Issues?**

- The server now reports both container and local paths
- Look for the "Local" path in the download response
- Files should appear in `~/Downloads/mcp-videos/` by default

**Permission Errors?**

- Make sure Docker Desktop has access to your file system
- Try creating the `~/Downloads/mcp-videos/` directory manually first

### ✅ Benefits

- **Persistent Storage**: Videos remain after Docker container exits
- **Clear Path Information**: Always know where your files are located
- **Automatic Setup**: Server handles volume detection automatically
- **Standard Docker**: Uses familiar Docker volume mounting
- **No Special Tools**: Just Docker and Claude Desktop

This is the recommended approach for Claude Desktop users!
