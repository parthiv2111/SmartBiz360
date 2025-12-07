from flask import Blueprint, jsonify, request, send_file
from models import db, Product, Customer, Order, OrderItem
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import io
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        from flask import request
        
        # Get date range from query parameter, default to 30 days
        days_param = request.args.get('days', '30')
        
        # Handle special date range values
        today = datetime.utcnow()
        if days_param == 'month':
            # This month
            current_start = datetime(today.year, today.month, 1)
            previous_start = datetime(today.year, today.month - 1, 1) if today.month > 1 else datetime(today.year - 1, 12, 1)
            period_days = (today - current_start).days
        elif days_param == 'last_month':
            # Last month
            if today.month == 1:
                current_start = datetime(today.year - 1, 12, 1)
                previous_start = datetime(today.year - 1, 11, 1)
            else:
                current_start = datetime(today.year, today.month - 1, 1)
                previous_start = datetime(today.year, today.month - 2, 1) if today.month > 2 else datetime(today.year - 1, 12, 1)
            period_days = (today - current_start).days
        elif days_param == 'year':
            # This year
            current_start = datetime(today.year, 1, 1)
            previous_start = datetime(today.year - 1, 1, 1)
            period_days = (today - current_start).days
        else:
            # Numeric days (7, 30, 90, etc.)
            try:
                period_days = int(days_param)
            except ValueError:
                period_days = 30
            
            current_start = today - timedelta(days=period_days)
            previous_start = today - timedelta(days=period_days * 2)

        # Total revenue (current period)
        total_revenue = db.session.query(func.sum(Order.total)).filter(
            Order.status != 'Cancelled',
            Order.created_at >= current_start
        ).scalar() or Decimal('0.0')
        
        # Active customers (total count, period-based change)
        active_customers = Customer.query.filter_by(status='Active').count()
        
        # Active customers who became active in current period
        new_active_current = Customer.query.filter(
            Customer.status == 'Active',
            Customer.created_at >= current_start
        ).count()
        
        # Active customers who became active in previous period
        new_active_prev = Customer.query.filter(
            Customer.status == 'Active',
            Customer.created_at >= previous_start,
            Customer.created_at < current_start
        ).count()
        
        # Products sold (current period)
        products_sold = db.session.query(func.sum(OrderItem.quantity)).join(Order).filter(
            Order.created_at >= current_start
        ).scalar() or 0
        
        # Pending orders (snapshot)
        pending_orders = Order.query.filter_by(status='Pending').count()
        
        # Recent orders (last 5)
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
        
        # Top products (current period)
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('sales'),
            func.sum(OrderItem.subtotal).label('revenue')
        ).join(OrderItem).join(Order).filter(
            Order.created_at >= current_start
        ).group_by(Product.name).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(4).all()
        
        top_products_data = []
        for product in top_products:
            top_products_data.append({
                'name': product.name,
                'sales': int(product.sales),
                'revenue': f"${float(product.revenue):,.0f}"
            })
        
        # Compute previous period metrics for deltas
        prev_revenue = db.session.query(func.sum(Order.total)).filter(
            Order.status != 'Cancelled',
            Order.created_at >= previous_start,
            Order.created_at < current_start
        ).scalar() or Decimal('0.0')

        prev_products_sold = db.session.query(func.sum(OrderItem.quantity)).join(Order).filter(
            Order.created_at >= previous_start,
            Order.created_at < current_start
        ).scalar() or 0

        prev_pending_orders = Order.query.filter(
            Order.status == 'Pending',
            Order.created_at >= previous_start,
            Order.created_at < current_start
        ).count()

        def pct_change(current, previous):
            try:
                current_val = float(current)
                previous_val = float(previous)
                if previous_val == 0:
                    return '+0%'
                delta = (current_val - previous_val) / previous_val * 100.0
                sign = '+' if delta >= 0 else ''
                return f"{sign}{delta:.1f}%"
            except Exception:
                return '+0%'

        return jsonify({
            'success': True,
            'data': {
                'stats': [
                    {
                        'title': 'Total Revenue',
                        'value': f"${float(total_revenue):,.2f}",
                        'change': pct_change(total_revenue, prev_revenue),
                        'changeType': 'positive',
                        'iconColor': 'text-success-600',
                        'iconBgColor': 'bg-success-50'
                    },
                    {
                        'title': 'Active Customers',
                        'value': f"{active_customers:,}",
                        'change': pct_change(new_active_current, new_active_prev),
                        'changeType': 'positive',
                        'iconColor': 'text-primary-600',
                        'iconBgColor': 'bg-primary-50'
                    },
                    {
                        'title': 'Products Sold',
                        'value': f"{products_sold:,}",
                        'change': pct_change(products_sold, prev_products_sold),
                        'changeType': 'positive',
                        'iconColor': 'text-warning-600',
                        'iconBgColor': 'bg-warning-50'
                    },
                    {
                        'title': 'Pending Orders',
                        'value': f"{pending_orders}",
                        'change': pct_change(pending_orders, prev_pending_orders),
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
        # Customer satisfaction: Based on repeat customer rate
        repeat_customers = db.session.query(func.count(Customer.id)).select_from(Customer).join(Order).group_by(Customer.id).having(func.count(Order.id) >= 2).count()
        total_customers_with_orders = db.session.query(func.count(Customer.id)).select_from(Customer).join(Order).distinct().scalar() or 1
        customer_satisfaction = (repeat_customers / total_customers_with_orders * 100) if total_customers_with_orders > 0 else 0.0
        
        # Profit margin: (Revenue - Expenses) / Revenue * 100
        from models import Expense
        total_revenue_all = db.session.query(func.sum(Order.total)).filter(Order.status != 'Cancelled').scalar() or Decimal('0.0')
        total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or Decimal('0.0')
        profit = total_revenue_all - total_expenses
        profit_margin = (float(profit / total_revenue_all * 100)) if total_revenue_all > 0 else 0.0
        
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
            avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
        else:
            avg_delivery_time = 0.0
        
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

@dashboard_bp.route('/dashboard/export', methods=['GET'])
def export_dashboard_report():
    """Export dashboard report in various formats"""
    try:
        from flask_jwt_extended import jwt_required, get_jwt_identity
        from models import User
        
        # Get format and date range from query parameters
        format_type = request.args.get('format', 'pdf').lower()
        days_param = request.args.get('days', '30')
        
        # Calculate date range (same logic as get_dashboard_stats)
        today = datetime.utcnow()
        if days_param == 'month':
            current_start = datetime(today.year, today.month, 1)
        elif days_param == 'last_month':
            if today.month == 1:
                current_start = datetime(today.year - 1, 12, 1)
            else:
                current_start = datetime(today.year, today.month - 1, 1)
        elif days_param == 'year':
            current_start = datetime(today.year, 1, 1)
        else:
            try:
                period_days = int(days_param)
            except ValueError:
                period_days = 30
            current_start = today - timedelta(days=period_days)
        
        # Get dashboard data
        total_revenue = db.session.query(func.sum(Order.total)).filter(
            Order.status != 'Cancelled',
            Order.created_at >= current_start
        ).scalar() or Decimal('0.0')
        
        active_customers = Customer.query.filter_by(status='Active').count()
        products_sold = db.session.query(func.sum(OrderItem.quantity)).join(Order).filter(
            Order.created_at >= current_start
        ).scalar() or 0
        pending_orders = Order.query.filter_by(status='Pending').count()
        
        # Get top products
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('sales'),
            func.sum(OrderItem.subtotal).label('revenue')
        ).join(OrderItem).join(Order).filter(
            Order.created_at >= current_start
        ).group_by(Product.name).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        # Get recent orders for PDF
        recent_orders = db.session.query(Order).join(Customer).order_by(
            Order.created_at.desc()
        ).limit(10).all()
        
        # Prepare report data
        report_data = {
            'period': days_param,
            'date_range': f"{current_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}",
            'total_revenue': float(total_revenue),
            'active_customers': active_customers,
            'products_sold': int(products_sold),
            'pending_orders': pending_orders,
            'top_products': [
                {
                    'name': p.name,
                    'sales': int(p.sales),
                    'revenue': float(p.revenue)
                }
                for p in top_products
            ],
            'recent_orders': [
                {
                    'order_number': order.order_number,
                    'customer': order.customer.name,
                    'total': float(order.total),
                    'status': order.status,
                    'date': order.order_date.strftime('%Y-%m-%d') if order.order_date else ''
                }
                for order in recent_orders
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'dashboard_report_{timestamp}'
        
        if format_type == 'csv':
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Dashboard Report'])
            writer.writerow(['Period', report_data['date_range']])
            writer.writerow(['Generated At', report_data['generated_at']])
            writer.writerow([])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Revenue', f"${report_data['total_revenue']:,.2f}"])
            writer.writerow(['Active Customers', report_data['active_customers']])
            writer.writerow(['Products Sold', report_data['products_sold']])
            writer.writerow(['Pending Orders', report_data['pending_orders']])
            writer.writerow([])
            writer.writerow(['Top Products'])
            writer.writerow(['Product Name', 'Sales', 'Revenue'])
            for product in report_data['top_products']:
                writer.writerow([product['name'], product['sales'], f"${product['revenue']:,.2f}"])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        
        elif format_type == 'xlsx':
            # For Excel, return CSV for now (can be enhanced with openpyxl later)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Dashboard Report'])
            writer.writerow(['Period', report_data['date_range']])
            writer.writerow(['Generated At', report_data['generated_at']])
            writer.writerow([])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Revenue', f"${report_data['total_revenue']:,.2f}"])
            writer.writerow(['Active Customers', report_data['active_customers']])
            writer.writerow(['Products Sold', report_data['products_sold']])
            writer.writerow(['Pending Orders', report_data['pending_orders']])
            writer.writerow([])
            writer.writerow(['Top Products'])
            writer.writerow(['Product Name', 'Sales', 'Revenue'])
            for product in report_data['top_products']:
                writer.writerow([product['name'], product['sales'], f"${product['revenue']:,.2f}"])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{filename}.xlsx'
            )
        
        else:  # PDF - generate PDF with tables
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph("Dashboard Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Report Info
            info_style = styles['Normal']
            story.append(Paragraph(f"<b>Period:</b> {report_data['date_range']}", info_style))
            story.append(Paragraph(f"<b>Generated At:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Key Metrics Table
            metrics_data = [
                ['Metric', 'Value'],
                ['Total Revenue', f"${report_data['total_revenue']:,.2f}"],
                ['Active Customers', str(report_data['active_customers'])],
                ['Products Sold', f"{report_data['products_sold']:,}"],
                ['Pending Orders', str(report_data['pending_orders'])],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(Paragraph("<b>Key Metrics</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            story.append(metrics_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Top Products Table
            if report_data['top_products']:
                products_data = [['Product Name', 'Sales (Units)', 'Revenue']]
                for product in report_data['top_products']:
                    products_data.append([
                        product['name'],
                        str(product['sales']),
                        f"${product['revenue']:,.2f}"
                    ])
                
                products_table = Table(products_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                products_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(Paragraph("<b>Top Selling Products</b>", styles['Heading2']))
                story.append(Spacer(1, 0.1*inch))
                story.append(products_table)
                story.append(Spacer(1, 0.3*inch))
            
            # Recent Orders Table
            if report_data['recent_orders']:
                orders_data = [['Order Number', 'Customer', 'Total', 'Status', 'Date']]
                for order in report_data['recent_orders']:
                    orders_data.append([
                        order['order_number'],
                        order['customer'],
                        f"${order['total']:,.2f}",
                        order['status'],
                        order['date']
                    ])
                
                orders_table = Table(orders_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 1.3*inch])
                orders_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(Paragraph("<b>Recent Orders</b>", styles['Heading2']))
                story.append(Spacer(1, 0.1*inch))
                story.append(orders_table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{filename}.pdf'
            )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
