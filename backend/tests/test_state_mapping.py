import pytest

from mcp_server.batch_plant_functions import OPCUABatchPlantClient


@pytest.mark.parametrize("code, expected", [
    # every valid enum member, pinned as a regression guard on the mapping table
    (0, "disabled"),
    (1, "idle"),
    (2, "running"),
    (3, "starved"),
    (4, "blocked"),
    (5, "planned_downtime"),
    (6, "unplanned_downtime"),
    (7, "other"),
    # out-of-range codes fall through to the sentinel branch
    (99, "unknown_state_99"),
    (-1, "unknown_state_-1"),
])
def test_int_to_state_string(code, expected):
    assert OPCUABatchPlantClient()._int_to_state_string(code) == expected

