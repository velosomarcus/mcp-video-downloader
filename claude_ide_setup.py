#!/usr/bin/env python3
"""
Claude IDE Integration Helper for MCP Video Downloader

This script helps set up the MCP Video Downloader for use with Claude IDE.
It provides configuration generation and testing utilities.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional

class ClaudeIDESetup:
    """Helper class for setting up MCP Video Downloader with Claude IDE."""
    
    def __init__(self):
        self.config_paths = self._get_config_paths()
    
    def _get_config_paths(self) -> Dict[str, str]:
        """Get Claude Desktop configuration paths for different platforms."""
        system = platform.system().lower()
        home = Path.home()
        
        if system == "darwin":  # macOS
            config_path = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif system == "windows":
            config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            config_path = home / ".config" / "claude" / "claude_desktop_config.json"
        
        return {
            "config_path": str(config_path),
            "config_dir": str(config_path.parent)
        }
    
    def generate_docker_config(self, server_name: str = "video-downloader-streaming") -> Dict[str, Any]:
        """Generate Claude Desktop configuration for Docker-based streaming server."""
        return {
            "mcpServers": {
                server_name: {
                    "command": "docker",
                    "args": [
                        "run", "-i", "--rm",
                        "mcp-video-downloader"
                    ],
                    "env": {
                        "PYTHONUNBUFFERED": "1"
                    }
                }
            }
        }
    
    def generate_python_config(self, 
                              project_path: str, 
                              server_name: str = "video-downloader-streaming") -> Dict[str, Any]:
        """Generate Claude Desktop configuration for Python-based streaming server."""
        return {
            "mcpServers": {
                server_name: {
                    "command": "python",
                    "args": ["-m", "mcp_video_downloader"],
                    "cwd": project_path,
                    "env": {
                        "PYTHONUNBUFFERED": "1"
                    }
                }
            }
        }
    
    def generate_uv_config(self, 
                          project_path: str, 
                          server_name: str = "video-downloader-streaming") -> Dict[str, Any]:
        """Generate Claude Desktop configuration for uv-based streaming server."""
        return {
            "mcpServers": {
                server_name: {
                    "command": "uv",
                    "args": ["run", "python", "-m", "mcp_video_downloader"],
                    "cwd": project_path,
                    "env": {
                        "PYTHONUNBUFFERED": "1"
                    }
                }
            }
        }
    
    def create_config_file(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """Create or update Claude Desktop configuration file."""
        config_path = Path(self.config_paths["config_path"])
        config_dir = Path(self.config_paths["config_dir"])
        
        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config if requested
        if backup and config_path.exists():
            backup_path = config_path.with_suffix(".json.backup")
            config_path.rename(backup_path)
            print(f"📄 Backed up existing config to: {backup_path}")
        
        # Load existing config if it exists
        existing_config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_config = {}
        
        # Merge configurations
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"].update(config["mcpServers"])
        
        # Write updated config
        try:
            with open(config_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            print(f"✅ Configuration written to: {config_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to write configuration: {e}")
            return False
    
    def test_docker_setup(self) -> bool:
        """Test if Docker setup is working."""
        import subprocess
        
        try:
            # Test Docker availability
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode != 0:
                print("❌ Docker is not available")
                return False
            
            print(f"✅ Docker available: {result.stdout.strip()}")
            
            # Test Docker container
            result = subprocess.run([
                "docker", "run", "--rm", 
                "mcp-video-downloader", "--help"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ MCP Video Downloader Docker container is working")
                return True
            else:
                print(f"❌ Docker container test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Docker test timed out")
            return False
        except FileNotFoundError:
            print("❌ Docker not found in PATH")
            return False
        except Exception as e:
            print(f"❌ Docker test failed: {e}")
            return False
    
    def test_python_setup(self, project_path: str) -> bool:
        """Test if Python setup is working."""
        import subprocess
        
        try:
            # Test Python module
            result = subprocess.run([
                "python", "-m", "mcp_video_downloader", "--help"
            ], cwd=project_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Python MCP Video Downloader module is working")
                return True
            else:
                print(f"❌ Python module test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Python test timed out")
            return False
        except FileNotFoundError:
            print("❌ Python not found in PATH")
            return False
        except Exception as e:
            print(f"❌ Python test failed: {e}")
            return False
    
    def show_usage_instructions(self):
        """Show instructions for using the video downloader in Claude IDE."""
        print("""
🎬 Using MCP Video Downloader in Claude IDE

Once configured, you can use these commands in Claude IDE:

1. Basic Video Download:
   "Download this video: https://youtu.be/VIDEO_ID"

2. Audio-Only Download:
   "Download the audio from this video: https://youtu.be/VIDEO_ID"

3. Quality Selection:
   "Download this video in 720p: https://youtu.be/VIDEO_ID"
   "Download this video in 480p: https://youtu.be/VIDEO_ID"

4. Multiple Downloads:
   "Download these videos: [list of URLs]"

📝 Note: Claude IDE will receive the file data through the MCP protocol.
The files are encoded as base64 and included in the tool response.
""")

def main():
    """Main setup interface."""
    print("🎬 MCP Video Downloader - Claude IDE Setup")
    print("=" * 50)
    
    setup = ClaudeIDESetup()
    
    print(f"📍 Claude Desktop config path: {setup.config_paths['config_path']}")
    print()
    
    # Setup options
    print("Choose setup method:")
    print("1. Docker (Recommended)")
    print("2. Python (Development)")
    print("3. uv (Advanced)")
    print("4. Test existing setup")
    print("5. Show usage instructions")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        # Docker setup
        print("\n🐳 Setting up Docker configuration...")
        
        if not setup.test_docker_setup():
            print("\n⚠️  Docker setup issues detected. Please fix them before continuing.")
            return
        
        config = setup.generate_docker_config()
        print(f"\n📄 Generated configuration:")
        print(json.dumps(config, indent=2))
        
        if input("\nWrite this configuration? (y/N): ").lower().startswith('y'):
            setup.create_config_file(config)
            print("\n✅ Docker configuration complete!")
            print("Restart Claude Desktop to load the new configuration.")
    
    elif choice == "2":
        # Python setup
        print("\n🐍 Setting up Python configuration...")
        project_path = input("Enter project path (or press Enter for current directory): ").strip()
        if not project_path:
            project_path = os.getcwd()
        
        if not setup.test_python_setup(project_path):
            print("\n⚠️  Python setup issues detected. Please fix them before continuing.")
            return
        
        config = setup.generate_python_config(project_path)
        print(f"\n📄 Generated configuration:")
        print(json.dumps(config, indent=2))
        
        if input("\nWrite this configuration? (y/N): ").lower().startswith('y'):
            setup.create_config_file(config)
            print("\n✅ Python configuration complete!")
            print("Restart Claude Desktop to load the new configuration.")
    
    elif choice == "3":
        # uv setup
        print("\n📦 Setting up uv configuration...")
        project_path = input("Enter project path (or press Enter for current directory): ").strip()
        if not project_path:
            project_path = os.getcwd()
        
        config = setup.generate_uv_config(project_path)
        print(f"\n📄 Generated configuration:")
        print(json.dumps(config, indent=2))
        
        if input("\nWrite this configuration? (y/N): ").lower().startswith('y'):
            setup.create_config_file(config)
            print("\n✅ uv configuration complete!")
            print("Restart Claude Desktop to load the new configuration.")
    
    elif choice == "4":
        # Test setup
        print("\n🧪 Testing existing setup...")
        
        config_path = Path(setup.config_paths["config_path"])
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print("✅ Configuration file found")
                
                servers = config.get("mcpServers", {})
                video_servers = [name for name in servers.keys() if "video" in name.lower()]
                
                if video_servers:
                    print(f"✅ Found video downloader servers: {', '.join(video_servers)}")
                else:
                    print("⚠️  No video downloader servers found in configuration")
                
            except Exception as e:
                print(f"❌ Error reading configuration: {e}")
        else:
            print("❌ No Claude Desktop configuration found")
    
    elif choice == "5":
        # Usage instructions
        setup.show_usage_instructions()
    
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
