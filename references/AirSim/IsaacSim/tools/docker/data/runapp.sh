#! /bin/sh

/isaac-sim/license.sh && /isaac-sim/privacy.sh && /isaac-sim/isaac-sim.sh \
  --/persistent/isaac/asset_root/default="$OMNI_SERVER" \
  --merge-config="/isaac-sim/config/open_endpoint.toml" --allow-root "$@"
