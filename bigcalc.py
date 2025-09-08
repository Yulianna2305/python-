def calculator(nums):
    tokens = []                #(+, -, *, /, ())
    i = 0
    while i < len(nums):
        if nums[i].isdigit():  
            num = ''
            while i < len(nums) and nums[i].isdigit() :
                num += nums[i]
                i += 1
            tokens.append(num)
        elif nums[i] in "+-*/()":  
            tokens.append(nums[i])
            i += 1
        else:  
            i += 1

    def parse_nums(index=0):
        values, ops = [], []
        def apply_o():
            b = values.pop()
            a = values.pop()
            o = ops.pop()
            if o == '+': values.append(a + b)
            elif o == '-': values.append(a - b)
            elif o == '*': values.append(a * b)
            elif o == '/': values.append(a / b)

        while index < len(tokens):
            t = tokens[index]
            if t.isdigit() or '.' in t:  # якщо число або десяткове число
                values.append(float(t))
            elif t == '(':
                val, index = parse_nums(index + 1)
                values.append(val)
            elif t == ')':
                break
            elif t in "+-*/":
                while ops and ((t in "+-") or (t in "*/" and ops[-1] in "*/")):   # пріоритетність операцій
                    apply_o()
                ops.append(t)
            index += 1

        while ops:
            apply_o()
        return values[0], index

    result, _ = parse_nums()
    return result


while True:
    s = input("enter: ")
    try:
        print("result:", calculator(s))
    except:
        print("error!!!")