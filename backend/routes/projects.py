from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, Project, Task, User
from schemas import project_schema, projects_schema, task_schema, tasks_schema
from sqlalchemy.exc import IntegrityError
from datetime import date

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all projects with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')

        query = Project.query
        if search:
            query = query.filter(Project.name.ilike(f'%{search}%'))
        if status:
            query = query.filter(Project.status == status)
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'success': True,
            'data': projects_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        errors = project_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
        
        new_project = Project(**data)
        db.session.add(new_project)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Project created successfully',
            'data': project_schema.dump(new_project)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<uuid:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get a single project by ID"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'data': project_schema.dump(project)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<uuid:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update an existing project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        for field, value in data.items():
            if hasattr(project, field):
                setattr(project, field, value)
                
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Project updated successfully',
            'data': project_schema.dump(project)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<uuid:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/stats', methods=['GET'])
@jwt_required()
def get_project_stats():
    """Get key project metrics for the dashboard"""
    try:
        active_statuses = ['Planning', 'In Progress', 'Review']
        active_projects_count = Project.query.filter(Project.status.in_(active_statuses)).count()
        
        at_risk_count = Project.query.filter(
            Project.status.in_(active_statuses),
            Project.end_date < date.today()
        ).count()
        
        on_track_count = active_projects_count - at_risk_count
        
        team_members_count = db.session.query(Task.assignee_id).distinct().count()

        return jsonify({
            'success': True,
            'data': {
                'active_projects': active_projects_count,
                'on_track': on_track_count,
                'at_risk': at_risk_count,
                'team_members': team_members_count
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Task Management Endpoints ---

@projects_bp.route('/projects/<uuid:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_project_tasks(project_id):
    """Get all tasks for a specific project"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'data': tasks_schema.dump(project.tasks)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<uuid:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    """Create a new task for a project"""
    try:
        Project.query.get_or_404(project_id) # Ensure project exists
        data = request.get_json()
        errors = task_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
        
        data['project_id'] = project_id
        new_task = Task(**data)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'data': task_schema.dump(new_task)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/tasks/<uuid:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update an existing task"""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        errors = task_schema.validate(data, partial=True)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
            
        for field, value in data.items():
            setattr(task, field, value)
            
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Task updated successfully',
            'data': task_schema.dump(task)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
