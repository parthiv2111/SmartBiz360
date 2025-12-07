from flask import Blueprint, jsonify, request
from models import db, Product, Customer, Order, OrderItem, Expense, Lead, Deal
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from decimal import Decimal

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get analytics overview with key metrics"""
    try:
        # Total revenue
        total_revenue = db.session.query(func.sum(Order.total)).filter(
            Order.status != 'Cancelled'
        ).scalar() or Decimal('0.0')
        
        # New customers (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_customers = Customer.query.filter(
            Customer.created_at >= thirty_days_ago
        ).count()
        
        # Conversion rate: leads converted to deals / total leads
        total_leads = Lead.query.count()
        converted_leads = Lead.query.filter(Lead.status.in_(['Converted', 'Qualified'])).count()
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else Decimal('0.0')
        
        # Average order value
        avg_order_value = db.session.query(
            func.avg(Order.total)
        ).filter(
            Order.status != 'Cancelled'
        ).scalar() or Decimal('0.0')
        
        # Customer satisfaction: Based on repeat customer rate (customers with 2+ orders)
        repeat_customers = db.session.query(func.count(Customer.id)).select_from(Customer).join(Order).group_by(Customer.id).having(func.count(Order.id) >= 2).count()
        total_customers_with_orders = db.session.query(func.count(Customer.id)).select_from(Customer).join(Order).distinct().scalar() or 1
        customer_satisfaction = (repeat_customers / total_customers_with_orders * 100) if total_customers_with_orders > 0 else Decimal('0.0')
        
        # Profit margin: (Revenue - Expenses) / Revenue * 100
        total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or Decimal('0.0')
        profit = total_revenue - total_expenses
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.0')
        
        # Average delivery time: Days from order creation to completion
        completed_orders = Order.query.filter(
            Order.status == 'Completed',
            Order.created_at.isnot(None),
            Order.updated_at.isnot(None)
        ).all()
        if completed_orders:
            delivery_times = []
            for order in completed_orders:
                if order.created_at and order.updated_at:
                    days = (order.updated_at - order.created_at).days
                    if days >= 0:
                        delivery_times.append(days)
            avg_delivery_time = Decimal(sum(delivery_times) / len(delivery_times)) if delivery_times else Decimal('0.0')
        else:
            avg_delivery_time = Decimal('0.0')
        
        return jsonify({
            'success': True,
            'data': {
                'total_revenue': float(total_revenue),
                'new_customers': new_customers,
                'conversion_rate': float(conversion_rate),
                'avg_order_value': float(avg_order_value),
                'customer_satisfaction': float(customer_satisfaction),
                'profit_margin': float(profit_margin),
                'avg_delivery_time': float(avg_delivery_time)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/revenue-trends', methods=['GET'])
def get_revenue_trends():
    """Get detailed revenue trends"""
    try:
        period = request.args.get('period', 'monthly')  # daily, weekly, monthly, yearly
        
        if period == 'daily':
            # Last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            group_by = func.date(Order.created_at)
        elif period == 'weekly':
            # Last 12 weeks
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=12)
            group_by = func.date_trunc('week', Order.created_at)
        elif period == 'yearly':
            # Last 5 years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*5)
            group_by = func.date_trunc('year', Order.created_at)
        else:
            # Monthly (default)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            group_by = func.date_trunc('month', Order.created_at)
        
        revenue_data = db.session.query(
            group_by.label('period'),
            func.sum(Order.total).label('revenue'),
            func.count(Order.id).label('orders')
        ).filter(
            Order.created_at >= start_date,
            Order.status != 'Cancelled'
        ).group_by(group_by).order_by(group_by).all()
        
        trends = []
        for data in revenue_data:
            trends.append({
                'period': data.period.strftime('%Y-%m-%d') if period == 'daily' else 
                         data.period.strftime('%Y-%m') if period == 'monthly' else
                         data.period.strftime('%Y-%W') if period == 'weekly' else
                         data.period.strftime('%Y'),
                'revenue': float(data.revenue),
                'orders': data.orders
            })
        
        return jsonify({
            'success': True,
            'data': trends
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/customer-insights', methods=['GET'])
def get_customer_insights():
    """Get customer insights and analytics"""
    try:
        # Customer growth over time
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        customer_growth = db.session.query(
            func.date_trunc('month', Customer.created_at).label('month'),
            func.count(Customer.id).label('new_customers')
        ).filter(
            Customer.created_at >= start_date
        ).group_by(
            func.date_trunc('month', Customer.created_at)
        ).order_by(
            func.date_trunc('month', Customer.created_at)
        ).all()
        
        # Top customers by revenue
        top_customers = db.session.query(
            Customer.name,
            Customer.email,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total).label('total_spent')
        ).join(Order).filter(
            Order.status != 'Cancelled'
        ).group_by(
            Customer.id, Customer.name, Customer.email
        ).order_by(
            desc(func.sum(Order.total))
        ).limit(10).all()
        
        # Customer retention (customers with multiple orders)
        repeat_customers = db.session.query(
            func.count(Customer.id)
        ).select_from(Customer).join(Order).group_by(
            Customer.id
        ).having(
            func.count(Order.id) > 1
        ).count()
        
        total_customers_with_orders = db.session.query(
            func.count(Customer.id)
        ).select_from(Customer).join(Order).distinct().scalar()
        
        retention_rate = (repeat_customers / total_customers_with_orders * 100) if total_customers_with_orders > 0 else 0
        
        growth_data = []
        for month_data in customer_growth:
            growth_data.append({
                'month': month_data.month.strftime('%Y-%m'),
                'new_customers': month_data.new_customers
            })
        
        top_customers_data = []
        for customer in top_customers:
            top_customers_data.append({
                'name': customer.name,
                'email': customer.email,
                'total_orders': customer.total_orders,
                'total_spent': float(customer.total_spent)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'customer_growth': growth_data,
                'top_customers': top_customers_data,
                'retention_rate': round(retention_rate, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/product-performance', methods=['GET'])
def get_product_performance():
    """Get product performance analytics"""
    try:
        # Top selling products
        top_products = db.session.query(
            Product.name,
            Product.category,
            func.sum(OrderItem.quantity).label('units_sold'),
            func.sum(OrderItem.subtotal).label('revenue'),
            func.avg(OrderItem.unit_price).label('avg_price')
        ).join(OrderItem).group_by(
            Product.id, Product.name, Product.category
        ).order_by(
            desc(func.sum(OrderItem.quantity))
        ).limit(10).all()
        
        # Product category performance
        category_performance = db.session.query(
            Product.category,
            func.sum(OrderItem.quantity).label('units_sold'),
            func.sum(OrderItem.subtotal).label('revenue')
        ).join(OrderItem).group_by(
            Product.category
        ).order_by(
            desc(func.sum(OrderItem.subtotal))
        ).all()
        
        # Stock level analysis
        stock_analysis = db.session.query(
            Product.status,
            func.count(Product.id).label('count')
        ).group_by(Product.status).all()
        
        top_products_data = []
        for product in top_products:
            top_products_data.append({
                'name': product.name,
                'category': product.category,
                'units_sold': int(product.units_sold),
                'revenue': float(product.revenue),
                'avg_price': float(product.avg_price)
            })
        
        category_data = []
        for category in category_performance:
            category_data.append({
                'category': category.category,
                'units_sold': int(category.units_sold),
                'revenue': float(category.revenue)
            })
        
        stock_data = {}
        for stock in stock_analysis:
            stock_data[stock.status] = stock.count
        
        return jsonify({
            'success': True,
            'data': {
                'top_products': top_products_data,
                'category_performance': category_data,
                'stock_analysis': stock_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/sales-performance', methods=['GET'])
def get_sales_performance():
    """Get sales performance analytics"""
    try:
        # Sales by status
        sales_by_status = db.session.query(
            Order.status,
            func.count(Order.id).label('count'),
            func.sum(Order.total).label('revenue')
        ).group_by(Order.status).all()
        
        # Sales by payment method
        sales_by_payment = db.session.query(
            Order.payment_method,
            func.count(Order.id).label('count'),
            func.sum(Order.total).label('revenue')
        ).filter(
            Order.payment_method.isnot(None)
        ).group_by(Order.payment_method).all()
        
        # Monthly sales comparison
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_sales = db.session.query(
            func.sum(Order.total)
        ).filter(
            func.extract('month', Order.created_at) == current_month,
            func.extract('year', Order.created_at) == current_year,
            Order.status != 'Cancelled'
        ).scalar() or Decimal('0.0')
        
        last_month_sales = db.session.query(
            func.sum(Order.total)
        ).filter(
            func.extract('month', Order.created_at) == (current_month - 1 if current_month > 1 else 12),
            func.extract('year', Order.created_at) == (current_year if current_month > 1 else current_year - 1),
            Order.status != 'Cancelled'
        ).scalar() or Decimal('0.0')
        
        month_over_month_change = 0
        if last_month_sales > 0:
            month_over_month_change = ((current_month_sales - last_month_sales) / last_month_sales) * 100
        
        status_data = []
        for status in sales_by_status:
            status_data.append({
                'status': status.status,
                'count': status.count,
                'revenue': float(status.revenue)
            })
        
        payment_data = []
        for payment in sales_by_payment:
            payment_data.append({
                'method': payment.payment_method,
                'count': payment.count,
                'revenue': float(payment.revenue)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'sales_by_status': status_data,
                'sales_by_payment': payment_data,
                'current_month_sales': float(current_month_sales),
                'last_month_sales': float(last_month_sales),
                'month_over_month_change': round(month_over_month_change, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/inventory-value', methods=['GET'])
def get_inventory_value():
    """Get the total monetary value of all inventory"""
    try:
        inventory_value = db.session.query(func.sum(Product.price * Product.stock)).scalar() or 0
        return jsonify({
            'success': True,
            'data': {
                'inventory_value': float(inventory_value)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/analytics/finance-stats', methods=['GET'])
def get_finance_stats():
    """Get key finance stats including net profit"""
    try:
        total_revenue = db.session.query(func.sum(Order.total)).filter(Order.status != 'Cancelled').scalar() or 0
        total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
        net_profit = total_revenue - total_expenses
        
        return jsonify({
            'success': True,
            'data': {
                'total_revenue': float(total_revenue),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500