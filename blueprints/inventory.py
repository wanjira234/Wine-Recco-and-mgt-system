# blueprints/inventory.py
from flask import Blueprint, jsonify
from services.inventory_service import InventoryService

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock_wines():
    """
    Get wines with low stock
    """
    try:
        low_stock_wines = InventoryService.get_low_stock_wines()
        return jsonify(low_stock_wines), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500