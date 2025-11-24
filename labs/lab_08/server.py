import os
import csv
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort

app = Flask(__name__)

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "inventory.csv")
COLUMNS = ("id", "name", "category", "quantity", "price", "location", "created_at")


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()


def read_items():
    ensure_storage()
    items = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            row["quantity"] = int(row["quantity"])
            row["price"] = float(row["price"])
            items.append(row)
    return items


def write_items(items):
    ensure_storage()
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(items)


def validate_item(data):
    req = ["name", "category", "quantity", "price", "location"]
    for f in req:
        if f not in data or str(data[f]).strip() == "":
            abort(400, description=f"Missing field: {f}")

    try:
        data["quantity"] = int(data["quantity"])
    except:
        abort(400, description="quantity must be integer")

    try:
        data["price"] = float(str(data["price"]).replace(",", "."))
    except:
        abort(400, description="price must be float")

    return data

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(read_items())


@app.route("/items", methods=["POST"])
def create_item():
    data = validate_item(request.get_json())
    items = read_items()

    ids = [int(x["id"]) for x in items] or [0]
    new_id = max(ids) + 1

    item = {
        "id": str(new_id),
        "name": data["name"],
        "category": data["category"],
        "quantity": data["quantity"],
        "price": data["price"],
        "location": data["location"],
        "created_at": datetime.utcnow().isoformat(timespec="seconds")
    }

    items.append(item)
    write_items(items)
    return jsonify(item), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = validate_item(request.get_json())
    items = read_items()

    for it in items:
        if str(it["id"]) == str(item_id):
            it.update(data)
            write_items(items)
            return jsonify(it)
    abort(404)

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    items = read_items()
    new_items = [x for x in items if str(x["id"]) != str(item_id)]

    if len(new_items) == len(items):
        abort(404)

    write_items(new_items)
    return "", 204


@app.route("/export")
def export_csv():
    return send_file(CSV_PATH, as_attachment=True)


if __name__ == "__main__":
    ensure_storage()
    app.run(debug=True)


