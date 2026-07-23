import pytest

from agents.material.database_data_access import get_recipe


def test_get_recipe_returns_per_batch_quantities(seeded_db):
    assert get_recipe("Product A") == {
        "Material A": 100, "Material B": 200, "Material C": 150,
    }


def test_get_recipe_unknown_product_raises(seeded_db):
    with pytest.raises(ValueError):
        get_recipe("Product Z")
