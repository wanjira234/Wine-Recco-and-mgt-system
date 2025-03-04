# services/event_service.py
from extensions import db
from models import Event, EventAttendee, EventType, EventCategory
from services.notification_service import NotificationService
from datetime import datetime, timedelta
import uuid

class EventService:
    @classmethod
    def create_event(cls, event_data, host_id=None):
        """
        Create a new event
        """
        # Validate event dates
        if event_data['start_date'] > event_data['end_date']:
            raise ValueError("Start date must be before end date")

        # Create event
        event = Event(
            title=event_data['title'],
            description=event_data['description'],
            event_type=EventType(event_data['event_type']),
            category=EventCategory(event_data['category']),
            start_date=event_data['start_date'],
            end_date=event_data['end_date'],
            venue=event_data.get('venue'),
            address=event_data.get('address'),
            virtual_link=event_data.get('virtual_link'),
            total_capacity=event_data['total_capacity'],
            ticket_price=event_data['ticket_price'],
            host_id=host_id,
            organization=event_data.get('organization'),
            featured_wines=event_data.get('featured_wines', []),
            requirements=event_data.get('requirements')
        )

        db.session.add(event)
        db.session.commit()

        return event

    @classmethod
    def register_for_event(cls, event_id, user_id, attendee_data):
        """
        Register a user for an event
        """
        event = Event.query.get(event_id)
        
        if not event:
            raise ValueError("Event not found")

        # Check event capacity
        if event.current_attendees >= event.total_capacity:
            raise ValueError("Event is fully booked")

        # Create event attendee
        attendee = EventAttendee(
            event_id=event_id,
            user_id=user_id,
            ticket_type=attendee_data.get('ticket_type', 'standard'),
            payment_status='pending',
            dietary_restrictions=attendee_data.get('dietary_restrictions'),
            special_requests=attendee_data.get('special_requests')
        )

        db.session.add(attendee)
        
        # Update event attendee count
        event.current_attendees += 1
        
        db.session.commit()

        # Send notification
        NotificationService.create_notification(
            user_id=user_id,
            notification_type='event_registration',
            content=f"You've registered for {event.title}",
            metadata={
                'event_id': event.id,
                'event_title': event.title
            }
        )

        return attendee

    @classmethod
    def get_upcoming_events(cls, filters=None):
        """
        Retrieve upcoming events with optional filters
        """
        query = Event.query.filter(Event.start_date > datetime.utcnow())

        # Apply filters
        if filters:
            if filters.get('event_type'):
                query = query.filter(Event.event_type == EventType(filters['event_type']))
            
            if filters.get('category'):
                query = query.filter(Event.category == EventCategory(filters['category']))
            
            if filters.get('min_date'):
                query = query.filter(Event.start_date >= filters['min_date'])
            
            if filters.get('max_date'):
                query = query.filter(Event.start_date <= filters['max_date'])

        # Order by start date
        query = query.order_by(Event.start_date)

        return query.all()

    @classmethod
    def generate_virtual_event_link(cls):
        """
        Generate a unique virtual event link
        """
        return f"https://wine-events.com/{uuid.uuid4()}"

    @classmethod
    def cancel_event_registration(cls, event_id, user_id):
        """
        Cancel user's event registration
        """
        attendee = EventAttendee.query.filter_by(
            event_id=event_id, 
            user_id=user_id
        ).first()

        if not attendee:
            raise ValueError("Registration not found")

        # Remove attendee
        db.session.delete(attendee)
        
        # Update event attendee count
        event = Event.query.get(event_id)
        event.current_attendees -= 1
        
        db.session.commit()

        # Send cancellation notification
        NotificationService.create_notification(
            user_id=user_id,
            notification_type='event_cancellation',
            content=f"You've cancelled registration for {event.title}"
        )

        return True