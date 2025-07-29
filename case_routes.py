from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
from datetime import datetime

try:
    from db_utils import (
        create_case_template, get_all_case_templates, get_case_template,
        update_case_template, delete_case_template,
        create_case, get_all_cases, get_case, update_case, delete_case,
        get_custom_table_related_data
    )
except Exception as e:
    print(f"Error importing db_utils: {e}")

cases_bp = Blueprint('cases', __name__)


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@cases_bp.route('/cases')
@admin_required
def case_list():
    cases = get_all_cases()
    templates = {t['id']: t['name'] for t in get_all_case_templates()}
    return render_template('cases.html', cases=cases, templates=templates)


@cases_bp.route('/cases/new', methods=['GET', 'POST'])
@admin_required
def new_case():
    templates = get_all_case_templates()
    if not templates:
        flash('No case templates available. Create one first.', 'warning')
        return redirect(url_for('cases.manage_templates'))

    if request.method == 'POST':
        template_id = int(request.form.get('template_id'))
        data = {}
        template = get_case_template(template_id)
        if template:
            fields = json.loads(template['fields_json'])
            for field in fields:
                fid = field.get('id')
                if not fid:
                    continue
                value = request.form.get(fid)
                data[fid] = value
            case_id = create_case(template_id, json.dumps(data), session.get('username','admin'))
            if case_id:
                flash('Case created', 'success')
                return redirect(url_for('cases.case_list'))
            flash('Failed to create case', 'danger')
    return render_template('case_form.html', templates=templates)


@cases_bp.route('/cases/<int:case_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_case(case_id):
    case = get_case(case_id)
    if not case:
        return redirect(url_for('cases.case_list'))
    template = get_case_template(case['template_id'])
    if not template:
        flash('Template not found', 'danger')
        return redirect(url_for('cases.case_list'))
    fields = json.loads(template['fields_json'])
    data = json.loads(case['data_json']) if case['data_json'] else {}
    if request.method == 'POST':
        for field in fields:
            fid = field.get('id')
            if fid:
                data[fid] = request.form.get(fid)
        if update_case(case_id, json.dumps(data)):
            flash('Case updated', 'success')
            return redirect(url_for('cases.case_list'))
        flash('Failed to update case', 'danger')
    return render_template('case_form.html', case=case, template=template, fields=fields, data=data)


@cases_bp.route('/cases/<int:case_id>/delete', methods=['POST'])
@admin_required
def delete_case_route(case_id):
    delete_case(case_id)
    return redirect(url_for('cases.case_list'))


@cases_bp.route('/case-templates', methods=['GET', 'POST'])
@admin_required
def manage_templates():
    templates = get_all_case_templates()
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        description = request.form.get('description','').strip()
        fields_json = request.form.get('fields_json','[]')
        if name and fields_json:
            if create_case_template(name, description, fields_json, session.get('username','admin')):
                flash('Template created', 'success')
                return redirect(url_for('cases.manage_templates'))
            flash('Failed to create template','danger')
    return render_template('case_templates.html', templates=templates)


@cases_bp.route('/case-templates/<int:template_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_template(template_id):
    template = get_case_template(template_id)
    if not template:
        return redirect(url_for('cases.manage_templates'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        description = request.form.get('description','').strip()
        fields_json = request.form.get('fields_json','[]')
        if update_case_template(template_id, name, description, fields_json):
            flash('Template updated', 'success')
            return redirect(url_for('cases.manage_templates'))
        flash('Failed to update template','danger')
    return render_template('case_templates.html', templates=[template], edit=True)


@cases_bp.route('/case-templates/<int:template_id>/delete', methods=['POST'])
@admin_required
def delete_template(template_id):
    delete_case_template(template_id)
    return redirect(url_for('cases.manage_templates'))


# API endpoint for dependent fields
@cases_bp.route('/api/case/related-data/<table_name>', methods=['POST'])
@admin_required
def case_related_data(table_name):
    payload = request.json or {}
    column = payload.get('match_column')
    value = payload.get('value')
    return_columns = payload.get('return_columns', [])
    data = get_custom_table_related_data(table_name, column, value, return_columns)
    if data:
        return {'success': True, 'data': data}
    return {'success': False}
