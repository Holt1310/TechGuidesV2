"""
Enhanced database initialization for the improved case management system.
Includes support for interactive field types, data tables, and dependent fields.
"""

import sqlite3
import json
from datetime import datetime

def init_enhanced_database():
    """Initialize the enhanced database with all required tables."""
    try:
        db_path = 'enhanced_database.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table (keeping existing structure)
        cursor.execute('''
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
            )
        ''')
        
        # Create enhanced data tables for autocomplete and dropdowns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT
            )
        ''')
        
        # Create data table columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_table_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER NOT NULL,
                column_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                data_type TEXT NOT NULL CHECK (data_type IN ('text', 'number', 'date', 'boolean')),
                is_key_field INTEGER DEFAULT 0,
                is_display_field INTEGER DEFAULT 0,
                is_searchable INTEGER DEFAULT 1,
                validation_rules TEXT,
                created_at TEXT,
                FOREIGN KEY (table_id) REFERENCES data_tables(id) ON DELETE CASCADE,
                UNIQUE(table_id, column_name)
            )
        ''')
        
        # Create data table records (dynamic data storage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_table_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER NOT NULL,
                record_data TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                FOREIGN KEY (table_id) REFERENCES data_tables(id) ON DELETE CASCADE
            )
        ''')
        
        # Enhanced case templates with field types and dependencies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_case_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                version INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                template_config TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT
            )
        ''')
        
        # Enhanced field definitions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                field_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                field_type TEXT NOT NULL CHECK (field_type IN (
                    'text', 'textarea', 'number', 'email', 'phone', 'url', 'date', 'datetime',
                    'select', 'multiselect', 'radio', 'checkbox', 'toggle',
                    'autocomplete', 'data_table_lookup', 'dependent_field',
                    'file_upload', 'image_upload', 'signature', 'rating',
                    'location', 'color', 'json_editor'
                )),
                is_required INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                field_config TEXT NOT NULL,
                validation_rules TEXT,
                conditional_logic TEXT,
                data_table_id INTEGER,
                parent_field_id INTEGER,
                created_at TEXT,
                FOREIGN KEY (template_id) REFERENCES enhanced_case_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (data_table_id) REFERENCES data_tables(id),
                FOREIGN KEY (parent_field_id) REFERENCES template_fields(id),
                UNIQUE(template_id, field_id)
            )
        ''')
        
        # Field dependencies and conditional logic
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS field_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dependent_field_id INTEGER NOT NULL,
                parent_field_id INTEGER NOT NULL,
                condition_type TEXT NOT NULL CHECK (condition_type IN (
                    'equals', 'not_equals', 'contains', 'not_contains',
                    'greater_than', 'less_than', 'in_list', 'not_in_list',
                    'is_empty', 'is_not_empty'
                )),
                condition_value TEXT,
                action_type TEXT NOT NULL CHECK (action_type IN (
                    'show', 'hide', 'enable', 'disable', 'require', 'optional',
                    'set_value', 'clear_value', 'update_options'
                )),
                action_config TEXT,
                created_at TEXT,
                FOREIGN KEY (dependent_field_id) REFERENCES template_fields(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_field_id) REFERENCES template_fields(id) ON DELETE CASCADE
            )
        ''')
        
        # Enhanced cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT UNIQUE NOT NULL,
                template_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft' CHECK (status IN (
                    'draft', 'open', 'in_progress', 'pending', 'resolved', 
                    'closed', 'cancelled', 'escalated'
                )),
                priority TEXT DEFAULT 'medium' CHECK (priority IN (
                    'low', 'medium', 'high', 'urgent', 'critical'
                )),
                assigned_to TEXT,
                case_data TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                due_date TEXT,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                last_modified_by TEXT,
                FOREIGN KEY (template_id) REFERENCES enhanced_case_templates(id)
            )
        ''')
        
        # Case history and audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                action_type TEXT NOT NULL CHECK (action_type IN (
                    'created', 'updated', 'status_changed', 'assigned', 
                    'comment_added', 'attachment_added', 'field_changed'
                )),
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                comment TEXT,
                created_at TEXT,
                created_by TEXT,
                FOREIGN KEY (case_id) REFERENCES enhanced_cases(id) ON DELETE CASCADE
            )
        ''')
        
        # Case attachments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                file_path TEXT NOT NULL,
                uploaded_at TEXT,
                uploaded_by TEXT,
                FOREIGN KEY (case_id) REFERENCES enhanced_cases(id) ON DELETE CASCADE
            )
        ''')
        
        # Case comments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                is_internal INTEGER DEFAULT 0,
                created_at TEXT,
                created_by TEXT,
                FOREIGN KEY (case_id) REFERENCES enhanced_cases(id) ON DELETE CASCADE
            )
        ''')
        
        # Form builder configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS form_builder_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT UNIQUE NOT NULL,
                config_type TEXT NOT NULL CHECK (config_type IN (
                    'field_type', 'validation_rule', 'conditional_logic', 'data_source'
                )),
                config_data TEXT NOT NULL,
                is_system INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("Enhanced database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing enhanced database: {e}")
        return False

def create_sample_data_tables():
    """Create sample data tables for demonstration."""
    try:
        conn = sqlite3.connect('enhanced_database.db')
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        
        # Create departments data table
        cursor.execute('''
            INSERT INTO data_tables (table_name, display_name, description, created_at, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', ('departments', 'Departments', 'Company departments', current_time, 'system'))
        dept_table_id = cursor.lastrowid
        
        # Create department columns
        dept_columns = [
            ('dept_id', 'Department ID', 'text', 1, 0, 1),
            ('dept_name', 'Department Name', 'text', 0, 1, 1),
            ('manager', 'Manager', 'text', 0, 0, 1),
            ('budget', 'Budget', 'number', 0, 0, 0)
        ]
        
        for col_name, display_name, data_type, is_key, is_display, is_searchable in dept_columns:
            cursor.execute('''
                INSERT INTO data_table_columns 
                (table_id, column_name, display_name, data_type, is_key_field, is_display_field, is_searchable, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dept_table_id, col_name, display_name, data_type, is_key, is_display, is_searchable, current_time))
        
        # Add department data
        departments = [
            {'dept_id': 'IT', 'dept_name': 'Information Technology', 'manager': 'John Smith', 'budget': 500000},
            {'dept_id': 'HR', 'dept_name': 'Human Resources', 'manager': 'Jane Doe', 'budget': 200000},
            {'dept_id': 'FIN', 'dept_name': 'Finance', 'manager': 'Bob Johnson', 'budget': 300000},
            {'dept_id': 'MKT', 'dept_name': 'Marketing', 'manager': 'Alice Brown', 'budget': 250000}
        ]
        
        for dept in departments:
            cursor.execute('''
                INSERT INTO data_table_records (table_id, record_data, created_at, created_by)
                VALUES (?, ?, ?, ?)
            ''', (dept_table_id, json.dumps(dept), current_time, 'system'))
        
        # Create categories data table
        cursor.execute('''
            INSERT INTO data_tables (table_name, display_name, description, created_at, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', ('categories', 'Issue Categories', 'Categorization for support issues', current_time, 'system'))
        cat_table_id = cursor.lastrowid
        
        # Create category columns
        cat_columns = [
            ('cat_id', 'Category ID', 'text', 1, 0, 1),
            ('cat_name', 'Category Name', 'text', 0, 1, 1),
            ('parent_id', 'Parent Category', 'text', 0, 0, 1),
            ('sla_hours', 'SLA Hours', 'number', 0, 0, 0)
        ]
        
        for col_name, display_name, data_type, is_key, is_display, is_searchable in cat_columns:
            cursor.execute('''
                INSERT INTO data_table_columns 
                (table_id, column_name, display_name, data_type, is_key_field, is_display_field, is_searchable, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cat_table_id, col_name, display_name, data_type, is_key, is_display, is_searchable, current_time))
        
        # Add category data
        categories = [
            {'cat_id': 'HW', 'cat_name': 'Hardware Issues', 'parent_id': '', 'sla_hours': 24},
            {'cat_id': 'HW_LAPTOP', 'cat_name': 'Laptop Problems', 'parent_id': 'HW', 'sla_hours': 8},
            {'cat_id': 'HW_DESKTOP', 'cat_name': 'Desktop Problems', 'parent_id': 'HW', 'sla_hours': 12},
            {'cat_id': 'SW', 'cat_name': 'Software Issues', 'parent_id': '', 'sla_hours': 16},
            {'cat_id': 'SW_OS', 'cat_name': 'Operating System', 'parent_id': 'SW', 'sla_hours': 8},
            {'cat_id': 'SW_APP', 'cat_name': 'Application Software', 'parent_id': 'SW', 'sla_hours': 12},
            {'cat_id': 'NET', 'cat_name': 'Network Issues', 'parent_id': '', 'sla_hours': 4},
            {'cat_id': 'ACC', 'cat_name': 'Account Access', 'parent_id': '', 'sla_hours': 2}
        ]
        
        for cat in categories:
            cursor.execute('''
                INSERT INTO data_table_records (table_id, record_data, created_at, created_by)
                VALUES (?, ?, ?, ?)
            ''', (cat_table_id, json.dumps(cat), current_time, 'system'))
        
        conn.commit()
        conn.close()
        
        print("Sample data tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating sample data tables: {e}")
        return False

def create_form_builder_configs():
    """Create default form builder configurations."""
    try:
        conn = sqlite3.connect('enhanced_database.db')
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        
        # Field type configurations
        field_types = [
            {
                'name': 'Enhanced Text Input',
                'type': 'text',
                'config': {
                    'placeholder': 'Enter text...',
                    'maxLength': 255,
                    'pattern': '',
                    'autocomplete': True,
                    'suggestions': []
                }
            },
            {
                'name': 'Data Table Lookup',
                'type': 'data_table_lookup',
                'config': {
                    'searchable': True,
                    'multiSelect': False,
                    'displayFormat': '{display_field}',
                    'valueFormat': '{key_field}',
                    'minSearchLength': 2,
                    'maxResults': 10
                }
            },
            {
                'name': 'Dependent Select',
                'type': 'dependent_field',
                'config': {
                    'dependsOn': '',
                    'optionsMap': {},
                    'defaultOption': '-- Select --',
                    'cascade': True
                }
            },
            {
                'name': 'Smart Autocomplete',
                'type': 'autocomplete',
                'config': {
                    'dataSource': 'static',
                    'options': [],
                    'minLength': 1,
                    'maxResults': 10,
                    'allowCustom': True,
                    'fuzzySearch': True
                }
            }
        ]
        
        for field_type in field_types:
            cursor.execute('''
                INSERT INTO form_builder_configs (config_name, config_type, config_data, is_system, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (field_type['name'], 'field_type', json.dumps(field_type), 1, current_time, 'system'))
        
        # Validation rule configurations
        validation_rules = [
            {
                'name': 'Required Field',
                'rule': 'required',
                'config': {'message': 'This field is required'}
            },
            {
                'name': 'Email Format',
                'rule': 'email',
                'config': {'message': 'Please enter a valid email address'}
            },
            {
                'name': 'Phone Number',
                'rule': 'phone',
                'config': {'pattern': r'^\+?[\d\s\-\(\)]+$', 'message': 'Please enter a valid phone number'}
            },
            {
                'name': 'Minimum Length',
                'rule': 'minLength',
                'config': {'length': 3, 'message': 'Must be at least {length} characters'}
            },
            {
                'name': 'Maximum Length',
                'rule': 'maxLength',
                'config': {'length': 255, 'message': 'Must not exceed {length} characters'}
            }
        ]
        
        for rule in validation_rules:
            cursor.execute('''
                INSERT INTO form_builder_configs (config_name, config_type, config_data, is_system, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rule['name'], 'validation_rule', json.dumps(rule), 1, current_time, 'system'))
        
        conn.commit()
        conn.close()
        
        print("Form builder configurations created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating form builder configs: {e}")
        return False

if __name__ == "__main__":
    print("Initializing enhanced database...")
    init_enhanced_database()
    create_sample_data_tables()
    create_form_builder_configs()
    print("Enhanced database setup completed!")
