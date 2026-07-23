"""Read product recipes from the SQLite plant DB (built by data/static_data/seed_data.py)."""
import os
import sqlite3

# Resolve to <repo_root>/data/static_data/plant.db; override with PLANT_DB_PATH.
DB_PATH = os.getenv(
    "PLANT_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "data", "static_data", "plant.db"),
)


def get_recipe(product: str, db_path: str | None = None) -> dict[str, float]:
    """Litres of each raw material required to make ONE batch of `product`.

    Raises ValueError if the product isn't in the database.
    """
    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT rm.name, pr.quantity
            FROM product_recipes pr
            JOIN products       p  ON p.id  = pr.product_id
            JOIN raw_materials  rm ON rm.id = pr.material_id
            WHERE p.name = ?
            ORDER BY rm.name
            """,
            (product,),
        ).fetchall()
    finally:
        conn.close()
    if not rows:
        raise ValueError(f"Unknown product: {product!r}")
    return {name: qty for name, qty in rows}
