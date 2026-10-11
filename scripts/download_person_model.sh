#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
mkdir -p models
curl -L --fail --silent --show-error -o models/yolov4-tiny.weights https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights
curl -L --fail --silent --show-error -o models/yolov4-tiny.cfg https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
curl -L --fail --silent --show-error -o models/coco.names https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
echo "Downloaded YOLOv4-tiny COCO person detector. Verify hashes before offline use."
sha256sum models/yolov4-tiny.weights models/yolov4-tiny.cfg models/coco.names

