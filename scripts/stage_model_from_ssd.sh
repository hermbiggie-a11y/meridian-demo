#!/bin/bash
# Copy Qwen3.6-35B-A3B-NVFP4 from a local folder (for example an SSD) into the HF cache layout
# NemoClaw's managed vLLM expects, under the revision NemoClaw pins (LFS weights are identical to the 1355db6 snapshot).
# Usage: scripts/stage_model_from_ssd.sh <folder holding the Qwen3.6-35B-A3B-NVFP4 weights>
set -euo pipefail
SRC="${1:?usage: scripts/stage_model_from_ssd.sh <folder holding the Qwen3.6-35B-A3B-NVFP4 weights>}"
R=491c2f1ea524c639598bf8fa787a93fed5a6fbce
M=~/.cache/huggingface/hub/models--nvidia--Qwen3.6-35B-A3B-NVFP4
mkdir -p "$M/snapshots/$R" "$M/refs"
echo -n "$R" > "$M/refs/main"
rsync -a --info=progress2 --exclude .cache "$SRC/" "$M/snapshots/$R/"
