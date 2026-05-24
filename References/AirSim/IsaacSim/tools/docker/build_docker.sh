#! /bin/sh

# Default tag
TAG="isaac-sim-docker:latest"
CONTAINER_PLATFORM=linux/amd64
PUSH_TAG=""

# Parse command line arguments
while [ $# -gt 0 ]; do
    case $1 in
        --tag)
            TAG="$2"
            shift 2
            ;;
        --x86_64)
            CONTAINER_PLATFORM=linux/amd64
            shift
            ;;
        --aarch64)
            CONTAINER_PLATFORM=linux/arm64
            shift
            ;;
        --push)
            PUSH_TAG="--push"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--tag TAG]"
            echo "  --tag TAG    Docker image tag (default: isaac-sim-docker:latest)"
            echo "  --x86_64     Platform tag (default: x86_64)"
            echo "  --aarch64    Platform tag (default: x86_64)"
            echo "  --push       Push docker image tag"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if docker buildx inspect | grep -q $CONTAINER_PLATFORM; then
    echo "This builder supports $CONTAINER_PLATFORM builds"
else
    echo "ERROR: This host's buildx builder does NOT support $CONTAINER_PLATFORM"
    exit 1
fi

docker buildx build \
  -t "$TAG" \
  --platform=$CONTAINER_PLATFORM \
  -f tools/docker/Dockerfile \
  $PUSH_TAG _container_temp
