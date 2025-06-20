#!/usr/bin/env python3
"""
Quick Test Script for MCP Video Downloader
This script performs basic connectivity and functionality tests.
"""

import subprocess
import sys
import json
import time

def run_command(cmd, timeout=30):
    """Run a command with timeout."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"

def test_docker_availability():
    """Test if Docker is available."""
    print("🐳 Testing Docker availability...")
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✅ Docker is available: {stdout.strip()}")
        return True
    else:
        print(f"❌ Docker not available: {stderr}")
        return False

def test_docker_image():
    """Test if the Docker image exists."""
    print("📦 Testing Docker image availability...")
    success, stdout, stderr = run_command("docker images mcp-video-downloader --format '{{.Repository}}:{{.Tag}}'")
    if success and "mcp-video-downloader" in stdout:
        print("✅ MCP Video Downloader Docker image found")
        return True
    else:
        print("❌ MCP Video Downloader Docker image not found")
        print("💡 Run: docker build -t mcp-video-downloader .")
        return False

def test_python_dependencies():
    """Test if required Python modules are available."""
    print("🐍 Testing Python dependencies...")
    required_modules = ['json', 'subprocess', 'sys']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} module available")
        except ImportError:
            print(f"❌ {module} module not available")
            return False
    
    return True

def test_client_syntax():
    """Test if the client script has valid syntax."""
    print("📝 Testing client script syntax...")
    success, stdout, stderr = run_command("python -m py_compile video_downloader_client.py")
    if success:
        print("✅ Client script syntax is valid")
        return True
    else:
        print(f"❌ Client script has syntax errors: {stderr}")
        return False

def test_basic_connectivity():
    """Test basic MCP server connectivity."""
    print("🔌 Testing MCP server connectivity...")
    
    # Create a minimal test that just tries to start the server
    test_script = '''
import subprocess
import signal
import sys
import time

def timeout_handler(signum, frame):
    raise TimeoutError("Server startup timeout")

try:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    process = subprocess.Popen(
        ["docker", "run", "-i", "--rm", "mcp-video-downloader"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    
    # Send a minimal initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    import json
    request_line = json.dumps(init_request) + "\\n"
    process.stdin.write(request_line.encode())
    process.stdin.flush()
    
    # Try to read response
    response_line = process.stdout.readline().decode().strip()
    
    if response_line:
        response = json.loads(response_line)
        if "result" in response:
            print("SUCCESS")
        else:
            print(f"ERROR: {response}")
    else:
        print("ERROR: No response")
    
    process.terminate()
    process.wait()
    
except Exception as e:
    print(f"ERROR: {e}")
finally:
    signal.alarm(0)  # Cancel the alarm
'''
    
    success, stdout, stderr = run_command(f"python -c '{test_script}'", timeout=15)
    
    if success and "SUCCESS" in stdout:
        print("✅ MCP server connectivity test passed")
        return True
    else:
        print("❌ MCP server connectivity test failed")
        if stderr:
            print(f"   Error details: {stderr}")
        if stdout and "ERROR:" in stdout:
            print(f"   Server response: {stdout}")
        return False

def main():
    """Run all tests."""
    print("🧪 MCP Video Downloader - Quick Test Suite")
    print("=" * 50)
    
    tests = [
        ("Docker Availability", test_docker_availability),
        ("Docker Image", test_docker_image),
        ("Python Dependencies", test_python_dependencies),
        ("Client Script Syntax", test_client_syntax),
        ("MCP Server Connectivity", test_basic_connectivity),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You can run the client:")
        print("   python video_downloader_client.py")
        print("   python video_downloader_client.py --interactive")
        return True
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
