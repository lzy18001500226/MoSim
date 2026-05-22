#!/bin/bash
PRIVACY_EMAIL="${PRIVACY_EMAIL:-user@example.com}"  # Allow override via environment

docker run --name isaac-sim --entrypoint bash -it --gpus all -e "ACCEPT_EULA=Y" --rm \
 --network=host -e "PRIVACY_CONSENT=Y" -e "PRIVACY_USERID=${PRIVACY_EMAIL}" isaac-sim-docker:latest \
 "$@"
