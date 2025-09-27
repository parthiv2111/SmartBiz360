from flask import Blueprint, jsonify
from models import db, Product, Customer, Order, OrderItem
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Total revenue
        total_revenue = db.session.query(func.sum(Order.total)).filter(
            Order.status != 'Cancelled'
        ).scalar() or Decimal('0.0')
        
        # Active customers
        active_customers = Customer.query.filter_by(status='Active').count()
        
        # Products sold (total quantity from order items)
        products_sold = db.session.query(func.sum(OrderItem.quantity)).scalar() or 0
        
        # Pending orders
        pending_orders = Order.query.filter_by(status='Pending').count()
        
        # Recent orders
        recent_orders = db.session.query(Order).join(Customer).order_by(
            Order.created_at.desc()
        ).limit(5).all()
        
        recent_orders_data = []
        for order in recent_orders:
            recent_orders_data.append({
                'id': order.order_number,
                'customer': order.customer.name,
                'product': ', '.join([item.product.name for item in order.order_items[:2]]),  # First 2 products
                'amount': f"${float(order.total):.2f}",
                'status': order.status
            })
        
        # Top products
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('sales'),
            func.sum(OrderItem.subtotal).label('revenue')
        ).join(OrderItem).group_by(Product.name).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(4).all()
        
        top_products_data = []
        for product in top_products:
            top_products_data.append({
                'name': product.name,
                'sales': int(product.sales),
                'revenue': f"${float(product.revenue):,.0f}"
            })
        
        return jsonify({
            'success': True,
            'data': {
                'stats': [
                    {
                        'title': 'Total Revenue',
                        'value': f"${float(total_revenue):,.2f}",
                        'change': '+20.1%',  # This would be calculated based on time period
                        'changeType': 'positive',
                        'iconColor': 'text-success-600',
                        'iconBgColor': 'bg-success-50'
                    },
                    {
                        'title': 'Active Customers',
                        'value': f"{active_customers:,}",
                        'change': '+180.1%',  # This would be calculated based on time period
                        'changeType': 'positive',
                        'iconColor': 'text-primary-600',
                        'iconBgColor': 'bg-primary-50'
                    },
                    {
                        'title': 'Products Sold',
                        'value': f"{products_sold:,}",
                        'change': '+19%',  # This would be calculated based on time period
                        'changeType': 'positive',
                        'iconColor': 'text-warning-600',
                        'iconBgColor': 'bg-warning-50'
                    },
                    {
                        'title': 'Pending Orders',
                        'value': f"{pending_orders}",
                        'change': '+201',  # This would be calculated based on time period
                        'changeType': 'positive',
                        'iconColor': 'text-secondary-600',
                        'iconBgColor': 'bg-secondary-50'
                    }
                ],
                'recent_orders': recent_orders_data,
                'top_products': top_products_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/dashboard/revenue-trends', methods=['GET'])
def get_revenue_trends():
    """Get revenue trends for charts"""
    try:
        # Get revenue for last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        monthly_revenue = db.session.query(
            func.date_trunc('month', Order.created_at).label('month'),
            func.sum(Order.total).label('revenue')
        ).filter(
            Order.created_at >= start_date,
            Order.status != 'Cancelled'
        ).group_by(
            func.date_trunc('month', Order.created_at)
        ).order_by(
            func.date_trunc('month', Order.created_at)
        ).all()
        
        revenue_data = []
        for month_data in monthly_revenue:
            revenue_data.append({
                'month': month_data.month.strftime('%Y-%m'),
                'revenue': float(month_data.revenue)
            })
        
        return jsonify({
            'success': True,
            'data': revenue_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/dashboard/customer-growth', methods=['GET'])
def get_customer_growth():
    """Get customer growth data for charts"""
    try:
        # Get customer count for last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        monthly_customers = db.session.query(
            func.date_trunc('month', Customer.created_at).label('month'),
            func.count(Customer.id).label('customers')
        ).filter(
            Customer.created_at >= start_date
        ).group_by(
            func.date_trunc('month', Customer.created_at)
        ).order_by(
            func.date_trunc('month', Customer.created_at)
        ).all()
        
        customer_data = []
        for month_data in monthly_customers:
            customer_data.append({
                'month': month_data.month.strftime('%Y-%m'),
                'customers': month_data.customers
            })
        
        return jsonify({
            'success': True,
            'data': customer_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/dashboard/performance-metrics', methods=['GET'])
def get_performance_metrics():
    """Get performance metrics"""
    try:
        # Customer satisfaction (mock data for now)
        customer_satisfaction = 98.5
        
        # Profit margin (mock data for now)
        profit_margin = 24.3
        
        # Average delivery time (mock data for now)
        avg_delivery_time = 2.4
        
        return jsonify({
            'success': True,
            'data': {
                'customer_satisfaction': customer_satisfaction,
                'profit_margin': profit_margin,
                'avg_delivery_time': avg_delivery_time
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
