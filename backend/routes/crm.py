from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, Lead, Deal, Customer
from schemas import lead_schema, leads_schema, deal_schema, deals_schema
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from utils.decorators import admin_required

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_leads():
    """Get all leads with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Lead.query
        if search:
            query = query.filter(
                db.or_(
                    Lead.name.ilike(f'%{search}%'),
                    Lead.email.ilike(f'%{search}%'),
                    Lead.company.ilike(f'%{search}%')
                )
            )
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'success': True,
            'data': leads_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_bp.route('/leads', methods=['POST'])
@admin_required()
def create_lead():
    """Create a new lead"""
    try:
        data = request.get_json()
        errors = lead_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400
        
        if Lead.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Lead with this email already exists'}), 400
            
        new_lead = Lead(**data)
        db.session.add(new_lead)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Lead created successfully',
            'data': lead_schema.dump(new_lead)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_bp.route('/deals', methods=['GET'])
@jwt_required()
def get_deals():
    """Get all deals for the sales pipeline"""
    try:
        deals = Deal.query.all()
        return jsonify({
            'success': True,
            'data': deals_schema.dump(deals)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_bp.route('/deals', methods=['POST'])
@admin_required()
def create_deal():
    """Create a new deal"""
    try:
        data = request.get_json()
        errors = deal_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': errors}), 400

        # Check if the customer exists
        if not Customer.query.get(data['customer_id']):
             return jsonify({'success': False, 'error': 'Customer not found'}), 404

        new_deal = Deal(**data)
        db.session.add(new_deal)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Deal created successfully',
            'data': deal_schema.dump(new_deal)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_bp.route('/deals/<uuid:deal_id>', methods=['PUT'])
@admin_required()
def update_deal(deal_id):
    """Update a deal's stage or other details"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        for field, value in data.items():
            if hasattr(deal, field):
                setattr(deal, field, value)
                
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Deal updated successfully',
            'data': deal_schema.dump(deal)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_bp.route('/crm/stats', methods=['GET'])
@jwt_required()
def get_crm_stats():
    """Get key CRM metrics for the dashboard"""
    try:
        total_leads = Lead.query.count()
       
        pipeline_value = db.session.query(func.sum(Deal.value)).filter(
            Deal.stage.in_(['Qualified', 'Proposal', 'Negotiation'])
        ).scalar() or 0
       
        current_quarter = (datetime.utcnow().month - 1) // 3 + 1
        start_month = 3 * current_quarter - 2
        start_of_quarter = datetime(datetime.utcnow().year, start_month, 1)
        
        revenue_this_quarter = db.session.query(func.sum(Deal.value)).filter(
            Deal.stage == 'Closed Won',
            Deal.close_date >= start_of_quarter
        ).scalar() or 0
       
        conversion_rate = "24.5%"

        return jsonify({
            'success': True,
            'data': {
                'total_leads': total_leads,
                'pipeline_value': float(pipeline_value),
                'revenue_this_quarter': float(revenue_this_quarter),
                'conversion_rate': conversion_rate
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_bp.route('/leads/<uuid:lead_id>/convert', methods=['POST'])
@admin_required()
def convert_lead(lead_id):
    """Converts a lead into a customer and a deal"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        if lead.status == 'Converted':
            return jsonify({'success': False, 'error': 'Lead has already been converted'}), 400
        
        data = request.get_json()
        deal_name = data.get('deal_name')
        deal_value = data.get('deal_value')
        if not all([deal_name, deal_value]):
            return jsonify({'success': False, 'error': 'deal_name and deal_value are required'}), 400

        # Create a new customer from the lead
        new_customer = Customer(
            name=lead.name,
            email=lead.email,
            company=lead.company,
            status='Active'
        )
        db.session.add(new_customer)
        db.session.flush() # To get the new_customer.id

        # Create a new deal linked to the new customer
        new_deal = Deal(
            name=deal_name,
            customer_id=new_customer.id,
            value=deal_value,
            stage='Qualified' # Initial stage after conversion
        )
        db.session.add(new_deal)
        
        # Update the lead's status
        lead.status = 'Converted'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lead converted successfully',
            'data': {
                'customer': customer_schema.dump(new_customer),
                'deal': deal_schema.dump(new_deal)
            }
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'A customer with this email already exists.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
