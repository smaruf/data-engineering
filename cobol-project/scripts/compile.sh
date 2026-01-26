#!/bin/bash
# Compile COBOL programs
# Author: Muhammad Shamsul Maruf

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "  COBOL Program Compilation Script"
echo "========================================"
echo ""

# Check if GnuCOBOL is installed
if ! command -v cobc &> /dev/null; then
    echo -e "${RED}ERROR: GnuCOBOL (cobc) is not installed${NC}"
    echo "Please install it with: sudo apt-get install gnucobol"
    exit 1
fi

echo -e "${GREEN}GnuCOBOL version:${NC}"
cobc --version | head -1
echo ""

# Create bin directory if it doesn't exist
BIN_DIR="../bin"
SRC_DIR="../src"

mkdir -p "$BIN_DIR"

# Compile all COBOL programs
echo "Compiling COBOL programs..."
echo "----------------------------"

compiled=0
failed=0

for cob_file in "$SRC_DIR"/*.cob; do
    if [ -f "$cob_file" ]; then
        filename=$(basename "$cob_file" .cob)
        echo -n "Compiling $filename.cob... "
        
        if cobc -x "$cob_file" -o "$BIN_DIR/$filename" 2>/dev/null; then
            echo -e "${GREEN}OK${NC}"
            ((compiled++))
        else
            echo -e "${RED}FAILED${NC}"
            ((failed++))
            # Show error details
            echo -e "${YELLOW}Error details:${NC}"
            cobc -x "$cob_file" -o "$BIN_DIR/$filename" 2>&1 | head -5
        fi
    fi
done

echo ""
echo "========================================"
echo "Compilation Summary:"
echo "  Compiled: $compiled"
echo "  Failed:   $failed"
echo "========================================"

if [ $compiled -gt 0 ]; then
    echo ""
    echo -e "${GREEN}Executables are in: $BIN_DIR${NC}"
    echo "Run them with: $BIN_DIR/<program-name>"
fi

exit 0
