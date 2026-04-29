#!/bin/bash
# Launch Stacker in dev mode, pointing Swift at the local Python engine.
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
export STACKER_ENGINE_DIR="$REPO_ROOT/engine"
export STACKER_PYTHON="$(command -v python3)"
open "$REPO_ROOT/Stacker/build/Debug/Stacker.app"
