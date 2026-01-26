#!/usr/bin/env python3
"""
COBOL to Python Converter
Converts COBOL code to Python syntax
Author: Muhammad Shamsul Maruf
Date: 2026-01-26
"""

import re
import sys
import argparse
from typing import List, Dict, Tuple


class CobolToPythonConverter:
    """Converts COBOL code to Python"""
    
    def __init__(self):
        self.variables = {}
        self.in_data_division = False
        self.in_procedure_division = False
        self.current_section = None
        self.indent_level = 0
        
    def parse_pic_clause(self, pic_clause: str) -> Tuple[str, str]:
        """Parse COBOL PIC clause to Python type"""
        pic_clause = pic_clause.upper().strip()
        
        # Numeric types
        if re.match(r'9+\((\d+)\)', pic_clause) or re.match(r'9+', pic_clause):
            return 'int', '0'
        
        # Decimal types
        if 'V' in pic_clause or '.' in pic_clause:
            return 'float', '0.0'
        
        # Alphanumeric types
        if 'X' in pic_clause or 'A' in pic_clause:
            return 'str', '""'
        
        return 'str', '""'
    
    def parse_data_definition(self, line: str) -> Tuple[str, str, str]:
        """Parse COBOL data definition"""
        # Match: 01 VARIABLE-NAME PIC X(20) VALUE 'value'.
        match = re.match(r'\s*\d+\s+([A-Z0-9-]+)\s+PIC\s+([^\s]+)(?:\s+VALUE\s+(.+))?\.', line, re.IGNORECASE)
        if match:
            var_name = match.group(1).lower().replace('-', '_')
            pic_clause = match.group(2)
            value = match.group(3).strip() if match.group(3) else None
            
            py_type, default_value = self.parse_pic_clause(pic_clause)
            
            if value:
                # Remove quotes and extra spaces
                value = value.strip().strip("'").strip('"')
                if py_type == 'int':
                    value = value.replace(',', '')
                elif py_type == 'str':
                    value = f'"{value}"'
            else:
                value = default_value
            
            return var_name, py_type, value
        
        return None, None, None
    
    def convert_move_statement(self, line: str) -> str:
        """Convert COBOL MOVE to Python assignment"""
        match = re.match(r'\s*MOVE\s+(.+)\s+TO\s+([A-Z0-9-]+)', line, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            var_name = match.group(2).strip().lower().replace('-', '_')
            
            # Handle SPACES
            if value.upper() == 'SPACES':
                value = '""'
            # Handle ZERO/ZEROS/ZEROES
            elif value.upper() in ['ZERO', 'ZEROS', 'ZEROES']:
                value = '0'
            # Handle quoted strings
            elif value.startswith("'") or value.startswith('"'):
                value = value.strip("'").strip('"')
                value = f'"{value}"'
            # Handle variable references
            else:
                value = value.lower().replace('-', '_')
            
            return ' ' * (self.indent_level * 4) + f'{var_name} = {value}'
        
        return None
    
    def convert_display_statement(self, line: str) -> str:
        """Convert COBOL DISPLAY to Python print"""
        match = re.match(r'\s*DISPLAY\s+(.+?)(?:\s+WITH\s+NO\s+ADVANCING)?\.?$', line, re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            
            # Split by spaces but keep quoted strings together
            parts = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', content)
            
            python_parts = []
            for part in parts:
                if part.startswith('"') or part.startswith("'"):
                    # Quoted string
                    python_parts.append(part.strip("'").strip('"'))
                else:
                    # Variable reference
                    var = part.lower().replace('-', '_')
                    python_parts.append(f'{{{var}}}')
            
            result = ''.join(python_parts)
            
            if 'WITH NO ADVANCING' in line.upper():
                return ' ' * (self.indent_level * 4) + f'print(f"{result}", end="")'
            else:
                return ' ' * (self.indent_level * 4) + f'print(f"{result}")'
        
        return None
    
    def convert_if_statement(self, line: str) -> str:
        """Convert COBOL IF to Python if"""
        match = re.match(r'\s*IF\s+(.+)', line, re.IGNORECASE)
        if match:
            condition = match.group(1).strip()
            
            # Remove END-IF if present
            condition = re.sub(r'\s+END-IF.*$', '', condition, flags=re.IGNORECASE)
            
            # Convert COBOL operators to Python
            condition = re.sub(r'\s+NOT\s+=\s+', ' != ', condition, flags=re.IGNORECASE)
            condition = re.sub(r'\s+NOT\s+', ' not ', condition, flags=re.IGNORECASE)
            condition = re.sub(r'\s+AND\s+', ' and ', condition, flags=re.IGNORECASE)
            condition = re.sub(r'\s+OR\s+', ' or ', condition, flags=re.IGNORECASE)
            condition = condition.replace('>=', '>=').replace('<=', '<=')
            condition = condition.replace('>', '>').replace('<', '<')
            
            # Convert variable names
            words = re.findall(r'[A-Z][A-Z0-9-]*', condition)
            for word in words:
                if '-' in word:
                    condition = condition.replace(word, word.lower().replace('-', '_'))
            
            return ' ' * (self.indent_level * 4) + f'if {condition}:'
        
        return None
    
    def convert_perform_statement(self, line: str) -> str:
        """Convert COBOL PERFORM to Python loop or function call"""
        # PERFORM UNTIL
        match = re.match(r'\s*PERFORM\s+UNTIL\s+(.+)', line, re.IGNORECASE)
        if match:
            condition = match.group(1).strip()
            # Convert condition
            condition = re.sub(r'\s+NOT\s+', ' not ', condition, flags=re.IGNORECASE)
            return ' ' * (self.indent_level * 4) + f'while not ({condition}):'
        
        # PERFORM VARYING
        match = re.match(r'\s*PERFORM\s+VARYING\s+([A-Z0-9-]+)\s+FROM\s+(\d+)\s+BY\s+(\d+)\s+UNTIL\s+(.+)', line, re.IGNORECASE)
        if match:
            var = match.group(1).lower().replace('-', '_')
            start = match.group(2)
            step = match.group(3)
            condition = match.group(4)
            
            # Parse UNTIL condition to get end value
            end_match = re.search(r'>\s*(\d+)', condition)
            if end_match:
                end = str(int(end_match.group(1)) + 1)
            else:
                end = '100'  # Default
            
            return ' ' * (self.indent_level * 4) + f'for {var} in range({start}, {end}, {step}):'
        
        # Simple PERFORM (paragraph/section call)
        match = re.match(r'\s*PERFORM\s+([A-Z0-9-]+)', line, re.IGNORECASE)
        if match:
            para_name = match.group(1).lower().replace('-', '_')
            return ' ' * (self.indent_level * 4) + f'{para_name}()'
        
        return None
    
    def convert_accept_statement(self, line: str) -> str:
        """Convert COBOL ACCEPT to Python input"""
        match = re.match(r'\s*ACCEPT\s+([A-Z0-9-]+)', line, re.IGNORECASE)
        if match:
            var_name = match.group(1).lower().replace('-', '_')
            return ' ' * (self.indent_level * 4) + f'{var_name} = input()'
        
        return None
    
    def convert_compute_statement(self, line: str) -> str:
        """Convert COBOL COMPUTE to Python assignment"""
        match = re.match(r'\s*COMPUTE\s+([A-Z0-9-]+)\s*=\s*(.+)', line, re.IGNORECASE)
        if match:
            var_name = match.group(1).lower().replace('-', '_')
            expression = match.group(2).strip()
            
            # Convert variable names in expression
            words = re.findall(r'[A-Z][A-Z0-9-]*', expression)
            for word in words:
                if '-' in word:
                    expression = expression.replace(word, word.lower().replace('-', '_'))
            
            return ' ' * (self.indent_level * 4) + f'{var_name} = {expression}'
        
        return None
    
    def convert_add_statement(self, line: str) -> str:
        """Convert COBOL ADD to Python +="""
        match = re.match(r'\s*ADD\s+(.+)\s+TO\s+([A-Z0-9-]+)', line, re.IGNORECASE)
        if match:
            value = match.group(1).strip().lower().replace('-', '_')
            var_name = match.group(2).strip().lower().replace('-', '_')
            return ' ' * (self.indent_level * 4) + f'{var_name} += {value}'
        
        return None
    
    def convert_paragraph(self, line: str) -> str:
        """Convert COBOL paragraph to Python function"""
        match = re.match(r'\s*([A-Z][A-Z0-9-]+)\.\s*$', line)
        if match and self.in_procedure_division:
            para_name = match.group(1).lower().replace('-', '_')
            if para_name not in ['procedure', 'division']:
                self.indent_level = 0
                return f'\ndef {para_name}():'
        
        return None
    
    def convert(self, cobol_code: str) -> str:
        """Convert COBOL code to Python"""
        lines = cobol_code.split('\n')
        result = []
        
        # Add header
        result.append('#!/usr/bin/env python3')
        result.append('"""')
        result.append('Auto-generated Python code from COBOL')
        result.append('Converter: COBOL to Python')
        result.append('"""')
        result.append('')
        
        # Track variables to initialize
        variables_to_init = []
        
        for line in lines:
            # Skip comments and empty lines
            if not line.strip() or line.strip().startswith('*'):
                continue
            
            # Check for divisions
            if 'DATA DIVISION' in line.upper():
                self.in_data_division = True
                self.in_procedure_division = False
                result.append('# Data Division - Variable Declarations')
                continue
            
            if 'PROCEDURE DIVISION' in line.upper():
                self.in_data_division = False
                self.in_procedure_division = True
                result.append('\n# Procedure Division')
                result.append('\ndef main():')
                self.indent_level = 1
                continue
            
            # Parse data definitions
            if self.in_data_division:
                var_name, py_type, value = self.parse_data_definition(line)
                if var_name:
                    variables_to_init.append((var_name, value))
                continue
            
            # Convert procedure division statements
            if self.in_procedure_division:
                converted = None
                
                # Try each conversion
                if 'MOVE' in line.upper():
                    converted = self.convert_move_statement(line)
                elif 'DISPLAY' in line.upper():
                    converted = self.convert_display_statement(line)
                elif line.strip().upper().startswith('IF '):
                    converted = self.convert_if_statement(line)
                    if converted:
                        self.indent_level += 1
                elif 'ELSE' in line.upper():
                    self.indent_level -= 1
                    converted = ' ' * (self.indent_level * 4) + 'else:'
                    self.indent_level += 1
                elif 'END-IF' in line.upper():
                    self.indent_level = max(1, self.indent_level - 1)
                    continue
                elif 'PERFORM' in line.upper():
                    converted = self.convert_perform_statement(line)
                    if converted and converted.strip().endswith(':'):
                        self.indent_level += 1
                elif 'ACCEPT' in line.upper():
                    converted = self.convert_accept_statement(line)
                elif 'COMPUTE' in line.upper():
                    converted = self.convert_compute_statement(line)
                elif 'ADD' in line.upper() and 'TO' in line.upper():
                    converted = self.convert_add_statement(line)
                elif 'STOP RUN' in line.upper():
                    converted = None  # Will be handled at the end
                    continue
                elif re.match(r'\s*([A-Z][A-Z0-9-]+)\.\s*$', line):
                    converted = self.convert_paragraph(line)
                    if converted:
                        self.indent_level = 1
                
                if converted:
                    result.append(converted)
        
        # Add variable initializations at the beginning of main
        if variables_to_init:
            # Insert after "def main():"
            main_index = -1
            for i, line in enumerate(result):
                if 'def main():' in line:
                    main_index = i
                    break
            
            if main_index >= 0:
                for var_name, value in variables_to_init:
                    result.insert(main_index + 1, f'    {var_name} = {value}')
        
        # Add main execution
        result.append('\n\nif __name__ == "__main__":')
        result.append('    main()')
        
        return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(description='Convert COBOL code to Python')
    parser.add_argument('input_file', nargs='?', help='Input COBOL file')
    parser.add_argument('-o', '--output', help='Output Python file')
    parser.add_argument('--test', action='store_true', help='Run test conversion')
    
    args = parser.parse_args()
    
    if args.test:
        # Test with sample COBOL code
        sample_cobol = '''
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SAMPLE.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  EMPLOYEE-NAME    PIC X(30) VALUE "JOHN DOE".
       01  EMPLOYEE-AGE     PIC 9(2) VALUE 30.
       01  COUNTER          PIC 9(3) VALUE 0.
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY "Employee: " EMPLOYEE-NAME.
           DISPLAY "Age: " EMPLOYEE-AGE.
           
           IF EMPLOYEE-AGE >= 18
               DISPLAY "Adult"
           ELSE
               DISPLAY "Minor"
           END-IF.
           
           PERFORM VARYING COUNTER FROM 1 BY 1 UNTIL COUNTER > 5
               DISPLAY "Count: " COUNTER
           END-PERFORM.
           
           STOP RUN.
'''
        converter = CobolToPythonConverter()
        python_code = converter.convert(sample_cobol)
        print(python_code)
        return
    
    if not args.input_file:
        parser.print_help()
        return
    
    # Read input file
    try:
        with open(args.input_file, 'r') as f:
            cobol_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found")
        sys.exit(1)
    
    # Convert
    converter = CobolToPythonConverter()
    python_code = converter.convert(cobol_code)
    
    # Output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(python_code)
            print(f"Conversion successful! Output written to {args.output}")
        except IOError as e:
            print(f"Error: Cannot write to file '{args.output}': {e}")
            sys.exit(1)
    else:
        print(python_code)


if __name__ == '__main__':
    main()
