from agents.material.tools import calculate_material_requirements


def test_tool_multiplies_recipe_by_batches(seeded_db):
    result = calculate_material_requirements.invoke(
        {"product": "Product A", "batches": 3}
    )
    assert result == {"Material A": 300, "Material B": 600, "Material C": 450}
