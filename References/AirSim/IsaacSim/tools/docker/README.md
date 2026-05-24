# Docker Build Tools

This directory contains scripts for building Docker images of Isaac Sim. The build process involves two main steps: preparing the build environment and building the Docker image.

## Prerequisites

Before running these scripts, ensure you have the following installed on your host machine:

- **rsync** - Required for file synchronization during the preparation phase
- **python3** - Required for running the preparation scripts and installing dependencies
- **Docker** - Required for building the final image

### Installing Prerequisites

On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y rsync python3 docker.io
```

On other systems, install these packages using your system's package manager.

## Build Process

### Step 1: Prepare the Build Environment

Use `prep_docker_build.sh` to prepare the Docker build context:

```bash
./tools/docker/prep_docker_build.sh [OPTIONS]
```

#### Options:
- `--build` - Run the full Isaac Sim build sequence before preparing Docker files:
  - Executes `build.sh -r`
- `--x86_64` - Build x86_64 container (default)
- `--aarch64` - Build aarch64 container
- `--skip-dedupe` - Skip the file deduplication process (faster but larger image)
- `--help, -h` - Show help message

#### What this script does:
1. **Build Verification**: Checks that `_build/$CONTAINER_PLATFORM/release` exists (required for Docker build)
2. **Dependency Installation**: Installs Python requirements from `tools/docker/requirements.txt`
3. **File Preparation**: Generates and runs an rsync script to copy necessary files to `_container_temp`
4. **Data Copying**: Copies additional data from `tools/docker/data` and `tools/docker/oss`
5. **Deduplication**: Finds duplicate files and replaces them with symlinks to reduce image size
6. **Symlink Cleanup**: Fixes any chained symlinks that may have been created

### Step 2: Build the Docker Image

Use `build_docker.sh` to build the actual Docker image:

```bash
./tools/docker/build_docker.sh [OPTIONS]
```

#### Options:
- `--tag TAG` - Specify the Docker image tag (default: `isaac-sim-docker:latest`)
- `--x86_64` - Specify the Platform tag (default: x86_64)
- `--aarch64` - Specify the Platform tag (default: x86_64)
- `--push` - Push docker image tag
- `-h, --help` - Show help message

## Example Usage

### Basic build:
```bash
# Prepare build environment (includes full build)
./tools/docker/prep_docker_build.sh --build

# Build Docker image with default tag
./tools/docker/build_docker.sh
```

### Custom tag:
```bash
# Prepare build environment
./tools/docker/prep_docker_build.sh --build

# Build with custom tag
./tools/docker/build_docker.sh --tag my-isaac-sim:v1.0
```

### Quick rebuild (skip deduplication):
```bash
# If you've already built once and want to rebuild quickly
./tools/docker/prep_docker_build.sh --skip-dedupe

# Build the image
./tools/docker/build_docker.sh
```

## Important Notes

- **Build Requirements**: The `_build/$CONTAINER_PLATFORM/release` directory must exist before running the Docker preparation. Use `--build` option if you haven't built Isaac Sim yet.
- **Deduplication**: The deduplication process can significantly reduce Docker image size by replacing duplicate files with symlinks, but it takes time. Use `--skip-dedupe` for faster rebuilds during development.
- **File Paths**: The deduplication process skips files with spaces in their paths for reliability.
- **Build Context**: The final Docker build uses `_container_temp` as the build context and `tools/docker/Dockerfile` as the Dockerfile.
- **Platform**: Add the `--aarch64` flag to build for arm64 platform. It is recommended to use this flag when on an arm64 host.

## Troubleshooting

- **Error: "_build/$CONTAINER_PLATFORM/release does not exist"**: Run the script with `--build` option to build Isaac Sim first.
- **rsync not found**: Install rsync using your system's package manager.
- **Python requirements installation fails**: Ensure python3 and pip are properly installed.
- **Docker build fails**: Check that Docker daemon is running and you have sufficient disk space.
