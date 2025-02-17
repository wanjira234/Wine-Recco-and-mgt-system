from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Wine, Order
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def admin_dashboard():
    # Basic dashboard statistics
    total_users = User.query.count()
    total_wines = Wine.query.count()
    total_orders = Order.query.count()
    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()

    return jsonify({
        "statistics": {
            "total_users": total_users,
            "total_wines": total_wines,
            "total_orders": total_orders
        },
        "recent_orders": [
            {
                "id": order.id,
                "user_id": order.user_id,
                "total_price": order.total_price,
                "status": order.status,
                "created_at": order.created_at.isoformat()
            } for order in recent_orders
        ]
    })

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    users = User.query.paginate(page=page, per_page=per_page)

    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            } for user in users.items
        ],
        "total_pages": users.pages,
        "current_page": page
    })