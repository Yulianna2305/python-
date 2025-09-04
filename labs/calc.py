def calculator():

  print("   Calculator")

  num1 = float(input("Enter first number: "))
  o = input("Enter operation: ")
  num2 = float(input("Enter second number: "))
 
  if o == "+":
     result = num1 + num2
  elif o == "-":
     result = num1 - num2
  elif o == "*":
     result = num1 * num2
  elif o == "/":
     result = num1 / num2
  else:
     result = "Error"

  print("Result:", result)

calculator()