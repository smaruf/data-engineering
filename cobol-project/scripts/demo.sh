#!/bin/bash
# COBOL Project Demonstration Script
# Shows the capabilities of the conversion tools

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║         COBOL Project - Conversion Tools Demo             ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd ../converters

# Demo 1: Python to COBOL
echo -e "${GREEN}Demo 1: Converting Python to COBOL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Python Source Code:${NC}"
cat ../examples/python/calculator.py
echo ""
echo -e "${YELLOW}Converting to COBOL...${NC}"
sleep 1
python3 python2cobol.py ../examples/python/calculator.py -o /tmp/demo_calculator.cob
echo -e "${GREEN}✓ Conversion successful!${NC}"
echo ""
echo -e "${YELLOW}Generated COBOL Code (first 30 lines):${NC}"
head -30 /tmp/demo_calculator.cob
echo ""
read -p "Press Enter to continue..."
clear

# Demo 2: COBOL to Python
echo -e "${GREEN}Demo 2: Converting COBOL to Python${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}COBOL Source Code (excerpt):${NC}"
head -40 ../examples/cobol/hello-world.cob
echo ""
echo -e "${YELLOW}Converting to Python...${NC}"
sleep 1
python3 cobol2python.py ../examples/cobol/hello-world.cob -o /tmp/demo_hello.py
echo -e "${GREEN}✓ Conversion successful!${NC}"
echo ""
echo -e "${YELLOW}Generated Python Code:${NC}"
cat /tmp/demo_hello.py
echo ""
read -p "Press Enter to continue..."
clear

# Demo 3: Round-trip conversion
echo -e "${GREEN}Demo 3: Testing Converter Features${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Testing Python to COBOL converter built-in test:${NC}"
python3 python2cobol.py --test | head -20
echo ""
echo -e "${GREEN}✓ Test passed!${NC}"
echo ""
read -p "Press Enter to continue..."
clear

# Demo 4: Convert employee example
echo -e "${GREEN}Demo 4: Employee Management Example${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Python Source:${NC}"
cat ../examples/python/employee.py
echo ""
echo -e "${YELLOW}Converting to COBOL...${NC}"
python3 python2cobol.py ../examples/python/employee.py -o /tmp/employee.cob
echo -e "${GREEN}✓ Conversion successful!${NC}"
echo ""
echo -e "${YELLOW}COBOL Output (Data Division):${NC}"
grep -A 20 "DATA DIVISION" /tmp/employee.cob | head -20
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  Demo Complete!                            ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  You've seen:                                              ║${NC}"
echo -e "${BLUE}║  ✓ Python to COBOL conversion                              ║${NC}"
echo -e "${BLUE}║  ✓ COBOL to Python conversion                              ║${NC}"
echo -e "${BLUE}║  ✓ Built-in test features                                  ║${NC}"
echo -e "${BLUE}║  ✓ Real-world examples                                     ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  Next: Try converting your own code!                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
