import os
import json
import tempfile
import os
import os
import json
import tempfile
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import db_utils
from contextlib import contextmanager




def setup_module(module):
    # use a temporary database for tests
    module.db_fd, module.db_path = tempfile.mkstemp()

    @contextmanager
    def get_conn():
        conn = db_utils.sqlite3.connect(module.db_path)
        conn.row_factory = db_utils.sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    db_utils.get_db_connection = get_conn
    conn = db_utils.sqlite3.connect(module.db_path)
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            bio TEXT,
            timezone TEXT DEFAULT 'UTC',
            language TEXT DEFAULT 'en',
            email_notifications INTEGER DEFAULT 1,
            chat_notifications INTEGER DEFAULT 1,
            newsletter INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            last_login TEXT,
            api_key TEXT,
            api_enabled INTEGER DEFAULT 0,
            external_features INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS custom_tables_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            columns_json TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT
        );
        CREATE TABLE IF NOT EXISTS user_external_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            tool_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT 'bi bi-gear',
            type TEXT NOT NULL CHECK (type IN ('executable', 'website', 'script')),
            executable_path TEXT,
            website_url TEXT,
            parameters TEXT,
            is_enabled INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(username, tool_id)
        );
        CREATE TABLE IF NOT EXISTS case_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            fields_json TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT
        );
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            data_json TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT,
            FOREIGN KEY(template_id) REFERENCES case_templates(id)
        );
    ''')
    conn.commit()
    conn.close()


def teardown_module(module):
    os.close(module.db_fd)
    os.unlink(module.db_path)


def test_case_template_crud():
    tid = db_utils.create_case_template('TestT', 'desc', '[]')
    assert tid
    tpl = db_utils.get_case_template(tid)
    assert tpl['name'] == 'TestT'
    assert db_utils.update_case_template(tid, 'TestT2', 'd', '[]')
    templates = db_utils.get_all_case_templates()
    assert any(t['name']=='TestT2' for t in templates)
    assert db_utils.delete_case_template(tid)


def test_case_crud():
    tid = db_utils.create_case_template('Temp', '', '[]')
    cid = db_utils.create_case(tid, json.dumps({'a':'b'}))
    case = db_utils.get_case(cid)
    assert case
    assert db_utils.update_case(cid, json.dumps({'a':'c'}))
    cases = db_utils.get_all_cases()
    assert any(c['id']==cid for c in cases)
    assert db_utils.delete_case(cid)
    db_utils.delete_case_template(tid)

