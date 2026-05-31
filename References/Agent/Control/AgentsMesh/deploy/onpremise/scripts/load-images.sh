#!/bin/bash
# =============================================================================
# Load Docker Images from Tar Files
# =============================================================================
#
# Loads pre-exported Docker images for air-gapped deployment.
#
# Usage:
#   ./load-images.sh [IMAGES_DIR]
#
# Default images directory: ../images/
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGES_DIR="${1:-${SCRIPT_DIR}/../images}"

echo "=============================================="
echo "Loading Docker images from ${IMAGES_DIR}"
echo "=============================================="

if [ ! -d "${IMAGES_DIR}" ]; then
    echo "Error: Images directory not found: ${IMAGES_DIR}"
    echo "Please ensure the images directory exists with .tar files."
    exit 1
fi

# Count total images
TOTAL_IMAGES=$(ls -1 "${IMAGES_DIR}"/*.tar 2>/dev/null | wc -l)

if [ "${TOTAL_IMAGES}" -eq 0 ]; then
    echo "Error: No .tar files found in ${IMAGES_DIR}"
    exit 1
fi

echo "Found ${TOTAL_IMAGES} image files to load."
echo ""

LOADED=0
FAILED=0

for tar_file in "${IMAGES_DIR}"/*.tar; do
    filename=$(basename "${tar_file}")
    echo -n "Loading ${filename}... "

    if docker load -i "${tar_file}" > /dev/null 2>&1; then
        echo "OK"
        ((LOADED++))
    else
        echo "FAILED"
        ((FAILED++))
    fi
done

echo ""
echo "=============================================="
echo "Image loading complete!"
echo "  Loaded: ${LOADED}"
echo "  Failed: ${FAILED}"
echo "=============================================="

if [ "${FAILED}" -gt 0 ]; then
    echo "Warning: Some images failed to load."
    exit 1
fi

# List loaded images
echo ""
echo "Loaded images:"
docker images --format "  {{.Repository}}:{{.Tag}}" | grep -E "(agentsmesh|postgres|redis|minio|traefik)" | sort
