#!/bin/sh
# Fetch the pinned FreeRTOS kernel and check the toolchain.   sh labs/fetch-deps.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
TAG=V11.3.2
COMMIT=640d0c43705e64cd53f46b31d882de6cd8433933
mkdir -p "$HERE/third_party"
if [ ! -d "$HERE/third_party/FreeRTOS-Kernel" ]; then
  git clone --depth 1 --branch "$TAG" https://github.com/FreeRTOS/FreeRTOS-Kernel.git "$HERE/third_party/FreeRTOS-Kernel"
fi
GOT="$(git -C "$HERE/third_party/FreeRTOS-Kernel" rev-parse HEAD)"
[ "$GOT" = "$COMMIT" ] && echo "FreeRTOS-Kernel $TAG ($COMMIT) OK" || echo "WARNING: FreeRTOS-Kernel is at $GOT, labs were run against $COMMIT"
for t in arm-none-eabi-gcc arm-none-eabi-gdb qemu-system-arm python3 cc; do
  command -v "$t" >/dev/null 2>&1 && echo "found  $t" || echo "MISSING $t   (macOS: brew install arm-none-eabi-gcc arm-none-eabi-gdb qemu)"
done
