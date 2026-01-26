#!/bin/bash
# Test COBOL programs and converters
# Author: Muhammad Shamsul Maruf

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  COBOL Project Test Suite"
echo "========================================"
echo ""

# Test converters
echo "Testing Python to COBOL Converter..."
echo "--------------------------------------"
cd ../converters
python3 python2cobol.py --test > /tmp/test_output.cob 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python to COBOL converter test passed${NC}"
else
    echo -e "${RED}✗ Python to COBOL converter test failed${NC}"
fi
echo ""

echo "Testing COBOL to Python Converter..."
echo "--------------------------------------"
python3 cobol2python.py --test > /tmp/test_output.py 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ COBOL to Python converter test passed${NC}"
else
    echo -e "${RED}✗ COBOL to Python converter test failed${NC}"
fi
echo ""

# Test example conversions
echo "Testing Example Conversions..."
echo "--------------------------------------"

# Python to COBOL
if [ -f ../examples/python/calculator.py ]; then
    python3 python2cobol.py ../examples/python/calculator.py -o /tmp/calculator.cob
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Calculator.py converted to COBOL${NC}"
    else
        echo -e "${RED}✗ Calculator.py conversion failed${NC}"
    fi
fi

# COBOL to Python
if [ -f ../src/data-validation.cob ]; then
    python3 cobol2python.py ../src/data-validation.cob -o /tmp/data_validation.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ data-validation.cob converted to Python${NC}"
    else
        echo -e "${RED}✗ data-validation.cob conversion failed${NC}"
    fi
fi

echo ""
echo "========================================"
echo "Test Suite Complete!"
echo "========================================"
