#!/bin/bash

if [ -z "$ACCEPT_EULA" ]
then
    echo
    echo 'The NVIDIA Isaac Sim Additional Software and Materials License must be accepted before'
    echo 'Isaac Sim can start. The license terms for this product can be viewed at'
    echo 'https://www.nvidia.com/en-us/agreements/enterprise-software/isaac-sim-additional-software-and-materials-license/'
    echo
    echo 'Please accept the EULA above by setting the ACCEPT_EULA environment variable.'
    echo 'e.g.: -e "ACCEPT_EULA=Y"'
    echo
    exit 1
else
    echo
    echo 'The NVIDIA Isaac Sim Additional Software and Materials License must be accepted before'
    echo 'Isaac Sim can start. The license terms for this product can be viewed at'
    echo 'https://www.nvidia.com/en-us/agreements/enterprise-software/isaac-sim-additional-software-and-materials-license/'
    echo
fi
