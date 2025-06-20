#!/usr/bin/env python3
"""
Test script to demonstrate the new downloads directory functionality
"""

from video_downloader_client import MCPVideoDownloaderClient
from pathlib import Path

def test_downloads_directory():
    """Test the downloads directory setup"""
    print("🧪 Testing Downloads Directory Setup")
    print("=" * 50)
    
    # Create client (this should create the downloads directory)
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    # Check downloads directory
    downloads_dir = client.get_downloads_directory()
    print(f"📁 Downloads directory: {downloads_dir}")
    
    # Check if directory exists
    downloads_path = Path(downloads_dir)
    if downloads_path.exists():
        print("✅ Downloads directory was created successfully!")
        print(f"🔍 Directory path: {downloads_path.resolve()}")
        print(f"📂 Is directory: {downloads_path.is_dir()}")
        
        # List contents if any
        contents = list(downloads_path.iterdir())
        if contents:
            print(f"📄 Contents ({len(contents)} items):")
            for item in contents:
                print(f"   • {item.name}")
        else:
            print("📄 Directory is empty (as expected)")
    else:
        print("❌ Downloads directory was not created!")
    
    print("\n🚀 Docker Command Modification Test")
    print("=" * 50)
    
    # Test Docker command modification without actually running
    print(f"Original command: {docker_cmd}")
    
    # Simulate the command modification logic
    docker_parts = docker_cmd.split()
    run_index = -1
    for i, part in enumerate(docker_parts):
        if part == "run":
            run_index = i
            break
    
    if run_index != -1:
        volume_mount = f"-v{downloads_path}:/downloads"
        docker_parts.insert(run_index + 1, volume_mount)
        modified_command = " ".join(docker_parts)
        print(f"Modified command: {modified_command}")
        print("✅ Command modification successful!")
    else:
        print("❌ Could not find 'run' in Docker command")
    
    print(f"\n💡 To open the downloads folder in Finder, run:")
    print(f"   open {downloads_dir}")

if __name__ == "__main__":
    test_downloads_directory()
