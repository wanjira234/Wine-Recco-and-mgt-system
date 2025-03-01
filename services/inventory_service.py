# services/inventory_service.py
from extensions import db
from models import Wine, WineInventory, WineRestock

class InventoryService:
    @classmethod
    def update_inventory(cls, wine_id, quantity_change):
        """
        Update wine inventory
        """
        inventory = WineInventory.query.filter_by(wine_id=wine_id).first()
        
        if not inventory:
            inventory = WineInventory(
                wine_id=wine_id, 
                quantity=0
            )
            db.session.add(inventory)
        
        inventory.quantity += quantity_change
        
        # Trigger restock if low
        if inventory.quantity < inventory.min_threshold:
            cls.create_restock_request(wine_id)
        
        db.session.commit()
        return inventory

    @classmethod
    def create_restock_request(cls, wine_id, requested_quantity=None):
        """
        Create a restock request for a wine
        """
        wine = Wine.query.get(wine_id)
        inventory = WineInventory.query.filter_by(wine_id=wine_id).first()
        
        if not requested_quantity:
            # Calculate default restock quantity
            requested_quantity = max(
                inventory.min_threshold * 2, 
                50  # Minimum restock quantity
            )
        
        restock_request = WineRestock(
            wine_id=wine_id,
            requested_quantity=requested_quantity,
            status='pending'
        )
        
        db.session.add(restock_request)
        db.session.commit()
        
        return restock_request

    @classmethod
    def get_low_stock_wines(cls, threshold=20):
        """
        Get wines with low stock
        """
        low_stock_wines = WineInventory.query.filter(
            WineInventory.quantity <= threshold
        ).all()
        
        return [
            {
                'wine_id': inv.wine_id,
                'wine_name': inv.wine.name,
                'current_quantity': inv.quantity,
                'min_threshold': inv.min_threshold
            } for inv in low_stock_wines
        ]