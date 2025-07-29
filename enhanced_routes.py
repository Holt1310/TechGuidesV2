"""
Enhanced case management routes for the Flask application.
Handles template creation, case management, and data table operations.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import json
from enhanced_db_utils import (
    create_enhanced_template, get_template_with_fields, create_enhanced_case,
    update_case_field, get_cases_list, create_data_table, add_data_table_record,
    search_data_table, get_data_tables_list, validate_field_dependencies,
    get_field_options_for_dependency, get_templates_list
)

enhanced_bp = Blueprint('enhanced', __name__, url_prefix='/enhanced')

@enhanced_bp.route('/template-builder')
def template_builder():
    """Show the enhanced template builder interface."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('enhanced_template_editor.html')

@enhanced_bp.route('/templates')
def templates_list():
    """Show list of enhanced templates."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get templates from database
    templates = get_templates_list()
    
    return render_template('enhanced_templates_list.html', templates=templates)

@enhanced_bp.route('/cases')
def cases_list():
    """Show list of enhanced cases."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameters
    status = request.args.get('status')
    assigned_to = request.args.get('assigned_to')
    template_id = request.args.get('template_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    offset = (page - 1) * per_page
    cases, message = get_cases_list(status, assigned_to, template_id, per_page, offset)
    templates = get_templates_list()
    
    return render_template('enhanced_cases_list.html', 
                         cases=cases, 
                         templates=templates,
                         current_page=page,
                         per_page=per_page)

@enhanced_bp.route('/case/<int:case_id>')
def view_case(case_id):
    """View a specific case."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get case details
    # This would need to be implemented
    case_data = {}
    
    return render_template('enhanced_case_view.html', case=case_data)

@enhanced_bp.route('/case/new/<int:template_id>')
def new_case(template_id):
    """Create a new case from a template."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    template_data, message = get_template_with_fields(template_id)
    
    if not template_data:
        return jsonify({'error': message}), 404
    
    return render_template('enhanced_case_form.html', template=template_data)

@enhanced_bp.route('/data-tables')
def data_tables():
    """Manage data tables."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    tables, message = get_data_tables_list()
    
    return render_template('enhanced_data_tables.html', tables=tables)

# API Routes

@enhanced_bp.route('/api/templates/create', methods=['POST'])
def api_create_template():
    """API endpoint to create a new template."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('fields'):
            return jsonify({'success': False, 'message': 'Name and fields are required'}), 400
        
        template_id, message = create_enhanced_template(
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'General'),
            fields=data['fields'],
            created_by=session['username']
        )
        
        if template_id:
            return jsonify({
                'success': True,
                'message': 'Template created successfully',
                'template_id': template_id
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@enhanced_bp.route('/api/templates/<int:template_id>')
def api_get_template(template_id):
    """API endpoint to get template details."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    template_data, message = get_template_with_fields(template_id)
    
    if template_data:
        return jsonify({'success': True, 'template': template_data})
    else:
        return jsonify({'success': False, 'message': message}), 404

@enhanced_bp.route('/api/cases/create', methods=['POST'])
def api_create_case():
    """API endpoint to create a new case."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        template_id = data.get('template_id')
        title = data.get('title')
        description = data.get('description', '')
        case_data = data.get('case_data', {})
        
        if not template_id or not title:
            return jsonify({'success': False, 'message': 'Template ID and title are required'}), 400
        
        # Validate field dependencies
        is_valid, validation_message = validate_field_dependencies(template_id, case_data)
        
        if not is_valid:
            return jsonify({'success': False, 'message': f'Validation failed: {validation_message}'}), 400
        
        case_id, case_number, message = create_enhanced_case(
            template_id=template_id,
            title=title,
            description=description,
            case_data=case_data,
            created_by=session['username'],
            status=data.get('status', 'draft'),
            priority=data.get('priority', 'medium'),
            assigned_to=data.get('assigned_to'),
            tags=data.get('tags', ''),
            due_date=data.get('due_date')
        )
        
        if case_id:
            return jsonify({
                'success': True,
                'message': 'Case created successfully',
                'case_id': case_id,
                'case_number': case_number
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@enhanced_bp.route('/api/cases/<int:case_id>/update-field', methods=['POST'])
def api_update_case_field(case_id):
    """API endpoint to update a specific field in a case."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        field_name = data.get('field_name')
        old_value = data.get('old_value')
        new_value = data.get('new_value')
        
        if not field_name:
            return jsonify({'success': False, 'message': 'Field name is required'}), 400
        
        success, message = update_case_field(
            case_id=case_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            updated_by=session['username']
        )
        
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@enhanced_bp.route('/api/data-tables')
def api_get_data_tables():
    """API endpoint to get list of data tables."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    tables, message = get_data_tables_list()
    
    return jsonify({
        'success': True,
        'tables': tables,
        'message': message
    })

@enhanced_bp.route('/api/data-tables/create', methods=['POST'])
def api_create_data_table():
    """API endpoint to create a new data table."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        table_name = data.get('table_name')
        display_name = data.get('display_name')
        description = data.get('description', '')
        columns = data.get('columns', [])
        
        if not table_name or not display_name or not columns:
            return jsonify({'success': False, 'message': 'Table name, display name, and columns are required'}), 400
        
        table_id, message = create_data_table(
            table_name=table_name,
            display_name=display_name,
            description=description,
            columns=columns,
            created_by=session['username']
        )
        
        if table_id:
            return jsonify({
                'success': True,
                'message': 'Data table created successfully',
                'table_id': table_id
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@enhanced_bp.route('/api/data-tables/<int:table_id>/records', methods=['POST'])
def api_add_data_record(table_id):
    """API endpoint to add a record to a data table."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        record_data = data.get('record_data', {})
        
        if not record_data:
            return jsonify({'success': False, 'message': 'Record data is required'}), 400
        
        record_id, message = add_data_table_record(
            table_id=table_id,
            record_data=record_data,
            created_by=session['username']
        )
        
        if record_id:
            return jsonify({
                'success': True,
                'message': 'Record added successfully',
                'record_id': record_id
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@enhanced_bp.route('/api/data-tables/<int:table_id>/search')
def api_search_data_table(table_id):
    """API endpoint to search records in a data table."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    search_term = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    results, message = search_data_table(table_id, search_term, limit)
    
    return jsonify({
        'success': True,
        'results': results,
        'message': message
    })

@enhanced_bp.route('/api/fields/<int:field_id>/options')
def api_get_field_options(field_id):
    """API endpoint to get dynamic options for a dependent field."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    parent_value = request.args.get('parent_value', '')
    
    options, message = get_field_options_for_dependency(field_id, parent_value)
    
    return jsonify({
        'success': True,
        'options': options,
        'message': message
    })

@enhanced_bp.route('/api/templates/<int:template_id>/validate', methods=['POST'])
def api_validate_template_data(template_id):
    """API endpoint to validate case data against template rules."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        case_data = data.get('case_data', {})
        
        is_valid, validation_result = validate_field_dependencies(template_id, case_data)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'validation_result': validation_result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
