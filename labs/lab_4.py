def shadow(limit=200):   
    def decorator(gen_func):
        def wrapper(*args, **kwargs):  
            total = 0
            gen = gen_func(*args, **kwargs) 

            while True:
                try:                 
                    item = next(gen)  
                except StopIteration: 
                    return total      
                
                print(item)

                parts = item.split()
                if len(parts) != 2:
                    print(f"   некоректний рядок: '{item}'") 
                    yield item 
                    continue

                t_type, amount_raw = parts

                if amount_raw.lstrip('-').isdigit():  
                    amount = int(amount_raw)
                else:
                    print(f"   некоректна сума: '{item}' ")
                    yield item
                    continue

                if t_type == "refund":                   
                    total -= amount
                elif t_type in ("payment", "transfer"):
                    total += amount
                else:
                    print(f"   невідомий тип транзакції: '{t_type}'")
                    yield item
                    continue

                if total > limit:                 

                    print("тіньовий ліміт перевищено")

                yield item

        return wrapper
    return decorator


def base_transaction_generator():
    items = [
        "payment 120",
        "refund 50",
        "transfer 90",  
        "payment 70",
        "line",
        "payment fifty",
        "shadow 999",    
    ]
    for it in items:
        yield it
   
@shadow(limit=200)
def transaction_stream():
    yield from base_transaction_generator()

if __name__ == "__main__":
    g = transaction_stream()

    try:
        while True:
            next(g)  
    except StopIteration as exc:
        final_total = exc.value
        print("\n Фінальна сума:", final_total)




