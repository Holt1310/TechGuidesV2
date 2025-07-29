import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_utils
import database_init

database_init.init_database()


def test_create_get_delete_case():
    data = {"title": "Test", "description": "demo"}
    success, case_id = db_utils.create_case("default", data, "tester")
    assert success
    case = db_utils.get_case(case_id)
    assert case is not None
    assert case["template_id"] == "default"
    assert case["data"]["title"] == "Test"
    assert db_utils.delete_case(case_id)
