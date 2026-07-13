#!/bin/bash
cd "$(dirname "$0")/abia-app"
pytest "$@"
