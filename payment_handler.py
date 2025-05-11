import stripe
import os

class PaymentHandler:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_API_KEY")
    
    def create_subscription(self, user_email, plan):
        """Crea suscripción en Stripe"""
        customer = stripe.Customer.create(email=user_email)
        return stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": self._get_price_id(plan)}],
        )
    
    def _get_price_id(self, plan):
        """Obtiene IDs de precios de Stripe"""
        return {
            'premium': 'price_1PJ5Zx...',
            'enterprise': 'price_1PJ5Zy...'
        }.get(plan, 'price_basic')