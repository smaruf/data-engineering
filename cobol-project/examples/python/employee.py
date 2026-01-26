# Employee Management System

employee_name = "John Doe"
employee_id = 12345
salary = 50000.50
department = "Engineering"

print("Employee Management System")
print("==========================")

# Display employee information
print(f"Employee ID: {employee_id}")
print(f"Name: {employee_name}")
print(f"Department: {department}")
print(f"Salary: ${salary}")

# Calculate annual bonus (10%)
bonus = salary * 0.10
total_compensation = salary + bonus

print(f"Annual Bonus: ${bonus}")
print(f"Total Compensation: ${total_compensation}")

# Check salary range
if salary >= 60000:
    print("Salary Grade: Senior")
elif salary >= 40000:
    print("Salary Grade: Mid-level")
else:
    print("Salary Grade: Junior")

print("Report generated successfully")
