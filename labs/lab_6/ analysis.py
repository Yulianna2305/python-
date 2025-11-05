import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_name = "supplies.csv"
df = pd.read_csv(file_name)

avg_price = np.mean(df["price_per_unit"])
median_quantity = np.median(df["quantity"])
std_price = np.std(df["price_per_unit"])

df["total_price"] = df["quantity"] * df["price_per_unit"]  
top_supplier = df.groupby("supplier")["total_price"].sum().idxmax()
category_sum = df.groupby("category")["quantity"].sum()

df[df["quantity"] < 100].to_csv("low_supply.csv", index=False)

top_orders = df.sort_values(by="total_price", ascending=False).head(3)

with open("report.txt", "w", encoding="utf-8") as f:
    f.write("Звіт по даних постачань\n")
    f.write(f"Середня ціна: {avg_price:.2f}\n")
    f.write(f"Медіана кількості: {median_quantity}\n")
    f.write(f"Стандартне відхилення ціни: {std_price:.2f}\n")
    f.write(f"Постачальник з найбільшим прибутком: {top_supplier}\n")
    f.write("Файл з дефіцитними поставками: low_supply.csv\n")

category_sum.plot(kind="bar", color="skyblue")
plt.title("Розподіл кількості препаратів за категоріями")
plt.xlabel("Категорія")
plt.ylabel("Кількість")
plt.savefig("category_distribution.png")


