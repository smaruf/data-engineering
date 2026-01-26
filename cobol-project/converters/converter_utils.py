"""
Converter Utilities
Common utilities for Python-COBOL conversion
Author: Muhammad Shamsul Maruf
"""

def normalize_identifier(name: str, to_cobol: bool = True) -> str:
    """
    Normalize identifiers between Python and COBOL naming conventions
    
    Args:
        name: Identifier name
        to_cobol: If True, convert to COBOL style (UPPER-CASE)
                 If False, convert to Python style (lower_case)
    
    Returns:
        Normalized identifier
    """
    if to_cobol:
        return name.upper().replace('_', '-')
    else:
        return name.lower().replace('-', '_')


def infer_python_type(cobol_pic: str) -> str:
    """
    Infer Python type from COBOL PIC clause
    
    Args:
        cobol_pic: COBOL PIC clause (e.g., "9(5)", "X(20)", "9(3)V99")
    
    Returns:
        Python type as string
    """
    pic = cobol_pic.upper().strip()
    
    if 'V' in pic or '.' in pic:
        return 'float'
    elif '9' in pic:
        return 'int'
    elif 'X' in pic or 'A' in pic:
        return 'str'
    else:
        return 'str'


def infer_cobol_pic(python_type: str, value=None) -> str:
    """
    Infer COBOL PIC clause from Python type and value
    
    Args:
        python_type: Python type as string
        value: Optional value to help determine size
    
    Returns:
        COBOL PIC clause
    """
    if python_type == 'int':
        if value:
            length = len(str(abs(int(value))))
            return f"PIC S9({length})"
        return "PIC 9(10)"
    elif python_type == 'float':
        if value:
            str_val = str(abs(float(value)))
            if '.' in str_val:
                parts = str_val.split('.')
                return f"PIC S9({len(parts[0])})V9({min(len(parts[1]), 2)})"
        return "PIC S9(8)V99"
    elif python_type == 'str':
        if value:
            return f"PIC X({max(len(str(value)), 20)})"
        return "PIC X(50)"
    else:
        return "PIC X(50)"


def format_cobol_comment(text: str, width: int = 65) -> list:
    """
    Format text as COBOL comments
    
    Args:
        text: Comment text
        width: Maximum width of comment (default 65)
    
    Returns:
        List of formatted comment lines
    """
    lines = []
    lines.append("      *" + "*" * width + "*")
    
    words = text.split()
    current_line = "      * "
    
    for word in words:
        if len(current_line) + len(word) + 1 <= width + 8:
            current_line += word + " "
        else:
            # Pad the line to full width
            padding = " " * (width + 8 - len(current_line))
            lines.append(current_line + padding + "*")
            current_line = "      * " + word + " "
    
    if current_line.strip() != "      *":
        padding = " " * (width + 8 - len(current_line))
        lines.append(current_line + padding + "*")
    
    lines.append("      *" + "*" * width + "*")
    return lines


def validate_cobol_identifier(name: str) -> bool:
    """
    Validate COBOL identifier name
    
    Args:
        name: Identifier to validate
    
    Returns:
        True if valid, False otherwise
    """
    # COBOL identifiers: 1-30 chars, alphanumeric + hyphen, can't start/end with hyphen
    if not name or len(name) > 30:
        return False
    
    if name[0] == '-' or name[-1] == '-':
        return False
    
    for char in name:
        if not (char.isalnum() or char == '-'):
            return False
    
    return True


def validate_python_identifier(name: str) -> bool:
    """
    Validate Python identifier name
    
    Args:
        name: Identifier to validate
    
    Returns:
        True if valid, False otherwise
    """
    import keyword
    
    if not name or keyword.iskeyword(name):
        return False
    
    if not (name[0].isalpha() or name[0] == '_'):
        return False
    
    for char in name:
        if not (char.isalnum() or char == '_'):
            return False
    
    return True


# Data type mapping tables
PYTHON_TO_COBOL_TYPES = {
    'int': 'PIC 9(10)',
    'float': 'PIC 9(8)V99',
    'str': 'PIC X(50)',
    'bool': 'PIC 9 VALUE 0',
    'list': 'OCCURS clause',
}

COBOL_TO_PYTHON_TYPES = {
    '9': 'int',
    'X': 'str',
    'A': 'str',
    'V': 'float',
    'S': 'int',  # Signed
}


# Operator mapping
PYTHON_TO_COBOL_OPERATORS = {
    '==': '=',
    '!=': 'NOT =',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'True': '1',
    'False': '0',
}

COBOL_TO_PYTHON_OPERATORS = {
    'NOT =': '!=',
    'AND': 'and',
    'OR': 'or',
    'NOT': 'not',
}
