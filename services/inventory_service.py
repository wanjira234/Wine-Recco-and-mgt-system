from flask import current_app
from extensions import db
from models import Wine, WineInventory, WineRestock
import logging

class InventoryService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_inventory(self, wine_id, quantity_change):
        """
        Update wine inventory with comprehensive error handling
        """
        try:
            # Find or create inventory record
            inventory = WineInventory.query.filter_by(wine_id=wine_id).first()
            
            if not inventory:
                # Create new inventory if not exists
                inventory = WineInventory(
                    wine_id=wine_id, 
                    quantity=0,
                    min_threshold=20  # Default threshold
                )
                db.session.add(inventory)
            
            # Update quantity
            inventory.quantity += quantity_change
            
            # Log inventory changes
            self.logger.info(f"Inventory updated for wine {wine_id}: {quantity_change}")
            
            # Check for restock
            if inventory.quantity < inventory.min_threshold:
                self.create_restock_request(wine_id)
            
            db.session.commit()
            return inventory
        
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating inventory: {e}")
            raise

    def create_restock_request(self, wine_id, requested_quantity=None):
        """
        Create a comprehensive restock request
        """
        try:
            # Find wine and current inventory
            wine = Wine.query.get(wine_id)
            if not wine:
                raise ValueError(f"Wine with ID {wine_id} not found")
            
            inventory = WineInventory.query.filter_by(wine_id=wine_id).first()
            
            # Calculate default restock quantity
            if not requested_quantity:
                requested_quantity = max(
                    inventory.min_threshold * 2, 
                    50  # Minimum restock quantity
                )
            
            # Create restock request
            restock_request = WineRestock(
                wine_id=wine_id,
                requested_quantity=requested_quantity,
                status='pending'
            )
            
            db.session.add(restock_request)
            
            # Log restock request
            self.logger.info(f"Restock request created for wine {wine_id}: {requested_quantity}")
            
            db.session.commit()
            return restock_request
        
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating restock request: {e}")
            raise

    def get_low_stock_wines(self, threshold=20):
        """
        Retrieve wines with low stock
        """
        try:
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
        
        except Exception as e:
            self.logger.error(f"Error retrieving low stock wines: {e}")
            return []

# Create a singleton instance
inventory_service = InventoryService()