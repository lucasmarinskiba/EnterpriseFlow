import stripe
import os
from typing import Dict, Optional
from pydantic import BaseModel

# Configuración de Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

class SubscriptionData(BaseModel):
    customer_id: str
    subscription_id: str
    status: str
    plan_type: str
    current_period_end: int

class PaymentHandler:
    def __init__(self):
        self.stripe = stripe
        self.price_ids = {
            'basic': os.getenv("STRIPE_BASIC_PRICE_ID"),
            'premium': os.getenv("STRIPE_PREMIUM_PRICE_ID"),
            'enterprise': os.getenv("STRIPE_ENTERPRISE_PRICE_ID")
        }

    def create_subscription(self, customer_email: str, price_key: str) -> Dict:
        """Crea una suscripción con manejo de errores y flujo de pago seguro"""
        try:
            # Validar price_key
            if price_key not in self.price_ids:
                raise ValueError("Plan de suscripción inválido")

            # Crear cliente en Stripe
            customer = self.stripe.Customer.create(email=customer_email)
            
            # Crear suscripción con parámetros esenciales
            subscription = self.stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": self.price_ids[price_key]}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "customer_id": customer.id,
                "status": subscription.status
            }
            
        except self.stripe.error.StripeError as e:
            error_msg = f"Error Stripe ({e.code}): {e.user_message}"
            raise PaymentError(error_msg) from e
        except Exception as e:
            raise PaymentError(f"Error inesperado: {str(e)}") from e

    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[SubscriptionData]:
        """Procesa webhooks de Stripe para actualizar estados de suscripción"""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
            
            if event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                return SubscriptionData(
                    customer_id=subscription.customer,
                    subscription_id=subscription.id,
                    status=subscription.status,
                    plan_type=subscription.items.data[0].price.id,
                    current_period_end=subscription.current_period_end
                )
                
        except self.stripe.error.SignatureVerificationError as e:
            raise SecurityError("Firma de webhook inválida") from e
            
        return None

class PaymentError(Exception):
    """Excepción personalizada para errores de pago"""
    pass

class SecurityError(Exception):
    """Excepción para errores de seguridad"""
    pass
