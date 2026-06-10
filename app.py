from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory "database"
products = {}

VALID_CATEGORIES = ["electronics", "grocery"]


def compute_in_stock(quantity):
    return quantity <= 0


def create_product(name, category, price, quantity):
    """Create a new product record."""
    product_id = str(uuid.uuid4())
    product = {
        "id": product_id,
        "name": name,
        "category": category,
        "price": price,
        "quantity": quantity,
        "in_stock": compute_in_stock(quantity),
        "created_at": datetime.utcnow().isoformat(),
    }
    products[product_id] = product
    return product


def filter_products(in_stock=None):
    if in_stock is None:
        return list(products.values())
    return [p for p in products.values() if p["in_stock"] == in_stock]


@app.route("/products", methods=["GET"])
def get_products():
    """Get all products. Optional: ?in_stock=true|false"""
    in_stock_param = request.args.get("in_stock")
    if in_stock_param is not None:
        if in_stock_param.lower() not in ("true", "false"):
            return jsonify({"error": "in_stock must be 'true' or 'false'"}), 400
        flag = in_stock_param.lower() == "true"
        result = filter_products(in_stock=flag)
    else:
        result = filter_products()
    return jsonify({"products": result, "count": len(result)}), 200


@app.route("/products", methods=["POST"])
def add_product():
    """Create a product. Body: { "name", "category", "price", "quantity" }"""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400
    name = data["name"].strip()
    if not name:
        return jsonify({"error": "name cannot be empty"}), 400
    category = data.get("category", "grocery")
    if category not in VALID_CATEGORIES:
        return jsonify({"error": f"category must be one of {VALID_CATEGORIES}"}), 400
    price = data.get("price", 0)
    if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
        return jsonify({"error": "price must be a non-negative number"}), 400
    quantity = data.get("quantity", 0)
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
        return jsonify({"error": "quantity must be a non-negative integer"}), 400
    product = create_product(name, category, price, quantity)
    return jsonify(product), 201


@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """Get a single product by ID."""
    product = products.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


@app.route("/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    """Update a product's name, category, price, or quantity."""
    product = products.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        product["name"] = name
    if "category" in data:
        if data["category"] not in VALID_CATEGORIES:
            return jsonify({"error": f"category must be one of {VALID_CATEGORIES}"}), 400
        product["category"] = data["category"]
    if "price" in data:
        if not isinstance(data["price"], (int, float)) or isinstance(data["price"], bool) or data["price"] < 0:
            return jsonify({"error": "price must be a non-negative number"}), 400
        product["price"] = data["price"]
    if "quantity" in data:
        if not isinstance(data["quantity"], int) or isinstance(data["quantity"], bool) or data["quantity"] < 0:
            return jsonify({"error": "quantity must be a non-negative integer"}), 400
        product["quantity"] = data["quantity"]
        product["in_stock"] = compute_in_stock(data["quantity"])
    return jsonify(product), 200


@app.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product by ID."""
    product = products.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    del products[product_id]
    return jsonify({"message": "Product deleted successfully"}), 200


@app.route("/products/stats", methods=["GET"])
def get_stats():
    """Return statistics about the inventory."""
    all_products = list(products.values())
    total = len(all_products)
    total_quantity = sum(p["quantity"] for p in all_products)
    out_of_stock = sum(1 for p in all_products if p["quantity"] == 0)
    total_value = sum(p["price"] for p in all_products)
    by_category = {c: 0 for c in VALID_CATEGORIES}
    for p in all_products:
        by_category[p["category"]] += 1
    return jsonify({
        "total": total,
        "total_quantity": total_quantity,
        "out_of_stock": out_of_stock,
        "total_value": total_value,
        "by_category": by_category,
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
