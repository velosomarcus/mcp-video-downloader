#!/bin/bash

# MCP Video Downloader Wrapper Script
# This script automatically handles volume mounting for downloads
# so that downloaded files persist on the host machine regardless
# of which MCP client is used (Claude, our Python client, etc.)

set -e

# Configuration
CONTAINER_NAME="mcp-video-downloader"
DOWNLOADS_DIR="${HOME}/Downloads/mcp-videos"
CONTAINER_DOWNLOADS_DIR="/downloads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[MCP-VideoDownloader]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[MCP-VideoDownloader]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[MCP-VideoDownloader]${NC} $1"
}

print_error() {
    echo -e "${RED}[MCP-VideoDownloader]${NC} $1"
}

# Create downloads directory if it doesn't exist
if [ ! -d "$DOWNLOADS_DIR" ]; then
    print_status "Creating downloads directory: $DOWNLOADS_DIR"
    mkdir -p "$DOWNLOADS_DIR"
    print_success "Downloads directory created"
else
    print_status "Using existing downloads directory: $DOWNLOADS_DIR"
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if the Docker image exists
if ! docker image inspect $CONTAINER_NAME >/dev/null 2>&1; then
    print_error "Docker image '$CONTAINER_NAME' not found."
    print_status "Please build the image first with: docker build -t $CONTAINER_NAME ."
    exit 1
fi

print_status "Starting MCP Video Downloader with volume mount..."
print_status "Downloads will be saved to: $DOWNLOADS_DIR"

# Run the Docker container with volume mount
# The container will automatically use the /downloads directory for output
exec docker run -i --rm \
    -v "$DOWNLOADS_DIR:$CONTAINER_DOWNLOADS_DIR" \
    "$CONTAINER_NAME" "$@"
