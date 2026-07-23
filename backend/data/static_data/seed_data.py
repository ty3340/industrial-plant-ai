"""
seed_data.py — creates & seeds data/static_data/plant.db with dummy batch-plant
data (products, raw materials, per-batch recipes) so the material-calculating
agent can read recipes from SQLite instead of a real database.

Run directly to (re)build the DB:  python data/static_data/seed_data.py
"""
import os
import sqlite3

# The DB lives next to this file so any subsystem can reference it via DB_PATH.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plant.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS raw_materials (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    tank_number INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS product_recipes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    material_id INTEGER NOT NULL REFERENCES raw_materials(id),
    quantity    REAL NOT NULL,          -- litres of material required per batch
    UNIQUE (product_id, material_id)
);
"""

RAW_MATERIALS = [("Material A", 1), ("Material B", 2), ("Material C", 3)]
PRODUCTS = ["Product A", "Product B", "Product C"]
RECIPES = {
    "Product A": {"Material A": 100, "Material B": 200, "Material C": 150},
    "Product B": {"Material A": 150, "Material B": 100, "Material C": 250},
    "Product C": {"Material A": 200, "Material B": 300, "Material C": 100},
}


def seed(db_path: str = DB_PATH) -> None:
    """Create the schema and (re)populate it with dummy data. Idempotent."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA)

        # Clean slate so re-running gives deterministic data (this is what makes
        # seed() idempotent).
        conn.execute("DELETE FROM product_recipes;")
        conn.execute("DELETE FROM raw_materials;")
        conn.execute("DELETE FROM products;")

        material_ids = {}
        for name, tank in RAW_MATERIALS:
            cur = conn.execute(
                "INSERT INTO raw_materials (name, tank_number) VALUES (?, ?);",
                (name, tank),
            )
            material_ids[name] = cur.lastrowid

        product_ids = {}
        for name in PRODUCTS:
            cur = conn.execute("INSERT INTO products (name) VALUES (?);", (name,))
            product_ids[name] = cur.lastrowid

        for product, recipe in RECIPES.items():
            for material, quantity in recipe.items():
                conn.execute(
                    "INSERT INTO product_recipes (product_id, material_id, quantity) "
                    "VALUES (?, ?, ?);",
                    (product_ids[product], material_ids[material], quantity),
                )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
    print(f"Seeded SQLite database at: {DB_PATH}")
