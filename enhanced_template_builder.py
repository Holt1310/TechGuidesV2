#!/usr/bin/env python3
"""
Interactive Template Builder for Enhanced Case Management System
Creates sophisticated case templates with dependent fields, data table lookups, and more.
"""

import json
import sys
import os
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_db_utils import (
    create_enhanced_template, create_data_table, add_data_table_record,
    get_data_tables_list, search_data_table
)

class InteractiveTemplateBuilder:
    def __init__(self):
        self.field_types = {
            'text': 'Text Input',
            'textarea': 'Multi-line Text',
            'number': 'Number Input',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'date': 'Date Picker',
            'select': 'Dropdown Select',
            'multiselect': 'Multi-Select Dropdown',
            'radio': 'Radio Buttons',
            'checkbox': 'Checkboxes',
            'autocomplete': 'Autocomplete Text',
            'data_table_lookup': 'Data Table Lookup',
            'dependent_field': 'Dependent Field',
            'file_upload': 'File Upload',
            'rating': 'Star Rating',
            'toggle': 'Toggle Switch'
        }
        
        self.condition_types = {
            'equals': 'Equals',
            'not_equals': 'Not Equals',
            'contains': 'Contains',
            'not_contains': 'Does Not Contain',
            'is_empty': 'Is Empty',
            'is_not_empty': 'Is Not Empty',
            'in_list': 'In List',
            'not_in_list': 'Not In List'
        }
        
        self.action_types = {
            'show': 'Show Field',
            'hide': 'Hide Field',
            'require': 'Make Required',
            'optional': 'Make Optional',
            'set_value': 'Set Value',
            'update_options': 'Update Options'
        }

    def create_template_interactive(self):
        """Create a template through interactive prompts."""
        print("\n" + "="*60)
        print("         ENHANCED CASE TEMPLATE BUILDER")
        print("="*60)
        
        # Basic template info
        name = self.get_input("Template Name", required=True)
        description = self.get_input("Template Description")
        category = self.get_input("Category", default="General")
        
        print(f"\nCreating template: {name}")
        print("-" * 40)
        
        fields = []
        field_counter = 1
        
        while True:
            print(f"\n--- Field {field_counter} ---")
            field = self.create_field_interactive(fields)
            
            if field:
                fields.append(field)
                field_counter += 1
                
                continue_adding = input("\nAdd another field? (y/n) [y]: ").strip().lower()
                if continue_adding in ['n', 'no']:
                    break
            else:
                break
        
        if not fields:
            print("No fields created. Template creation cancelled.")
            return
        
        # Create the template
        print("\nCreating template in database...")
        template_id, message = create_enhanced_template(name, description, category, fields)
        
        if template_id:
            print(f"✓ Template created successfully with ID: {template_id}")
            self.print_template_summary(name, fields)
        else:
            print(f"✗ Failed to create template: {message}")

    def create_field_interactive(self, existing_fields: List[Dict]) -> Dict:
        """Create a field through interactive prompts."""
        field_id = self.get_input("Field ID (unique)", required=True)
        
        # Check for duplicate field IDs
        if any(f['field_id'] == field_id for f in existing_fields):
            print(f"Error: Field ID '{field_id}' already exists!")
            return {}
        
        field_name = self.get_input("Field Display Name", required=True)
        
        # Choose field type
        print("\nAvailable field types:")
        for i, (key, label) in enumerate(self.field_types.items(), 1):
            print(f"  {i:2d}. {label} ({key})")
        
        while True:
            try:
                choice = int(input("\nSelect field type (number): "))
                if 1 <= choice <= len(self.field_types):
                    field_type = list(self.field_types.keys())[choice - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        print(f"Selected: {self.field_types[field_type]}")
        
        # Basic field properties
        is_required = input("Is this field required? (y/n) [n]: ").strip().lower() in ['y', 'yes']
        
        # Create field configuration based on type
        field_config = self.configure_field_type(field_type, existing_fields)
        
        # Validation rules
        validation_rules = self.configure_validation_rules(field_type)
        
        # Dependencies
        dependencies = self.configure_dependencies(existing_fields)
        
        field = {
            'field_id': field_id,
            'field_name': field_name,
            'field_type': field_type,
            'is_required': 1 if is_required else 0,
            'config': field_config,
            'validation_rules': validation_rules,
            'dependencies': dependencies
        }
        
        return field

    def configure_field_type(self, field_type: str, existing_fields: List[Dict]) -> Dict:
        """Configure specific settings for each field type."""
        config = {}
        
        if field_type == 'text':
            config['placeholder'] = self.get_input("Placeholder text")
            config['maxLength'] = self.get_number_input("Maximum length", 255)
            config['pattern'] = self.get_input("Validation pattern (regex)")
            
        elif field_type == 'textarea':
            config['placeholder'] = self.get_input("Placeholder text")
            config['rows'] = self.get_number_input("Number of rows", 3)
            config['maxLength'] = self.get_number_input("Maximum length", 1000)
            
        elif field_type == 'number':
            config['min'] = self.get_number_input("Minimum value")
            config['max'] = self.get_number_input("Maximum value")
            config['step'] = self.get_number_input("Step increment", 1)
            
        elif field_type in ['select', 'multiselect', 'radio', 'checkbox']:
            config['options'] = self.configure_options()
            config['allowOther'] = input("Allow 'Other' option? (y/n) [n]: ").strip().lower() in ['y', 'yes']
            
        elif field_type == 'autocomplete':
            config['options'] = self.configure_options()
            config['minLength'] = self.get_number_input("Minimum characters to search", 1)
            config['maxResults'] = self.get_number_input("Maximum results", 10)
            config['allowCustom'] = input("Allow custom values? (y/n) [y]: ").strip().lower() not in ['n', 'no']
            
        elif field_type == 'data_table_lookup':
            config.update(self.configure_data_table_lookup())
            
        elif field_type == 'dependent_field':
            config.update(self.configure_dependent_field(existing_fields))
            
        elif field_type == 'file_upload':
            config['maxSize'] = self.get_number_input("Max file size (MB)", 10)
            config['allowedTypes'] = self.get_input("Allowed file types (comma-separated)", "pdf,doc,docx,txt").split(',')
            config['multiple'] = input("Allow multiple files? (y/n) [n]: ").strip().lower() in ['y', 'yes']
            
        elif field_type == 'rating':
            config['maxRating'] = self.get_number_input("Maximum rating", 5)
            config['allowHalf'] = input("Allow half ratings? (y/n) [n]: ").strip().lower() in ['y', 'yes']
            
        return config

    def configure_options(self) -> List[Dict]:
        """Configure options for select/radio/checkbox fields."""
        options = []
        print("\nEnter options (press Enter with empty value to finish):")
        
        option_counter = 1
        while True:
            value = input(f"Option {option_counter} value: ").strip()
            if not value:
                break
            
            label = input(f"Option {option_counter} label [{value}]: ").strip() or value
            
            options.append({
                'value': value,
                'label': label
            })
            
            option_counter += 1
        
        return options

    def configure_data_table_lookup(self) -> Dict:
        """Configure data table lookup settings."""
        config = {}
        
        # Get available data tables
        tables, msg = get_data_tables_list()
        
        if not tables:
            print("No data tables available. Creating a basic lookup configuration.")
            config['dataTable'] = self.get_input("Data table name", required=True)
            config['displayField'] = self.get_input("Display field", "name")
            config['valueField'] = self.get_input("Value field", "id")
        else:
            print("\nAvailable data tables:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table['display_name']} ({table['table_name']}) - {table.get('record_count', 0)} records")
            
            while True:
                try:
                    choice = int(input("\nSelect data table (number): "))
                    if 1 <= choice <= len(tables):
                        selected_table = tables[choice - 1]
                        config['dataTableId'] = selected_table['id']
                        config['dataTable'] = selected_table['table_name']
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        
        config['searchable'] = input("Enable search? (y/n) [y]: ").strip().lower() not in ['n', 'no']
        config['multiSelect'] = input("Allow multiple selections? (y/n) [n]: ").strip().lower() in ['y', 'yes']
        config['minSearchLength'] = self.get_number_input("Minimum search length", 2)
        config['maxResults'] = self.get_number_input("Maximum results", 10)
        
        return config

    def configure_dependent_field(self, existing_fields: List[Dict]) -> Dict:
        """Configure dependent field settings."""
        config = {}
        
        if not existing_fields:
            print("No existing fields to depend on!")
            return config
        
        print("\nAvailable fields to depend on:")
        for i, field in enumerate(existing_fields, 1):
            print(f"  {i}. {field['field_name']} ({field['field_id']})")
        
        while True:
            try:
                choice = int(input("\nSelect parent field (number): "))
                if 1 <= choice <= len(existing_fields):
                    parent_field = existing_fields[choice - 1]
                    config['dependsOn'] = parent_field['field_id']
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Configure options mapping
        print(f"\nConfiguring options based on '{parent_field['field_name']}' values:")
        options_map = {}
        
        # If parent field has options, use them
        if 'options' in parent_field.get('config', {}):
            for option in parent_field['config']['options']:
                parent_value = option['value']
                print(f"\nWhen '{parent_field['field_name']}' = '{option['label']}':")
                child_options = self.configure_options()
                options_map[parent_value] = child_options
        else:
            print("Manual configuration (enter parent values and corresponding options):")
            while True:
                parent_value = input("Parent field value (empty to finish): ").strip()
                if not parent_value:
                    break
                
                print(f"Options when parent = '{parent_value}':")
                child_options = self.configure_options()
                options_map[parent_value] = child_options
        
        config['optionsMap'] = options_map
        
        return config

    def configure_validation_rules(self, field_type: str) -> Dict:
        """Configure validation rules for a field."""
        rules = {}
        
        print(f"\nConfiguring validation rules for {field_type} field:")
        
        if field_type in ['text', 'textarea']:
            if input("Add minimum length rule? (y/n) [n]: ").strip().lower() in ['y', 'yes']:
                rules['minLength'] = self.get_number_input("Minimum length", 1)
            
            if input("Add maximum length rule? (y/n) [n]: ").strip().lower() in ['y', 'yes']:
                rules['maxLength'] = self.get_number_input("Maximum length", 255)
            
            if input("Add pattern validation? (y/n) [n]: ").strip().lower() in ['y', 'yes']:
                rules['pattern'] = self.get_input("Regular expression pattern")
                rules['patternMessage'] = self.get_input("Pattern validation message")
        
        elif field_type == 'number':
            if input("Add minimum value rule? (y/n) [n]: ").strip().lower() in ['y', 'yes']:
                rules['min'] = self.get_number_input("Minimum value")
            
            if input("Add maximum value rule? (y/n) [n]: ").strip().lower() in ['y', 'yes']:
                rules['max'] = self.get_number_input("Maximum value")
        
        elif field_type == 'email':
            rules['emailFormat'] = True
        
        # Custom validation message
        if rules:
            custom_message = self.get_input("Custom validation message (optional)")
            if custom_message:
                rules['message'] = custom_message
        
        return rules

    def configure_dependencies(self, existing_fields: List[Dict]) -> List[Dict]:
        """Configure field dependencies."""
        dependencies = []
        
        if not existing_fields:
            return dependencies
        
        if input("\nAdd conditional logic? (y/n) [n]: ").strip().lower() not in ['y', 'yes']:
            return dependencies
        
        print("\nConfiguring conditional logic:")
        
        while True:
            print("\nAvailable parent fields:")
            for i, field in enumerate(existing_fields, 1):
                print(f"  {i}. {field['field_name']} ({field['field_id']})")
            
            try:
                choice = int(input("\nSelect parent field (0 to finish): "))
                if choice == 0:
                    break
                
                if 1 <= choice <= len(existing_fields):
                    parent_field = existing_fields[choice - 1]
                    
                    # Configure condition
                    print("\nCondition types:")
                    for i, (key, label) in enumerate(self.condition_types.items(), 1):
                        print(f"  {i}. {label}")
                    
                    cond_choice = int(input("Select condition type: "))
                    condition_type = list(self.condition_types.keys())[cond_choice - 1]
                    
                    condition_value = None
                    if condition_type not in ['is_empty', 'is_not_empty']:
                        condition_value = self.get_input("Condition value")
                    
                    # Configure action
                    print("\nAction types:")
                    for i, (key, label) in enumerate(self.action_types.items(), 1):
                        print(f"  {i}. {label}")
                    
                    action_choice = int(input("Select action type: "))
                    action_type = list(self.action_types.keys())[action_choice - 1]
                    
                    action_config = {}
                    if action_type == 'set_value':
                        action_config['value'] = self.get_input("Value to set")
                    
                    dependency = {
                        'parent_field_id': parent_field['field_id'],
                        'condition_type': condition_type,
                        'condition_value': condition_value,
                        'action_type': action_type,
                        'action_config': action_config
                    }
                    
                    dependencies.append(dependency)
                    
                    if input("Add another dependency? (y/n) [n]: ").strip().lower() not in ['y', 'yes']:
                        break
                
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")
        
        return dependencies

    def create_sample_templates(self):
        """Create comprehensive sample templates."""
        print("\nCreating sample enhanced templates...")
        
        # IT Support Ticket Template
        it_fields = [
            {
                'field_id': 'requestor_name',
                'field_name': 'Requestor Name',
                'field_type': 'text',
                'is_required': 1,
                'config': {'placeholder': 'Enter full name'},
                'validation_rules': {'minLength': 2},
                'dependencies': []
            },
            {
                'field_id': 'department',
                'field_name': 'Department',
                'field_type': 'data_table_lookup',
                'is_required': 1,
                'config': {
                    'dataTable': 'departments',
                    'searchable': True,
                    'multiSelect': False
                },
                'validation_rules': {},
                'dependencies': []
            },
            {
                'field_id': 'issue_category',
                'field_name': 'Issue Category',
                'field_type': 'select',
                'is_required': 1,
                'config': {
                    'options': [
                        {'value': 'HW', 'label': 'Hardware'},
                        {'value': 'SW', 'label': 'Software'},
                        {'value': 'NET', 'label': 'Network'},
                        {'value': 'ACC', 'label': 'Account Access'}
                    ]
                },
                'validation_rules': {},
                'dependencies': []
            },
            {
                'field_id': 'issue_subcategory',
                'field_name': 'Issue Subcategory',
                'field_type': 'dependent_field',
                'is_required': 1,
                'config': {
                    'dependsOn': 'issue_category',
                    'optionsMap': {
                        'HW': [
                            {'value': 'laptop', 'label': 'Laptop Issues'},
                            {'value': 'desktop', 'label': 'Desktop Issues'},
                            {'value': 'printer', 'label': 'Printer Issues'}
                        ],
                        'SW': [
                            {'value': 'os', 'label': 'Operating System'},
                            {'value': 'app', 'label': 'Application Software'},
                            {'value': 'browser', 'label': 'Web Browser'}
                        ],
                        'NET': [
                            {'value': 'wifi', 'label': 'WiFi Connection'},
                            {'value': 'ethernet', 'label': 'Ethernet Connection'},
                            {'value': 'vpn', 'label': 'VPN Access'}
                        ],
                        'ACC': [
                            {'value': 'password', 'label': 'Password Reset'},
                            {'value': 'permissions', 'label': 'Access Permissions'},
                            {'value': 'new_user', 'label': 'New User Setup'}
                        ]
                    }
                },
                'validation_rules': {},
                'dependencies': []
            },
            {
                'field_id': 'priority',
                'field_name': 'Priority',
                'field_type': 'radio',
                'is_required': 1,
                'config': {
                    'options': [
                        {'value': 'low', 'label': 'Low - Can wait a few days'},
                        {'value': 'medium', 'label': 'Medium - Needed this week'},
                        {'value': 'high', 'label': 'High - Needed today'},
                        {'value': 'urgent', 'label': 'Urgent - Blocking work'}
                    ]
                },
                'validation_rules': {},
                'dependencies': []
            },
            {
                'field_id': 'description',
                'field_name': 'Problem Description',
                'field_type': 'textarea',
                'is_required': 1,
                'config': {
                    'placeholder': 'Please describe the issue in detail...',
                    'rows': 5
                },
                'validation_rules': {'minLength': 10},
                'dependencies': []
            },
            {
                'field_id': 'asset_tag',
                'field_name': 'Asset Tag',
                'field_type': 'text',
                'is_required': 0,
                'config': {
                    'placeholder': 'Asset tag number (if applicable)'
                },
                'validation_rules': {},
                'dependencies': [
                    {
                        'parent_field_id': 'issue_category',
                        'condition_type': 'equals',
                        'condition_value': 'HW',
                        'action_type': 'require',
                        'action_config': {}
                    }
                ]
            },
            {
                'field_id': 'screenshots',
                'field_name': 'Screenshots',
                'field_type': 'file_upload',
                'is_required': 0,
                'config': {
                    'maxSize': 5,
                    'allowedTypes': ['jpg', 'jpeg', 'png', 'gif'],
                    'multiple': True
                },
                'validation_rules': {},
                'dependencies': []
            }
        ]
        
        # Create IT Support template
        template_id, message = create_enhanced_template(
            "Enhanced IT Support Ticket",
            "Comprehensive IT support ticket with dependent fields and data table lookups",
            "IT Support",
            it_fields
        )
        
        if template_id:
            print(f"✓ Created IT Support template with ID: {template_id}")
        else:
            print(f"✗ Failed to create IT Support template: {message}")

    def create_data_management_tool(self):
        """Tool for managing data tables."""
        print("\n" + "="*50)
        print("         DATA TABLE MANAGEMENT")
        print("="*50)
        
        while True:
            print("\n1. View existing data tables")
            print("2. Create new data table")
            print("3. Add records to data table")
            print("4. Search data table")
            print("5. Back to main menu")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self.view_data_tables()
            elif choice == '2':
                self.create_data_table_interactive()
            elif choice == '3':
                self.add_data_records_to_existing_table()
            elif choice == '4':
                self.search_existing_data_table()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def view_data_tables(self):
        """View all existing data tables."""
        tables, message = get_data_tables_list()
        
        if not tables:
            print("No data tables found.")
            return
        
        print(f"\nFound {len(tables)} data tables:")
        print("-" * 60)
        
        for table in tables:
            print(f"Name: {table['display_name']}")
            print(f"Table ID: {table['table_name']}")
            print(f"Records: {table.get('record_count', 0)}")
            print(f"Columns: {table.get('columns', 'N/A')}")
            print("-" * 40)

    def create_data_table_interactive(self):
        """Create a data table interactively."""
        print("\nCreating new data table...")
        
        table_name = self.get_input("Table name (no spaces)", required=True).replace(' ', '_').lower()
        display_name = self.get_input("Display name", required=True)
        description = self.get_input("Description")
        
        print("\nDefining columns:")
        columns = []
        col_counter = 1
        
        while True:
            print(f"\n--- Column {col_counter} ---")
            col_name = input("Column name (empty to finish): ").strip()
            if not col_name:
                break
            
            col_display = input(f"Display name [{col_name}]: ").strip() or col_name
            
            print("Data types: 1=text, 2=number, 3=date, 4=boolean")
            data_type_choice = input("Data type [1]: ").strip() or "1"
            data_types = {'1': 'text', '2': 'number', '3': 'date', '4': 'boolean'}
            data_type = data_types.get(data_type_choice, 'text')
            
            is_key = input("Is this a key field? (y/n) [n]: ").strip().lower() in ['y', 'yes']
            is_display = input("Is this the display field? (y/n) [n]: ").strip().lower() in ['y', 'yes']
            is_searchable = input("Is this field searchable? (y/n) [y]: ").strip().lower() not in ['n', 'no']
            
            column = {
                'column_name': col_name,
                'display_name': col_display,
                'data_type': data_type,
                'is_key_field': 1 if is_key else 0,
                'is_display_field': 1 if is_display else 0,
                'is_searchable': 1 if is_searchable else 0
            }
            
            columns.append(column)
            col_counter += 1
        
        if not columns:
            print("No columns defined. Table creation cancelled.")
            return
        
        # Create the table
        table_id, message = create_data_table(table_name, display_name, description, columns)
        
        if table_id:
            print(f"✓ Data table created successfully with ID: {table_id}")
            
            # Ask if they want to add initial data
            if input("Add initial data? (y/n) [y]: ").strip().lower() not in ['n', 'no']:
                self.add_records_to_table(table_id, columns)
        else:
            print(f"✗ Failed to create data table: {message}")

    def add_records_to_table(self, table_id: int, columns: List[Dict]):
        """Add records to a specific table."""
        print("\nAdding records to the table...")
        
        record_counter = 1
        while True:
            print(f"\n--- Record {record_counter} ---")
            record_data = {}
            
            for column in columns:
                value = input(f"{column['display_name']}: ").strip()
                if value:
                    # Convert value based on data type
                    if column['data_type'] == 'number':
                        try:
                            value = float(value) if '.' in value else int(value)
                        except ValueError:
                            print(f"Invalid number, using as text: {value}")
                    elif column['data_type'] == 'boolean':
                        value = value.lower() in ['true', 'yes', '1', 'y']
                
                record_data[column['column_name']] = value
            
            if record_data:
                record_id, message = add_data_table_record(table_id, record_data)
                if record_id:
                    print(f"✓ Record {record_counter} added successfully")
                else:
                    print(f"✗ Failed to add record: {message}")
                
                record_counter += 1
            
            if input("Add another record? (y/n) [y]: ").strip().lower() in ['n', 'no']:
                break

    def add_data_records_to_existing_table(self):
        """Add records to an existing data table."""
        tables, message = get_data_tables_list()
        
        if not tables:
            print("No data tables found.")
            return
        
        print("\nAvailable data tables:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table['display_name']} ({table['table_name']})")
        
        try:
            choice = int(input("\nSelect table (number): "))
            if 1 <= choice <= len(tables):
                selected_table = tables[choice - 1]
                print(f"Adding records to: {selected_table['display_name']}")
                
                # Get table columns (this would need to be implemented in enhanced_db_utils)
                # For now, ask user to input field names
                print("Enter field names and values for new records:")
                
                record_counter = 1
                while True:
                    print(f"\n--- Record {record_counter} ---")
                    record_data = {}
                    
                    while True:
                        field_name = input("Field name (empty to finish record): ").strip()
                        if not field_name:
                            break
                        
                        field_value = input(f"{field_name}: ").strip()
                        record_data[field_name] = field_value
                    
                    if record_data:
                        record_id, message = add_data_table_record(selected_table['id'], record_data)
                        if record_id:
                            print(f"✓ Record {record_counter} added successfully")
                        else:
                            print(f"✗ Failed to add record: {message}")
                        
                        record_counter += 1
                    
                    if input("Add another record? (y/n) [y]: ").strip().lower() in ['n', 'no']:
                        break
            
        except (ValueError, IndexError):
            print("Invalid choice.")

    def search_existing_data_table(self):
        """Search records in an existing data table."""
        tables, message = get_data_tables_list()
        
        if not tables:
            print("No data tables found.")
            return
        
        print("\nAvailable data tables:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table['display_name']} ({table['table_name']}) - {table.get('record_count', 0)} records")
        
        try:
            choice = int(input("\nSelect table to search (number): "))
            if 1 <= choice <= len(tables):
                selected_table = tables[choice - 1]
                
                search_term = input(f"Search term for {selected_table['display_name']} (empty for all): ").strip()
                limit = self.get_number_input("Maximum results", 10)
                
                results, message = search_data_table(selected_table['id'], search_term, limit)
                
                if results:
                    print(f"\nFound {len(results)} results:")
                    print("-" * 50)
                    for i, result in enumerate(results, 1):
                        print(f"{i}. {result['display']}")
                        print(f"   Data: {json.dumps(result['data'], indent=2)}")
                        print("-" * 30)
                else:
                    print(f"No results found. {message}")
            
        except (ValueError, IndexError):
            print("Invalid choice.")

    def get_input(self, prompt: str, default: str = "", required: bool = False) -> str:
        """Get user input with optional default and required validation."""
        while True:
            if default:
                value = input(f"{prompt} [{default}]: ").strip()
                if not value:
                    value = default
            else:
                value = input(f"{prompt}: ").strip()
            
            if required and not value:
                print("This field is required!")
                continue
            
            return value

    def get_number_input(self, prompt: str, default: int = 0) -> int:
        """Get numeric input with optional default."""
        while True:
            if default != 0:
                value = input(f"{prompt} [{default}]: ").strip()
                if not value:
                    return default
            else:
                value = input(f"{prompt}: ").strip()
                if not value:
                    return 0
            
            try:
                return int(value)
            except ValueError:
                print("Please enter a valid number.")

    def print_template_summary(self, name: str, fields: List[Dict]):
        """Print a summary of the created template."""
        print(f"\n{'='*60}")
        print(f"TEMPLATE SUMMARY: {name}")
        print(f"{'='*60}")
        
        for i, field in enumerate(fields, 1):
            print(f"\n{i}. {field['field_name']} ({field['field_id']})")
            print(f"   Type: {self.field_types.get(field['field_type'], field['field_type'])}")
            print(f"   Required: {'Yes' if field['is_required'] else 'No'}")
            
            if field.get('dependencies'):
                print(f"   Dependencies: {len(field['dependencies'])} conditional rules")
            
            if field['field_type'] in ['select', 'radio'] and 'options' in field.get('config', {}):
                options = field['config']['options']
                print(f"   Options: {', '.join([opt['label'] for opt in options[:3]])}")
                if len(options) > 3:
                    print(f"            ... and {len(options) - 3} more")

def main():
    """Main function for the interactive template builder."""
    builder = InteractiveTemplateBuilder()
    
    while True:
        print("\n" + "="*60)
        print("       ENHANCED CASE MANAGEMENT SYSTEM")
        print("         Interactive Template Builder")
        print("="*60)
        print("1. Create custom template (interactive)")
        print("2. Create sample templates")
        print("3. Manage data tables")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            builder.create_template_interactive()
        elif choice == '2':
            builder.create_sample_templates()
        elif choice == '3':
            builder.create_data_management_tool()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    # Initialize the enhanced database first
    from enhanced_database_init import init_enhanced_database, create_sample_data_tables, create_form_builder_configs
    
    print("Initializing enhanced database...")
    if init_enhanced_database():
        create_sample_data_tables()
        create_form_builder_configs()
        main()
    else:
        print("Failed to initialize database. Please check the error messages above.")
