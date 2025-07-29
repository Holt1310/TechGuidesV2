"""
Enhanced database utilities for the improved case management system.
Provides functions for managing interactive fields, data tables, and dependencies.
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

@contextmanager
def get_enhanced_db_connection():
    """Context manager for enhanced database connections."""
    conn = None
    try:
        conn = sqlite3.connect('enhanced_database.db')
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# Data Table Management Functions

def create_data_table(table_name, display_name, description, columns, created_by="admin"):
    """Create a new data table with specified columns."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Create the data table record
            cursor.execute('''
                INSERT INTO data_tables (table_name, display_name, description, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (table_name, display_name, description, current_time, created_by))
            
            table_id = cursor.lastrowid
            
            # Create columns
            for column in columns:
                cursor.execute('''
                    INSERT INTO data_table_columns 
                    (table_id, column_name, display_name, data_type, is_key_field, is_display_field, is_searchable, validation_rules, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    table_id,
                    column['column_name'],
                    column['display_name'],
                    column['data_type'],
                    column.get('is_key_field', 0),
                    column.get('is_display_field', 0),
                    column.get('is_searchable', 1),
                    json.dumps(column.get('validation_rules', {})),
                    current_time
                ))
            
            conn.commit()
            return table_id, "Data table created successfully"
            
    except Exception as e:
        return None, f"Error creating data table: {str(e)}"

def add_data_table_record(table_id, record_data, created_by="admin"):
    """Add a record to a data table."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO data_table_records (table_id, record_data, created_at, created_by)
                VALUES (?, ?, ?, ?)
            ''', (table_id, json.dumps(record_data), current_time, created_by))
            
            conn.commit()
            return cursor.lastrowid, "Record added successfully"
            
    except Exception as e:
        return None, f"Error adding record: {str(e)}"

def search_data_table(table_id, search_term="", limit=10):
    """Search records in a data table."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get table columns
            cursor.execute('''
                SELECT column_name, display_name, is_display_field, is_searchable
                FROM data_table_columns 
                WHERE table_id = ? 
                ORDER BY is_key_field DESC, is_display_field DESC
            ''', (table_id,))
            columns = cursor.fetchall()
            
            # Get records
            query = '''
                SELECT id, record_data 
                FROM data_table_records 
                WHERE table_id = ? AND is_active = 1
            '''
            params = [table_id]
            
            if search_term:
                query += ' AND record_data LIKE ?'
                params.append(f'%{search_term}%')
            
            query += ' LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            # Format results
            results = []
            for record in records:
                data = json.loads(record['record_data'])
                display_field = next((col['column_name'] for col in columns if col['is_display_field']), 
                                   columns[0]['column_name'] if columns else 'id')
                
                results.append({
                    'id': record['id'],
                    'data': data,
                    'display': data.get(display_field, str(record['id']))
                })
            
            return results, "Search completed successfully"
            
    except Exception as e:
        return [], f"Error searching data table: {str(e)}"

# Enhanced Template Management

def create_enhanced_template(name, description, category, fields, created_by="admin"):
    """Create an enhanced case template with interactive fields."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Create template
            template_config = {
                'layout': 'default',
                'validation': 'client_server',
                'save_mode': 'auto',
                'theme': 'default'
            }
            
            cursor.execute('''
                INSERT INTO enhanced_case_templates 
                (name, description, category, template_config, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, category, json.dumps(template_config), current_time, created_by))
            
            template_id = cursor.lastrowid
            
            # Create fields
            for order, field in enumerate(fields):
                cursor.execute('''
                    INSERT INTO template_fields 
                    (template_id, field_id, field_name, field_type, is_required, display_order, 
                     field_config, validation_rules, conditional_logic, data_table_id, parent_field_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template_id,
                    field['field_id'],
                    field['field_name'],
                    field['field_type'],
                    field.get('is_required', 0),
                    order,
                    json.dumps(field.get('config', {})),
                    json.dumps(field.get('validation_rules', {})),
                    json.dumps(field.get('conditional_logic', {})),
                    field.get('data_table_id'),
                    field.get('parent_field_id'),
                    current_time
                ))
                
                field_record_id = cursor.lastrowid
                
                # Create field dependencies if specified
                if 'dependencies' in field:
                    for dep in field['dependencies']:
                        cursor.execute('''
                            INSERT INTO field_dependencies 
                            (dependent_field_id, parent_field_id, condition_type, condition_value, 
                             action_type, action_config, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            field_record_id,
                            dep['parent_field_id'],
                            dep['condition_type'],
                            dep.get('condition_value'),
                            dep['action_type'],
                            json.dumps(dep.get('action_config', {})),
                            current_time
                        ))
            
            conn.commit()
            return template_id, "Enhanced template created successfully"
            
    except Exception as e:
        return None, f"Error creating enhanced template: {str(e)}"

def get_template_with_fields(template_id):
    """Get complete template with all fields and dependencies."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get template
            cursor.execute('''
                SELECT * FROM enhanced_case_templates WHERE id = ?
            ''', (template_id,))
            template = cursor.fetchone()
            
            if not template:
                return None, "Template not found"
            
            # Get fields
            cursor.execute('''
                SELECT tf.*, dt.table_name as data_table_name
                FROM template_fields tf
                LEFT JOIN data_tables dt ON tf.data_table_id = dt.id
                WHERE tf.template_id = ?
                ORDER BY tf.display_order
            ''', (template_id,))
            fields = cursor.fetchall()
            
            # Get dependencies for each field
            field_dependencies = {}
            for field in fields:
                cursor.execute('''
                    SELECT fd.*, pf.field_id as parent_field_name
                    FROM field_dependencies fd
                    JOIN template_fields pf ON fd.parent_field_id = pf.id
                    WHERE fd.dependent_field_id = ?
                ''', (field['id'],))
                dependencies = cursor.fetchall()
                field_dependencies[field['id']] = [dict(dep) for dep in dependencies]
            
            # Format result
            result = {
                'template': dict(template),
                'fields': [dict(field) for field in fields],
                'dependencies': field_dependencies
            }
            
            return result, "Template retrieved successfully"
            
    except Exception as e:
        return None, f"Error retrieving template: {str(e)}"

# Case Management

def create_enhanced_case(template_id, title, description, case_data, created_by="admin", **kwargs):
    """Create an enhanced case instance."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Generate case number
            cursor.execute('SELECT COUNT(*) FROM enhanced_cases')
            case_count = cursor.fetchone()[0]
            case_number = f"CASE-{case_count + 1:06d}"
            
            cursor.execute('''
                INSERT INTO enhanced_cases 
                (case_number, template_id, title, description, status, priority, 
                 assigned_to, case_data, metadata, tags, due_date, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_number,
                template_id,
                title,
                description,
                kwargs.get('status', 'draft'),
                kwargs.get('priority', 'medium'),
                kwargs.get('assigned_to'),
                json.dumps(case_data),
                json.dumps(kwargs.get('metadata', {})),
                kwargs.get('tags', ''),
                kwargs.get('due_date'),
                current_time,
                created_by
            ))
            
            case_id = cursor.lastrowid
            
            # Create history entry
            cursor.execute('''
                INSERT INTO case_history 
                (case_id, action_type, comment, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (case_id, 'created', f'Case {case_number} created', current_time, created_by))
            
            conn.commit()
            return case_id, case_number, "Case created successfully"
            
    except Exception as e:
        return None, None, f"Error creating case: {str(e)}"

def update_case_field(case_id, field_name, old_value, new_value, updated_by="admin"):
    """Update a specific field in a case and log the change."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Get current case data
            cursor.execute('SELECT case_data FROM enhanced_cases WHERE id = ?', (case_id,))
            case = cursor.fetchone()
            
            if not case:
                return False, "Case not found"
            
            case_data = json.loads(case['case_data'])
            case_data[field_name] = new_value
            
            # Update case
            cursor.execute('''
                UPDATE enhanced_cases 
                SET case_data = ?, updated_at = ?, last_modified_by = ?
                WHERE id = ?
            ''', (json.dumps(case_data), current_time, updated_by, case_id))
            
            # Log change
            cursor.execute('''
                INSERT INTO case_history 
                (case_id, action_type, field_name, old_value, new_value, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (case_id, 'field_changed', field_name, str(old_value), str(new_value), current_time, updated_by))
            
            conn.commit()
            return True, "Field updated successfully"
            
    except Exception as e:
        return False, f"Error updating field: {str(e)}"

def get_cases_list(status=None, assigned_to=None, template_id=None, limit=50, offset=0):
    """Get a list of cases with optional filtering."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT ec.*, ect.name as template_name
                FROM enhanced_cases ec
                JOIN enhanced_case_templates ect ON ec.template_id = ect.id
                WHERE 1=1
            '''
            params = []
            
            if status:
                query += ' AND ec.status = ?'
                params.append(status)
            
            if assigned_to:
                query += ' AND ec.assigned_to = ?'
                params.append(assigned_to)
            
            if template_id:
                query += ' AND ec.template_id = ?'
                params.append(template_id)
            
            query += ' ORDER BY ec.created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            cases = cursor.fetchall()
            
            return [dict(case) for case in cases], "Cases retrieved successfully"
            
    except Exception as e:
        return [], f"Error retrieving cases: {str(e)}"

def get_data_tables_list():
    """Get list of all available data tables."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dt.*, 
                       COUNT(dtr.id) as record_count,
                       GROUP_CONCAT(dtc.display_name) as columns
                FROM data_tables dt
                LEFT JOIN data_table_records dtr ON dt.id = dtr.table_id AND dtr.is_active = 1
                LEFT JOIN data_table_columns dtc ON dt.id = dtc.table_id
                WHERE dt.is_active = 1
                GROUP BY dt.id
                ORDER BY dt.display_name
            ''')
            
            tables = cursor.fetchall()
            return [dict(table) for table in tables], "Data tables retrieved successfully"
            
    except Exception as e:
        return [], f"Error retrieving data tables: {str(e)}"

def get_templates_list():
    """Get list of all enhanced templates."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ect.*, 
                       COUNT(tf.id) as field_count
                FROM enhanced_case_templates ect
                LEFT JOIN template_fields tf ON ect.id = tf.template_id
                GROUP BY ect.id
                ORDER BY ect.created_at DESC
            ''')
            
            templates = cursor.fetchall()
            return [dict(template) for template in templates]
            
    except Exception as e:
        print(f"Error retrieving templates: {str(e)}")
        return []

# Utility Functions

def validate_field_dependencies(template_id, case_data):
    """Validate field dependencies for a case."""
    try:
        template_data, msg = get_template_with_fields(template_id)
        if not template_data:
            return False, msg
        
        errors = []
        
        for field in template_data['fields']:
            field_id = field['field_id']
            field_value = case_data.get(field_id)
            
            # Check dependencies
            if field['id'] in template_data['dependencies']:
                for dep in template_data['dependencies'][field['id']]:
                    parent_value = case_data.get(dep['parent_field_name'])
                    
                    # Evaluate condition
                    condition_met = evaluate_condition(
                        parent_value, 
                        dep['condition_type'], 
                        dep.get('condition_value')
                    )
                    
                    # Apply action if condition is met
                    if condition_met:
                        action_config = json.loads(dep.get('action_config', '{}'))
                        
                        if dep['action_type'] == 'require' and not field_value:
                            errors.append(f"Field '{field['field_name']}' is required")
                        elif dep['action_type'] == 'set_value':
                            case_data[field_id] = action_config.get('value')
        
        return len(errors) == 0, errors if errors else "Validation passed"
        
    except Exception as e:
        return False, f"Error validating dependencies: {str(e)}"

def evaluate_condition(value, condition_type, condition_value):
    """Evaluate a dependency condition."""
    if condition_type == 'equals':
        return str(value) == str(condition_value)
    elif condition_type == 'not_equals':
        return str(value) != str(condition_value)
    elif condition_type == 'contains':
        return condition_value in str(value)
    elif condition_type == 'not_contains':
        return condition_value not in str(value)
    elif condition_type == 'is_empty':
        return not value or str(value).strip() == ''
    elif condition_type == 'is_not_empty':
        return value and str(value).strip() != ''
    elif condition_type == 'in_list':
        return str(value) in condition_value.split(',')
    elif condition_type == 'not_in_list':
        return str(value) not in condition_value.split(',')
    
    return False

def get_field_options_for_dependency(parent_field_id, parent_value):
    """Get dynamic options for a dependent field based on parent value."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get the field configuration
            cursor.execute('''
                SELECT field_config, data_table_id 
                FROM template_fields 
                WHERE id = ?
            ''', (parent_field_id,))
            
            field = cursor.fetchone()
            if not field:
                return [], "Field not found"
            
            config = json.loads(field['field_config'])
            
            # If it's connected to a data table, filter by parent value
            if field['data_table_id']:
                results, msg = search_data_table(field['data_table_id'], parent_value)
                return results, msg
            
            # Otherwise use static options from config
            options_map = config.get('optionsMap', {})
            return options_map.get(str(parent_value), []), "Options retrieved"
            
    except Exception as e:
        return [], f"Error getting field options: {str(e)}"

def delete_enhanced_template(template_id):
    """Delete an enhanced template if no cases reference it."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM enhanced_cases WHERE template_id = ?', (template_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Template is in use by existing cases"
            cursor.execute('DELETE FROM enhanced_case_templates WHERE id = ?', (template_id,))
            conn.commit()
            return True, "Template deleted successfully"
    except Exception as e:
        return False, f"Error deleting template: {str(e)}"


def update_enhanced_template(template_id, name, description, category, fields, updated_by="admin"):
    """Update an existing enhanced template with new metadata and fields."""
    try:
        with get_enhanced_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()

            cursor.execute('''
                UPDATE enhanced_case_templates
                SET name = ?, description = ?, category = ?, updated_at = ?
                WHERE id = ?
            ''', (name, description, category, current_time, template_id))

            cursor.execute('DELETE FROM template_fields WHERE template_id = ?', (template_id,))

            for order, field in enumerate(fields):
                cursor.execute('''
                    INSERT INTO template_fields
                    (template_id, field_id, field_name, field_type, is_required,
                     display_order, field_config, validation_rules, conditional_logic,
                     data_table_id, parent_field_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template_id,
                    field['field_id'],
                    field['field_name'],
                    field['field_type'],
                    field.get('is_required', 0),
                    order,
                    json.dumps(field.get('config', {})),
                    json.dumps(field.get('validation_rules', {})),
                    json.dumps(field.get('conditional_logic', {})),
                    field.get('data_table_id'),
                    field.get('parent_field_id'),
                    current_time
                ))

                field_record_id = cursor.lastrowid
                if 'dependencies' in field:
                    for dep in field['dependencies']:
                        cursor.execute('''
                            INSERT INTO field_dependencies
                            (dependent_field_id, parent_field_id, condition_type, condition_value,
                             action_type, action_config, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            field_record_id,
                            dep['parent_field_id'],
                            dep['condition_type'],
                            dep.get('condition_value'),
                            dep['action_type'],
                            json.dumps(dep.get('action_config', {})),
                            current_time
                        ))

            conn.commit()
            return True, "Template updated successfully"
    except Exception as e:
        return False, f"Error updating template: {str(e)}"
