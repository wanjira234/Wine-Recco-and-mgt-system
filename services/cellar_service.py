# services/cellar_service.py
from extensions import db
from models import WineCellar, WineCellarTransaction, WineCellarStatus, Wine
from services.notification_service import NotificationService
from datetime import datetime

class CellarService:
    @classmethod
    def add_wine_to_cellar(cls, user_id, wine_id, details):
        """
        Add a wine to user's cellar
        """
        # Check if wine already exists in cellar
        existing_entry = WineCellar.query.filter_by(
            user_id=user_id, 
            wine_id=wine_id
        ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.quantity += details.get('quantity', 1)
            existing_entry.purchase_price = details.get('purchase_price', existing_entry.purchase_price)
            existing_entry.storage_location = details.get('storage_location', existing_entry.storage_location)
            existing_entry.expected_peak_year = details.get('expected_peak_year', existing_entry.expected_peak_year)
        else:
            # Create new cellar entry
            cellar_entry = WineCellar(
                user_id=user_id,
                wine_id=wine_id,
                quantity=details.get('quantity', 1),
                purchase_price=details.get('purchase_price'),
                storage_location=details.get('storage_location'),
                expected_peak_year=details.get('expected_peak_year')
            )
            db.session.add(cellar_entry)
        
        db.session.commit()
        
        return existing_entry or cellar_entry

    @classmethod
    def update_wine_status(cls, cellar_id, status, additional_details=None):
        """
        Update status of a wine in the cellar
        """
        cellar_entry = WineCellar.query.get(cellar_id)
        
        if not cellar_entry:
            raise ValueError("Cellar entry not found")
        
        # Update status
        cellar_entry.status = WineCellarStatus(status)
        
        # Additional details based on status
        if status == 'consumed':
            cellar_entry.date_consumed = datetime.utcnow()
            cellar_entry.personal_rating = additional_details.get('personal_rating')
            cellar_entry.tasting_notes = additional_details.get('tasting_notes')
        
        # Create transaction
        transaction = WineCellarTransaction(
            cellar_id=cellar_id,
            transaction_type=status,
            quantity=cellar_entry.quantity,
            price=additional_details.get('price'),
            recipient_id=additional_details.get('recipient_id')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return cellar_entry

    @classmethod
    def get_user_cellar(cls, user_id, filters=None):
        """
        Retrieve user's cellar with optional filtering
        """
        query = WineCellar.query.filter_by(user_id=user_id)
        
        # Apply filters
        if filters:
            if filters.get('status'):
                query = query.filter(WineCellar.status == WineCellarStatus(filters['status']))
            
            if filters.get('min_purchase_year'):
                query = query.join(Wine).filter(Wine.year >= filters['min_purchase_year'])
            
            if filters.get('max_purchase_year'):
                query = query.join(Wine).filter(Wine.year <= filters['max_purchase_year'])
        
        # Order by purchase date
        query = query.order_by(WineCellar.purchase_date.desc())
        
        return query.all()

    @classmethod
    def get_aging_recommendations(cls, user_id):
        """
        Get recommendations for aging wines
        """
        # Find wines that could benefit from aging
        aging_wines = WineCellar.query.filter(
            WineCellar.user_id == user_id,
            WineCellar.status == WineCellarStatus.IN_STOCK,
            WineCellar.expected_peak_year > datetime.now().year
        ).all()
        
        return [
            {
                'wine_id': entry.wine_id,
                'wine_name': entry.wine.name,
                'current_year': datetime.now().year,
                'peak_year': entry.expected_peak_year,
                'years_left': entry.expected_peak_year - datetime.now().year
            } for entry in aging_wines
        ]

    @classmethod
    def analyze_cellar_value(cls, user_id):
        """
        Analyze the total value and composition of user's cellar
        """
        cellar_entries = WineCellar.query.filter_by(
            user_id=user_id, 
            status=WineCellarStatus.IN_STOCK
        ).all()
        
        # Calculate total value and wine type distribution
        total_value = 0
        wine_type_distribution = {}
        
        for entry in cellar_entries:
            # Calculate entry value
            entry_value = entry.quantity * (entry.purchase_price or 0)
            total_value += entry_value
            
            # Track wine type distribution
            wine_type = entry.wine.type
            wine_type_distribution[wine_type] = wine_type_distribution.get(wine_type, 0) + entry.quantity
        
        return {
            'total_wines': len(cellar_entries),
            'total_value': total_value,
            'wine_type_distribution': wine_type_distribution,
            'average_bottle_value': total_value / len(cellar_entries) if cellar_entries else 0
        }