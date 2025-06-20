#!/usr/bin/env python3
"""
Test script to verify Claude IDE configuration for MCP Video Downloader.
This simulates how Claude IDE would interact with the MCP server.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_claude_ide_config():
    """Test the Claude IDE configuration setup."""
    print("🧪 Testing Claude IDE MCP Configuration")
    print("=" * 50)
    
    # Check if the streaming config file exists
    config_path = Path("claude_desktop_config_streaming.json")
    if not config_path.exists():
        print("❌ Claude Desktop config file not found")
        return False
    
    # Load and validate the configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration file loaded successfully")
        
        # Check structure
        if "mcpServers" not in config:
            print("❌ Missing 'mcpServers' section")
            return False
        
        servers = config["mcpServers"]
        if not servers:
            print("❌ No MCP servers configured")
            return False
        
        # Find video downloader server
        video_server = None
        for name, server_config in servers.items():
            if "video" in name.lower():
                video_server = server_config
                server_name = name
                break
        
        if not video_server:
            print("❌ No video downloader server found")
            return False
        
        print(f"✅ Found video downloader server: {server_name}")
        
        # Validate server configuration
        if "command" not in video_server:
            print("❌ Missing 'command' in server config")
            return False
        
        if "args" not in video_server:
            print("❌ Missing 'args' in server config")
            return False
        
        command = video_server["command"]
        args = video_server["args"]
        
        print(f"✅ Server command: {command}")
        print(f"✅ Server args: {' '.join(args)}")
        
        # Test if the command is available
        if command == "docker":
            return test_docker_availability()
        elif command == "python":
            return test_python_availability()
        else:
            print(f"⚠️  Unknown command: {command}")
            return False
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def test_docker_availability():
    """Test if Docker is available and the container works."""
    print("\n🐳 Testing Docker setup...")
    
    try:
        # Check Docker version
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("❌ Docker not available")
            return False
        
        print(f"✅ Docker available: {result.stdout.strip()}")
        
        # Check if container image exists
        result = subprocess.run(
            ["docker", "images", "mcp-video-downloader", "--format", "{{.Repository}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "mcp-video-downloader" not in result.stdout:
            print("⚠️  MCP Video Downloader Docker image not found")
            print("   Build it with: docker build -t mcp-video-downloader .")
            return False
        
        print("✅ MCP Video Downloader Docker image found")
        
        # Test container startup (quick test)
        print("🔍 Testing container startup...")
        result = subprocess.run(
            ["docker", "run", "--rm", "mcp-video-downloader", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Container starts successfully")
            return True
        else:
            print(f"❌ Container startup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker test timed out")
        return False
    except FileNotFoundError:
        print("❌ Docker not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Docker test error: {e}")
        return False

def test_python_availability():
    """Test if Python module is available."""
    print("\n🐍 Testing Python setup...")
    
    try:
        # Test Python module import
        result = subprocess.run(
            [sys.executable, "-c", "import mcp_video_downloader; print('Module imported successfully')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Python module imports successfully")
            return True
        else:
            print(f"❌ Python module import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Python test error: {e}")
        return False

def simulate_claude_interaction():
    """Simulate how Claude IDE would interact with the MCP server."""
    print("\n🎭 Simulating Claude IDE interaction...")
    
    # This is a simplified simulation - actual Claude IDE interaction
    # would be more complex and handled by the MCP protocol
    
    sample_requests = [
        {
            "description": "List available tools",
            "expected": "download_video tool should be available"
        },
        {
            "description": "Download video request",
            "expected": "Should return base64-encoded file data"
        }
    ]
    
    for i, request in enumerate(sample_requests, 1):
        print(f"  {i}. {request['description']}")
        print(f"     Expected: {request['expected']}")
    
    print("\n📝 Note: Full MCP protocol testing requires Claude IDE or MCP client")
    return True

def main():
    """Main test function."""
    print("🎬 MCP Video Downloader - Claude IDE Configuration Test")
    print("=" * 60)
    
    success = True
    
    # Test configuration
    if not test_claude_ide_config():
        success = False
    
    # Simulate Claude interaction
    if not simulate_claude_interaction():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Configuration should work with Claude IDE.")
        print("\n📋 Next steps:")
        print("1. Copy the configuration to Claude Desktop")
        print("2. Restart Claude Desktop")
        print("3. Test with a video download request")
    else:
        print("⚠️  Some tests failed. Please fix the issues before using with Claude IDE.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
