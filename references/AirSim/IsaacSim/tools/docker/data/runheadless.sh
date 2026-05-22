#! /bin/sh

if [ "$(uname -m)" = "aarch64" ]; then
    echo 'Livestreaming is not supported on aarch64 for 5.1.0.'
    exec /bin/bash
else
    /isaac-sim/license.sh && /isaac-sim/privacy.sh && /isaac-sim/isaac-sim.streaming.sh \
      --/persistent/isaac/asset_root/default="$OMNI_SERVER" \
      --merge-config="/isaac-sim/config/open_endpoint.toml" --allow-root "$@"
fi
