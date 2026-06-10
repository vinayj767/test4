import pytest
from app import app, products


@pytest.fixture(autouse=True)
def clear_products():
    """Reset products before each test."""
    products.clear()
    yield
    products.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_products_empty(client):
    res = client.get("/products")
    assert res.status_code == 200
    assert res.json["products"] == []
    assert res.json["count"] == 0


def test_create_product_in_stock(client):
    res = client.post("/products", json={"name": "Laptop", "category": "electronics", "price": 1000, "quantity": 5})
    assert res.status_code == 201
    assert res.json["name"] == "Laptop"
    assert res.json["in_stock"] is True  # Fails until Bug 1 is fixed


def test_create_product_missing_name(client):
    res = client.post("/products", json={"quantity": 3})
    assert res.status_code == 400


def test_create_product_clothing_category(client):
    res = client.post("/products", json={"name": "T-Shirt", "category": "clothing", "quantity": 2})
    assert res.status_code == 201  # Fails until Bug 2 is fixed


def test_get_product_by_id(client):
    create = client.post("/products", json={"name": "Apple", "category": "grocery", "quantity": 10})
    product_id = create.json["id"]
    res = client.get(f"/products/{product_id}")
    assert res.status_code == 200
    assert res.json["id"] == product_id


def test_update_product(client):
    create = client.post("/products", json={"name": "Old", "category": "grocery", "quantity": 1})
    product_id = create.json["id"]
    res = client.put(f"/products/{product_id}", json={"name": "New", "quantity": 0})
    assert res.status_code == 200
    assert res.json["name"] == "New"
    assert res.json["quantity"] == 0


def test_delete_product(client):
    create = client.post("/products", json={"name": "Delete me", "category": "grocery", "quantity": 1})
    product_id = create.json["id"]
    res = client.delete(f"/products/{product_id}")
    assert res.status_code == 200


def test_stats_total_value(client):
    client.post("/products", json={"name": "A", "category": "grocery", "price": 10, "quantity": 3})
    client.post("/products", json={"name": "B", "category": "grocery", "price": 5, "quantity": 4})
    res = client.get("/products/stats")
    assert res.status_code == 200
    assert res.json["total"] == 2
    # total_value = 10*3 + 5*4 = 50
    assert res.json["total_value"] == 50  # Fails until Bug 3 is fixed


# --- Feature tests: PATCH /products/<id>/sell (implement this endpoint) ---

def test_sell_product(client):
    create = client.post("/products", json={"name": "Sellable", "category": "grocery", "quantity": 2})
    product_id = create.json["id"]
    res = client.patch(f"/products/{product_id}/sell")
    assert res.status_code == 200
    assert res.json["quantity"] == 1
    assert res.json["in_stock"] is True


def test_sell_last_unit_marks_out_of_stock(client):
    create = client.post("/products", json={"name": "Last one", "category": "grocery", "quantity": 1})
    product_id = create.json["id"]
    res = client.patch(f"/products/{product_id}/sell")
    assert res.status_code == 200
    assert res.json["quantity"] == 0
    assert res.json["in_stock"] is False


def test_sell_when_out_of_stock(client):
    create = client.post("/products", json={"name": "None left", "category": "grocery", "quantity": 0})
    product_id = create.json["id"]
    res = client.patch(f"/products/{product_id}/sell")
    assert res.status_code == 400
