"""LangChain tool exposing recipe math to the Material Calculating agent."""
from langchain_core.tools import tool

from agents.material.database_data_access import get_recipe


@tool
def calculate_material_requirements(product: str, batches: int) -> dict:
    """Litres of each raw material needed to produce `batches` batches of `product`.

    Looks up the per-batch recipe in the plant database and multiplies by the
    number of batches.
    """
    recipe = get_recipe(product)
    return {material: qty * batches for material, qty in recipe.items()}
