#!/usr/bin/env python3
"""
Python to COBOL Converter
Converts Python code to COBOL syntax
Author: Muhammad Shamsul Maruf
Date: 2026-01-26
"""

import re
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Tuple


class PythonToCobolConverter:
    """Converts Python code to COBOL"""
    
    def __init__(self):
        self.variables = {}
        self.functions = []
        self.indentation_level = 0
        self.current_paragraph = "MAIN-PROCEDURE"
        
    def infer_cobol_type(self, value: str) -> str:
        """Infer COBOL data type from Python value"""
        value = value.strip().strip('"').strip("'")
        
        # Check if it's a number
        if value.replace('.', '', 1).replace('-', '', 1).isdigit():
            if '.' in value:
                parts = value.split('.')
                return f"PIC 9({len(parts[0])})V9({len(parts[1])})"
            else:
                return f"PIC 9({max(len(value), 1)})"
        
        # Default to string
        return f"PIC X({max(len(value), 20)})"
    
    def parse_variable(self, line: str) -> Tuple[str, str, str]:
        """Parse Python variable assignment"""
        match = re.match(r'\s*(\w+)\s*=\s*(.+)', line)
        if match:
            var_name = match.group(1).upper().replace('_', '-')
            value = match.group(2).strip()
            
            # Remove quotes if string
            if value.startswith('"') or value.startswith("'"):
                value_clean = value.strip('"').strip("'")
                pic_clause = f"PIC X({max(len(value_clean), 20)})"
                return var_name, pic_clause, value_clean
            # Check if numeric
            elif value.replace('.', '', 1).replace('-', '', 1).isdigit():
                if '.' in value:
                    parts = value.split('.')
                    pic_clause = f"PIC 9({len(parts[0])})V9({len(parts[1])})"
                else:
                    pic_clause = f"PIC 9({max(len(value), 1)})"
                return var_name, pic_clause, value
            else:
                # Variable reference or expression
                pic_clause = "PIC X(50)"
                return var_name, pic_clause, ""
        
        return None, None, None
    
    def convert_if_statement(self, line: str, indent: int) -> List[str]:
        """Convert Python if statement to COBOL"""
        result = []
        
        # Extract condition
        match = re.match(r'\s*if\s+(.+):', line)
        if match:
            condition = match.group(1).strip()
            # Convert Python operators to COBOL
            condition = condition.replace('==', '=')
            condition = condition.replace('!=', 'NOT =')
            condition = condition.replace('and', 'AND')
            condition = condition.replace('or', 'OR')
            condition = condition.replace('not ', 'NOT ')
            
            # Convert variable names
            for word in condition.split():
                if word.replace('_', '').isalnum():
                    condition = condition.replace(word, word.upper().replace('_', '-'))
            
            result.append(' ' * (11 + indent * 4) + f"IF {condition}")
        
        return result
    
    def convert_while_loop(self, line: str, indent: int) -> List[str]:
        """Convert Python while loop to COBOL PERFORM"""
        result = []
        
        match = re.match(r'\s*while\s+(.+):', line)
        if match:
            condition = match.group(1).strip()
            condition = condition.replace('==', '=')
            condition = condition.replace('!=', 'NOT =')
            
            result.append(' ' * (11 + indent * 4) + f"PERFORM UNTIL NOT ({condition})")
        
        return result
    
    def convert_for_loop(self, line: str, indent: int) -> List[str]:
        """Convert Python for loop to COBOL PERFORM VARYING"""
        result = []
        
        match = re.match(r'\s*for\s+(\w+)\s+in\s+range\((\d+)(?:,\s*(\d+))?\):', line)
        if match:
            var = match.group(1).upper().replace('_', '-')
            start = match.group(2) if match.group(3) else "1"
            end = match.group(3) if match.group(3) else match.group(2)
            
            result.append(' ' * (11 + indent * 4) + 
                         f"PERFORM VARYING {var} FROM {start} BY 1 UNTIL {var} > {end}")
        
        return result
    
    def convert_function(self, line: str) -> Tuple[str, List[str]]:
        """Convert Python function to COBOL paragraph"""
        match = re.match(r'\s*def\s+(\w+)\s*\(([^)]*)\):', line)
        if match:
            func_name = match.group(1).upper().replace('_', '-')
            params = match.group(2)
            
            result = []
            result.append(f"       {func_name}.")
            
            return func_name, result
        
        return None, []
    
    def convert_print(self, line: str, indent: int) -> List[str]:
        """Convert Python print to COBOL DISPLAY"""
        result = []
        
        match = re.match(r'\s*print\s*\((.+)\)', line)
        if match:
            content = match.group(1).strip()
            
            # Handle f-strings
            if content.startswith('f"') or content.startswith("f'"):
                content = content[2:-1]
                # Simple conversion - replace {var} with variable names
                content = re.sub(r'\{(\w+)\}', r'" \1 "', content)
                result.append(' ' * (11 + indent * 4) + f'DISPLAY "{content}"')
            else:
                # Remove quotes if present
                content = content.strip('"').strip("'")
                result.append(' ' * (11 + indent * 4) + f'DISPLAY "{content}"')
        
        return result
    
    def convert_line(self, line: str, indent: int) -> List[str]:
        """Convert a single Python line to COBOL"""
        result = []
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            return result
        
        # Check for function definition
        if line.strip().startswith('def '):
            func_name, func_lines = self.convert_function(line)
            if func_name:
                self.functions.append(func_name)
                return func_lines
        
        # Check for variable assignment
        if '=' in line and not any(op in line for op in ['==', '!=', '>=', '<=']):
            var_name, pic_clause, value = self.parse_variable(line)
            if var_name:
                self.variables[var_name] = (pic_clause, value)
                result.append(' ' * (11 + indent * 4) + f"MOVE {value or 'SPACES'} TO {var_name}")
                return result
        
        # Check for control structures
        if line.strip().startswith('if '):
            return self.convert_if_statement(line, indent)
        
        if line.strip().startswith('elif '):
            line = line.replace('elif ', 'if ')
            return [' ' * (11 + indent * 4) + "ELSE"] + self.convert_if_statement(line, indent)
        
        if line.strip().startswith('else:'):
            return [' ' * (11 + indent * 4) + "ELSE"]
        
        if line.strip().startswith('while '):
            return self.convert_while_loop(line, indent)
        
        if line.strip().startswith('for '):
            return self.convert_for_loop(line, indent)
        
        if line.strip().startswith('print('):
            return self.convert_print(line, indent)
        
        # Return statement
        if line.strip().startswith('return'):
            result.append(' ' * (11 + indent * 4) + "EXIT PARAGRAPH")
            return result
        
        return result
    
    def generate_data_division(self) -> List[str]:
        """Generate COBOL DATA DIVISION from collected variables"""
        result = []
        result.append("       DATA DIVISION.")
        result.append("       WORKING-STORAGE SECTION.")
        
        for var_name, (pic_clause, value) in self.variables.items():
            if value:
                if value.replace('.', '', 1).replace('-', '', 1).isdigit():
                    result.append(f"       01  {var_name:<20} {pic_clause} VALUE {value}.")
                else:
                    result.append(f"       01  {var_name:<20} {pic_clause} VALUE '{value}'.")
            else:
                result.append(f"       01  {var_name:<20} {pic_clause}.")
        
        result.append("")
        return result
    
    def convert(self, python_code: str) -> str:
        """Convert Python code to COBOL"""
        lines = python_code.split('\n')
        
        # First pass: collect variables and functions
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                var_name, pic_clause, value = self.parse_variable(line)
                if var_name and var_name not in self.variables:
                    self.variables[var_name] = (pic_clause, value)
        
        # Generate COBOL program
        result = []
        
        # IDENTIFICATION DIVISION
        result.append("       IDENTIFICATION DIVISION.")
        result.append("       PROGRAM-ID. CONVERTED-PROGRAM.")
        result.append("       AUTHOR. PYTHON-TO-COBOL-CONVERTER.")
        result.append(f"       DATE-WRITTEN. {datetime.now().strftime('%Y-%m-%d')}.")
        result.append("      *****************************************************************")
        result.append("      * AUTO-GENERATED FROM PYTHON CODE                              *")
        result.append("      *****************************************************************")
        result.append("")
        
        # ENVIRONMENT DIVISION (if needed)
        result.append("       ENVIRONMENT DIVISION.")
        result.append("")
        
        # DATA DIVISION
        result.extend(self.generate_data_division())
        
        # PROCEDURE DIVISION
        result.append("       PROCEDURE DIVISION.")
        result.append("       MAIN-PROCEDURE.")
        
        # Second pass: convert procedure logic
        indent = 0
        for line in lines:
            # Calculate indentation
            stripped = line.lstrip()
            if stripped:
                current_indent = (len(line) - len(stripped)) // 4
                converted = self.convert_line(line, current_indent)
                result.extend(converted)
        
        result.append("           STOP RUN.")
        result.append("")
        result.append("       END PROGRAM CONVERTED-PROGRAM.")
        
        return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(description='Convert Python code to COBOL')
    parser.add_argument('input_file', nargs='?', help='Input Python file')
    parser.add_argument('-o', '--output', help='Output COBOL file')
    parser.add_argument('--test', action='store_true', help='Run test conversion')
    
    args = parser.parse_args()
    
    if args.test:
        # Test with sample code
        sample_python = '''
# Sample Python program
name = "John Doe"
age = 30
salary = 50000.50

print("Employee Information")
print(f"Name: {name}")
print(f"Age: {age}")

if age >= 18:
    print("Adult")
else:
    print("Minor")

for i in range(1, 5):
    print(f"Count: {i}")
'''
        converter = PythonToCobolConverter()
        cobol_code = converter.convert(sample_python)
        print(cobol_code)
        return
    
    if not args.input_file:
        parser.print_help()
        return
    
    # Read input file
    try:
        with open(args.input_file, 'r') as f:
            python_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found")
        sys.exit(1)
    
    # Convert
    converter = PythonToCobolConverter()
    cobol_code = converter.convert(python_code)
    
    # Output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(cobol_code)
            print(f"Conversion successful! Output written to {args.output}")
        except IOError as e:
            print(f"Error: Cannot write to file '{args.output}': {e}")
            sys.exit(1)
    else:
        print(cobol_code)


if __name__ == '__main__':
    main()
