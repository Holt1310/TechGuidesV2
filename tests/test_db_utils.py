import sqlite3
import json
import types
import os
import sys
from contextlib import contextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import db_utils


def setup_memory_db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE case_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            fields_json TEXT NOT NULL,
            rules_json TEXT,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT
        );
        CREATE TABLE cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            case_data TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT
        );
    ''')
    return conn


@contextmanager
def memory_connection(conn):
    try:
        yield conn
    finally:
        pass


def patch_db(monkeypatch, conn):
    monkeypatch.setattr(db_utils, 'get_db_connection', lambda: memory_connection(conn))


def test_case_template_crud(monkeypatch):
    conn = setup_memory_db()
    patch_db(monkeypatch, conn)

    tid, msg = db_utils.create_case_template('T1', 'desc', [{'id': 'f', 'name': 'F', 'type': 'text'}])
    assert tid is not None

    templates = db_utils.get_case_templates()
    assert len(templates) == 1
    assert templates[0]['name'] == 'T1'

    db_utils.update_case_template(tid, 'T1b', 'd', [{'id': 'f', 'name': 'F', 'type': 'text'}])
    t = db_utils.get_case_template(tid)
    assert t['name'] == 'T1b'

    db_utils.delete_case_template(tid)
    assert db_utils.get_case_template(tid) is None


def test_case_crud(monkeypatch):
    conn = setup_memory_db()
    patch_db(monkeypatch, conn)

    tid, _ = db_utils.create_case_template('T2', '', [{'id': 'a', 'name': 'A', 'type': 'text'}])
    cid, _ = db_utils.create_case(tid, {'a': '1'})
    case = db_utils.get_case(cid)
    assert case['case_data']['a'] == '1'

    db_utils.update_case(cid, {'a': '2'}, status='closed')
    case = db_utils.get_case(cid)
    assert case['status'] == 'closed'

    db_utils.delete_case(cid)
    assert db_utils.get_case(cid) is None
