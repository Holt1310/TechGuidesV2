# Case Management System Guide

## Overview

Your TruckSoft website includes a comprehensive case management system that allows you to:
- Create reusable case templates
- File cases based on templates
- Track case status and data
- Automate case creation with Selenium

## Case Creation Process

### 1. Create Case Templates (Admin Only)

Case templates define the structure and fields for your cases. You need to be logged in as an admin to create templates.

#### Access Templates
- Navigate to **Case Templates** in the admin section
- Click **New Template** to create a new template

#### Template Structure

```json
{
  "name": "Template Name",
  "description": "Description of the template",
  "fields": [
    {
      "id": "unique_field_id",
      "name": "Field Display Name", 
      "type": "field_type",
      "required": true/false
    }
  ],
  "rules": []
}
```

#### Field Types

| Type | Description | Additional Properties |
|------|-------------|----------------------|
| `text` | Single line text input | - |
| `textarea` | Multi-line text input | `rows` (number) |
| `select` | Dropdown selection | `options` (array) |
| `radio` | Radio button selection | `options` (array) |
| `checkbox` | Checkbox input | - |

#### Option Format (for select/radio fields)
```json
"options": [
  {"value": "option_value", "label": "Display Label"},
  {"value": "another_value", "label": "Another Label"}
]
```

### 2. Create Cases

Once you have templates, any logged-in user can create cases:

#### Via Web Interface
1. Navigate to **Cases** page
2. Click **New Case**
3. Select a template (if multiple exist)
4. Fill in the form fields
5. Click **Save**

#### Via API/Automation
Use the Selenium automation scripts in `client_tools/` for automated case creation.

## Sample Templates

### Support Ticket Template
```json
{
  "name": "Support Ticket",
  "description": "General customer support ticket template",
  "fields": [
    {
      "id": "subject",
      "name": "Subject",
      "type": "text",
      "required": true
    },
    {
      "id": "customer_name", 
      "name": "Customer Name",
      "type": "text",
      "required": true
    },
    {
      "id": "priority",
      "name": "Priority",
      "type": "select",
      "required": true,
      "options": [
        {"value": "low", "label": "Low"},
        {"value": "medium", "label": "Medium"},
        {"value": "high", "label": "High"},
        {"value": "urgent", "label": "Urgent"}
      ]
    },
    {
      "id": "description",
      "name": "Description", 
      "type": "textarea",
      "required": true,
      "rows": 5
    }
  ]
}
```

### Incident Report Template
```json
{
  "name": "Incident Report",
  "description": "Template for reporting system incidents",
  "fields": [
    {
      "id": "incident_title",
      "name": "Incident Title",
      "type": "text",
      "required": true
    },
    {
      "id": "severity",
      "name": "Severity Level",
      "type": "select", 
      "required": true,
      "options": [
        {"value": "critical", "label": "Critical - System Down"},
        {"value": "high", "label": "High - Major Feature Broken"},
        {"value": "medium", "label": "Medium - Minor Feature Issue"},
        {"value": "low", "label": "Low - Cosmetic Issue"}
      ]
    },
    {
      "id": "incident_description",
      "name": "Incident Description",
      "type": "textarea",
      "required": true,
      "rows": 6
    }
  ]
}
```

## Creating Templates - Easy Method

I've created a helper script to make template creation easier:

### Using the Template Creator Script

1. **Run the script:**
   ```bash
   python create_case_templates.py
   ```

2. **Choose an option:**
   - Option 1: Create sample templates (Support Ticket, Incident Report, Change Request)
   - Option 2: Create a custom template interactively
   - Option 3: Exit

### Using the Web Interface

1. **Log in as admin**
2. **Navigate to Case Templates**
3. **Click "New Template"**
4. **Fill in the form:**
   - Template Name
   - Description
   - Fields JSON (copy from examples above)
   - Rules JSON (leave empty `[]` for now)

## Advanced Features

### Dependency Rules
You can create rules that automatically populate fields based on other field values:

```json
"rules": [
  {
    "source": "customer_id",
    "table": "customers", 
    "match_column": "id",
    "map": {
      "customer_name": "name",
      "customer_email": "email"
    }
  }
]
```

### Data Table Integration
Templates can integrate with custom data tables for dynamic field population.

### Selenium Automation
The system includes Selenium automation for creating cases in external systems:

1. **Configure:** Edit `client_tools/case_creator_config.json`
2. **Run:** `python client_tools/case_creator.py`

## Case Status Management

Cases have the following statuses:
- `open` (default)
- `in_progress` 
- `resolved`
- `closed`

## Database Structure

### Case Templates Table
- `id` - Unique identifier
- `name` - Template name
- `description` - Template description
- `fields_json` - JSON array of field definitions
- `rules_json` - JSON array of dependency rules
- `created_at`, `updated_at`, `created_by` - Metadata

### Cases Table
- `id` - Unique case identifier
- `template_id` - Reference to case template
- `case_data` - JSON object with field values
- `status` - Current case status
- `created_at`, `updated_at`, `created_by` - Metadata

## Best Practices

1. **Field IDs:** Use descriptive, unique field IDs (e.g., `customer_email`, not just `email`)
2. **Required Fields:** Mark essential fields as required
3. **Options:** Provide clear, meaningful option labels
4. **Validation:** Test templates before deploying to users
5. **Documentation:** Document template purpose and field meanings

## Troubleshooting

### Common Issues

1. **Template not appearing:** Ensure you're logged in as admin
2. **Field not saving:** Check JSON syntax in template definition
3. **Options not showing:** Verify option format is correct
4. **Automation failing:** Check Selenium configuration and driver path

### Getting Help

Check the application logs and database for error messages. The system provides detailed error reporting for template and case creation issues.
