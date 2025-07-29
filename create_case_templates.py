#!/usr/bin/env python3
"""
Script to create sample case templates in the database.
This will help you get started with the case management system.
"""

import json
import sys
import os

# Add the parent directory to the path so we can import db_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_utils import create_case_template

def load_sample_templates():
    """Load sample templates from the JSON file."""
    try:
        with open('sample_case_templates.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: sample_case_templates.json not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def create_sample_templates():
    """Create all sample templates in the database."""
    templates_data = load_sample_templates()
    if not templates_data:
        return
    
    created_count = 0
    
    for template_key, template_info in templates_data.items():
        print(f"Creating template: {template_info['name']}")
        
        try:
            template_id, message = create_case_template(
                name=template_info['name'],
                description=template_info['description'],
                fields=template_info['fields'],
                rules=template_info.get('rules', []),
                created_by="admin"
            )
            
            if template_id:
                print(f"✓ Successfully created template '{template_info['name']}' with ID: {template_id}")
                created_count += 1
            else:
                print(f"✗ Failed to create template '{template_info['name']}': {message}")
                
        except Exception as e:
            print(f"✗ Error creating template '{template_info['name']}': {e}")
    
    print(f"\nCompleted! Created {created_count} templates.")

def create_single_template():
    """Create a single template interactively."""
    print("Creating a custom case template...")
    
    name = input("Template Name: ").strip()
    if not name:
        print("Template name is required!")
        return
    
    description = input("Description (optional): ").strip()
    
    print("\nDefining fields:")
    print("Available field types: text, textarea, select, radio, checkbox")
    print("Enter fields one by one. Press Enter with empty field name to finish.")
    
    fields = []
    field_count = 1
    
    while True:
        print(f"\n--- Field {field_count} ---")
        field_name = input("Field name (or Enter to finish): ").strip()
        if not field_name:
            break
            
        field_id = input("Field ID (unique identifier): ").strip()
        if not field_id:
            field_id = field_name.lower().replace(' ', '_')
            
        field_type = input("Field type [text]: ").strip() or "text"
        
        required_input = input("Required? (y/n) [n]: ").strip().lower()
        required = required_input in ['y', 'yes', '1', 'true']
        
        field = {
            "id": field_id,
            "name": field_name, 
            "type": field_type,
            "required": required
        }
        
        # Handle select/radio options
        if field_type in ['select', 'radio']:
            print("Enter options for this field:")
            options = []
            opt_count = 1
            while True:
                opt_value = input(f"Option {opt_count} value (or Enter to finish): ").strip()
                if not opt_value:
                    break
                opt_label = input(f"Option {opt_count} label: ").strip() or opt_value
                options.append({"value": opt_value, "label": opt_label})
                opt_count += 1
            field["options"] = options
        
        # Handle textarea rows
        if field_type == 'textarea':
            rows_input = input("Number of rows [3]: ").strip()
            try:
                rows = int(rows_input) if rows_input else 3
                field["rows"] = rows
            except ValueError:
                field["rows"] = 3
        
        fields.append(field)
        field_count += 1
    
    if not fields:
        print("No fields defined. Template not created.")
        return
    
    try:
        template_id, message = create_case_template(
            name=name,
            description=description,
            fields=fields,
            rules=[],
            created_by="admin"
        )
        
        if template_id:
            print(f"\n✓ Successfully created template '{name}' with ID: {template_id}")
            print(f"Fields JSON: {json.dumps(fields, indent=2)}")
        else:
            print(f"\n✗ Failed to create template: {message}")
            
    except Exception as e:
        print(f"\n✗ Error creating template: {e}")

def main():
    """Main function to handle user input."""
    print("Case Template Creator")
    print("===================")
    print("1. Create sample templates (Support Ticket, Incident Report, Change Request)")
    print("2. Create a custom template interactively")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == '1':
        create_sample_templates()
    elif choice == '2':
        create_single_template()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
