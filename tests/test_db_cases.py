import json
import os
import sqlite3
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_utils


def setup_module(module):
    # ensure tables exist
    from database_init import init_database
    init_database()


def teardown_function(function):
    # cleanup created rows
    with db_utils.get_db_connection() as conn:
        conn.execute('DELETE FROM cases')
        conn.execute('DELETE FROM case_templates')
        conn.commit()


def test_case_template_crud():
    ok, tid = db_utils.create_case_template('temp1', json.dumps([{"id":"f","name":"F","type":"text"}]))
    assert ok
    tpl = db_utils.get_case_template(tid)
    assert tpl['name'] == 'temp1'
    assert db_utils.update_case_template(tid, json.dumps([{"id":"x","name":"X","type":"text"}]))
    tpl2 = db_utils.get_case_template(tid)
    assert 'x' in tpl2['fields_json']
    assert db_utils.delete_case_template(tid)
    assert db_utils.get_case_template(tid) is None


def test_case_crud():
    ok, tid = db_utils.create_case_template('temp2', json.dumps([{"id":"f","name":"F","type":"text"}]))
    assert ok
    ok, cid = db_utils.create_case(tid, json.dumps({'f':'v'}), 'tester')
    assert ok
    case = db_utils.get_case(cid)
    assert json.loads(case['data_json'])['f'] == 'v'
    assert db_utils.update_case(cid, json.dumps({'f':'z'}))
    case2 = db_utils.get_case(cid)
    assert json.loads(case2['data_json'])['f'] == 'z'
    assert db_utils.delete_case(cid)
    db_utils.delete_case_template(tid)
