#!/usr/bin/env bash
find . -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -prune -exec rm -rf '{}' +