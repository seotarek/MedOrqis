#!/usr/bin/env bash
# ==============================================================================
# MedOrqis-QNX: Release & Hackathon Packaging Script
# Creates verified submission package with SHA-256 checksums
# QNX Global Hackathon 2026
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QNX_EDGE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$QNX_EDGE_DIR/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"

mkdir -p "$DIST_DIR"

echo "================================================================================"
echo " MEDORQIS-QNX :: PACKAGING OFFICIAL HACKATHON SUBMISSION"
echo "================================================================================"

# 1. Run all tests first
echo "[1/3] Running complete automated verification suite..."
"$QNX_EDGE_DIR/scripts/run_tests.sh"

# 2. Package qnx_edge clean source archive
echo ""
echo "[2/3] Creating distribution tarball..."
PACKAGE_NAME="medorqis_qnx_hackathon_2026"
TAR_FILE="$DIST_DIR/${PACKAGE_NAME}.tar.gz"

cd "$ROOT_DIR"
tar --exclude='qnx_edge/bin' \
    --exclude='qnx_edge/build' \
    --exclude='qnx_edge/__pycache__' \
    --exclude='qnx_edge/*/__pycache__' \
    --exclude='qnx_edge/*.o' \
    --exclude='qnx_edge/reports/*.jsonl' \
    -czvf "$TAR_FILE" qnx_edge/

# 3. Generate SHA-256 Checksum
echo ""
echo "[3/3] Generating cryptographic checksum..."
cd "$DIST_DIR"
sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.sha256"

echo ""
echo "================================================================================"
echo " [SUCCESS] PACKAGING COMPLETE"
echo " Archive:  $TAR_FILE"
echo " Checksum: $(cat "${DIST_DIR}/${PACKAGE_NAME}.sha256")"
echo "================================================================================"
