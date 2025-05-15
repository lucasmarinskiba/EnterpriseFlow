import stripe
import os
from typing import Dict, Optional
from pydantic import BaseModel

# Si estás trabajando localmente, descomentá estas 2 líneas:
# from dotenv import load_dotenv
# load_dotenv()

class SubscriptionData(BaseModel):
    customer_id: str
    subscription_id: str
    status: str
    plan_type: str

class PaymentHandler:
    def _init_(self):
        # Verificación explícita de que la clave fue cargada
        api_key = os.getenv("STRIPE_API_KEY")
        if not api_key:
            raise ValueError("Falta la variable de entorno STRIPE_API_KEY")

        stripe.api_key = api_key
        self.stripe = stripe

        self.price_ids = {
            'basico': os.getenv("STRIPE_BASIC_PRICE_ID"),
            'premium': os.getenv("STRIPE_PREMIUM_PRICE_ID"),
            'enterprise': os.getenv("STRIPE_ENTERPRISE_PRICE_ID")
        }

        # Validar que se hayan cargado todos los IDs de precio
        for plan, price_id in self.price_ids.items():
            if not price_id:
                raise ValueError(f"Falta la variable de entorno STRIPE_{plan.upper()}_PRICE_ID")

    def create_subscription(self, customer_email: str, price_key: str) -> Dict:
        try:
            customer = self.stripe.Customer.create(email=customer_email)

            subscription = self.stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": self.price_ids[price_key]}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )

            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }

        except self.stripe.error.StripeError as e:
            raise Exception(f"Error Stripe: {e.user_message}") from e

    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[SubscriptionData]:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            raise ValueError("Falta la variable de entorno STRIPE_WEBHOOK_SECRET")

        try:
            event = self.stripe.Webhook.construct_event(
                payload,
                sig_header,
                webhook_secret
            )

            if event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                return SubscriptionData(
                    customer_id=subscription.customer,
                    subscription_id=subscription.id,
                    status=subscription.status,
                    plan_type=subscription.items.data[0].price.id
                )

        except self.stripe.error.SignatureVerificationError as e:
            raise Exception("Firma inválida") from e

        return None
