# Inventory API — Interview Project

A small REST API for managing a product inventory, built with Python & Flask.

## Getting Started

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py
```

Server runs at `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products (optional: `?in_stock=true/false`) |
| POST | `/products` | Create a product (`name`, `category`: electronics/grocery/clothing, `price`, `quantity`) |
| GET | `/products/<id>` | Get a product by ID |
| PUT | `/products/<id>` | Update a product |
| DELETE | `/products/<id>` | Delete a product |
| GET | `/products/stats` | Get summary statistics |

## Running Tests

```bash
pytest tests/ -v
```

## Your Tasks

1. **Create a branch** called `interview/<your-name>`.
2. **Run the tests** — some will fail. Find and fix the **3 bugs** causing them.
3. **Add a new feature:** implement a `PATCH /products/<id>/sell` endpoint that sells one unit — it decrements `quantity` by 1, updates `in_stock`, and returns `400` if the product is out of stock.
4. **Commit your changes** with clear commit messages and open a **Pull Request** back to the main branch.
