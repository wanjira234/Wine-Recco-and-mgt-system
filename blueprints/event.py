# blueprints/event.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.event_service import EventService
from services.subscription_service import SubscriptionService

event_bp = Blueprint('event', __name__)

@event_bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    """
    Create a new event
    """
    user_id = get_jwt_identity()
    
    # Check subscription tier for event creation
    if not SubscriptionService.check_subscription_access(
        user_id, 
        required_tier='PREMIUM'
    ):
        return jsonify({
            'error': 'Insufficient subscription tier'
        }), 403

    data = request.get_json()
    
    try:
        event = EventService.create_event(data, host_id=user_id)
        return jsonify({
            'id': event.id,
            'title': event.title
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@event_bp.route('/register/<int:event_id>', methods=['POST'])
@jwt_required()
def register_for_event(event_id):
    """
    Register for an event
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    try:
        attendee = EventService.register_for_event(
            event_id, 
            user_id, 
            data
        )
        return jsonify({
            'message': 'Registration successful',
            'attendee_id': attendee.id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@event_bp.route('/', methods=['GET'])
def get_events():
    """
    Retrieve upcoming events
    """
    filters = {
        'event_type': request.args.get('type'),
        'category': request.args.get('category'),
        'min_date': request.args.get('min_date'),
        'max_date': request.args.get('max_date')
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        events = EventService.get_upcoming_events(filters)
        return jsonify([
            {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type.value,
                'category': event.category.value,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat(),
                'venue': event.venue,
                'total_capacity': event.total_capacity,
                'current_attendees': event.current_attendees,
                'ticket_price': event.ticket_price
            } for event in events
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500