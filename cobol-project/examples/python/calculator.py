# Simple Calculator Program

num1 = 10
num2 = 5
result = 0

print("Simple Calculator")
print("=================")

# Addition
result = num1 + num2
print(f"Addition: {num1} + {num2} = {result}")

# Subtraction  
result = num1 - num2
print(f"Subtraction: {num1} - {num2} = {result}")

# Multiplication
result = num1 * num2
print(f"Multiplication: {num1} * {num2} = {result}")

# Division
if num2 != 0:
    result = num1 / num2
    print(f"Division: {num1} / {num2} = {result}")
else:
    print("Cannot divide by zero")

print("Calculator finished")
