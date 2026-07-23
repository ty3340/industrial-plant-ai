"""Re-running the seeder is idempotent (it DELETEs before inserting)."""
"""Test: check if the delete works properly by comparing before and after insert with the same number of rows"""
import sqlite3

from data.static_data.seed_data import seed


def _counts(db_path):
    conn = sqlite3.connect(db_path)
    try:
        products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        materials = conn.execute("SELECT COUNT(*) FROM raw_materials").fetchone()[0]
        recipes = conn.execute("SELECT COUNT(*) FROM product_recipes").fetchone()[0]
    finally:
        conn.close()
    return products, materials, recipes


def test_seeding_twice_is_idempotent(tmp_path):
    db = tmp_path / "plant.db"
    seed(str(db))
    first = _counts(str(db))

    seed(str(db))
    second = _counts(str(db))

    assert first == second == (3, 3, 9)   # 3 products, 3 materials, 3×3 recipes


    




