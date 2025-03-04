# services/subscription_service.py
from extensions import db
from models import (
    Subscription, 
    SubscriptionPlan, 
    SubscriptionTransaction, 
    SubscriptionTier, 
    User
)
from datetime import datetime, timedelta
import stripe

class SubscriptionService:
    @classmethod
    def initialize_subscription_plans(cls):
        """
        Initialize default subscription plans
        """
        plans = [
            {
                'tier': SubscriptionTier.BASIC,
                'name': 'Basic Wine Explorer',
                'description': 'Basic wine recommendations and community features',
                'price': 0,
                'duration_months': 1,
                'features': {
                    'max_recommendations_per_day': 5,
                    'access_to_community': True,
                    'basic_wine_insights': True
                }
            },
            {
                'tier': SubscriptionTier.PREMIUM,
                'name': 'Premium Wine Enthusiast',
                'description': 'Advanced recommendations and exclusive features',
                'price': 9.99,
                'duration_months': 1,
                'features': {
                    'max_recommendations_per_day': 20,
                    'access_to_community': True,
                    'advanced_wine_insights': True,
                    'personalized_wine_journal': True,
                    'exclusive_tastings': True
                }
            },
            {
                'tier': SubscriptionTier.ELITE,
                'name': 'Elite Wine Connoisseur',
                'description': 'Ultimate wine experience with premium features',
                'price': 19.99,
                'duration_months': 1,
                'features': {
                    'unlimited_recommendations': True,
                    'access_to_community': True,
                    'advanced_wine_insights': True,
                    'personalized_wine_journal': True,
                    'exclusive_tastings': True,
                    'sommelier_consultation': True,
                    'wine_event_priority': True
                }
            }
        ]

        for plan_data in plans:
            existing_plan = SubscriptionPlan.query.filter_by(
                tier=plan_data['tier']
            ).first()

            if not existing_plan:
                plan = SubscriptionPlan(**plan_data)
                db.session.add(plan)
        
        db.session.commit()

    @classmethod
    def create_subscription(cls, user_id, plan_tier):
        """
        Create a new subscription for a user
        """
        # Find the plan
        plan = SubscriptionPlan.query.filter_by(tier=plan_tier).first()
        
        if not plan:
            raise ValueError("Invalid subscription plan")

        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            tier=plan_tier,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return subscription

    @classmethod
    def process_payment(cls, user_id, plan_tier, payment_method):
        """
        Process subscription payment
        """
        # Find the plan
        plan = SubscriptionPlan.query.filter_by(tier=plan_tier).first()
        
        if not plan:
            raise ValueError("Invalid subscription plan")

        try:
            # Process Stripe payment
            stripe.api_key = 'your_stripe_secret_key'
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(plan.price * 100),  # Convert to cents
                currency='usd',
                payment_method=payment_method,
                confirm=True
            )

            # Create transaction
            transaction = SubscriptionTransaction(
                user_id=user_id,
                plan_id=plan.id,
                amount=plan.price,
                payment_method='stripe',
                status=payment_intent.status
            )
            
            db.session.add(transaction)
            
            # Create subscription
            subscription = cls.create_subscription(user_id, plan_tier)
            
            db.session.commit()
            
            return {
                'subscription': subscription,
                'transaction': transaction,
                'payment_intent': payment_intent
            }
        
        except stripe.error.StripeError as e:
            db.session.rollback()
            raise ValueError(f"Payment failed: {str(e)}")

    @classmethod
    def get_user_subscription(cls, user_id):
        """
        Get current user subscription
        """
        subscription = Subscription.query.filter_by(
            user_id=user_id, 
            is_active=True
        ).order_by(
            Subscription.start_date.desc()
        ).first()
        
        return subscription

    @classmethod
    def check_subscription_access(cls, user_id, required_tier):
        """
        Check if user has access to a specific tier
        """
        subscription = cls.get_user_subscription(user_id)
        
        if not subscription:
            return False
        
        tier_hierarchy = {
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PREMIUM: 2,
            SubscriptionTier.ELITE: 3
        }
        
        return (
            tier_hierarchy.get(subscription.tier, 0) >= 
            tier_hierarchy.get(required_tier, 0)
        )