import stripe
import os

class PaymentHandler:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = os.getenv("STRIPE_API_KEY")
        self.price_ids = {
            'basico': os.getenv("STRIPE_BASIC_PRICE_ID"),
            'premium': os.getenv("STRIPE_PREMIUM_PRICE_ID")
        }

    def create_subscription(self, customer_email: str, plan: str):
        try:
            customer = self.stripe.Customer.create(email=customer_email)
            subscription = self.stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": self.price_ids[plan]}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
        except Exception as e:
            raise Exception(f"Error Stripe: {str(e)}")
