---
name: wshobson-payment-processing
description: Payment processing patterns covering Stripe, PayPal, billing automation, and PCI compliance
---

# Payment Processing

Covers Stripe and PayPal integration, subscription billing automation, dunning management, proration, tax calculation, and PCI DSS compliance. Reference for building secure payment flows.

## Key Patterns

- **Checkout Sessions over Payment Intents** -- Stripe recommends Checkout Sessions for lower integration burden; use Payment Intents only when you need bespoke control
- **Tokenize everything** -- never let raw card data touch your server; use Stripe.js / PayPal SDK client-side
- **Webhook-driven fulfillment** -- never trust the client redirect; verify payment via `payment_intent.succeeded` or PayPal IPN
- **Idempotent webhook handling** -- deduplicate by `event_id` before processing
- **Dunning retry schedule** -- 3 days, 7 days, 14 days; cancel subscription after exhausting retries
- **Proration on plan changes** -- credit unused days on old plan, charge remaining days on new plan
- **PCI scope minimization** -- use SAQ A (hosted payment page) to avoid storing card data entirely
- **Never store CVV, PIN, or full track data** -- PCI DSS prohibits it regardless of encryption
- **Encrypt PAN at rest (AES-256-GCM)** and enforce TLS 1.2+ in transit
- **Audit log all access** to cardholder data with timestamp, user, action, IP

## Quick Reference

```python
# Stripe Checkout Session (recommended path)
session = stripe.checkout.Session.create(
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': 'Pro Plan'},
            'unit_amount': 2000,
            'recurring': {'interval': 'month'},
        },
        'quantity': 1,
    }],
    mode='subscription',
    success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
    cancel_url='https://example.com/cancel',
)

# Webhook verification (Flask)
@app.route('/webhook', methods=['POST'])
def webhook():
    event = stripe.Webhook.construct_event(
        request.data,
        request.headers.get('Stripe-Signature'),
        endpoint_secret,
    )
    if event['type'] == 'payment_intent.succeeded':
        handle_successful_payment(event['data']['object'])
    return 'OK', 200
```

### Subscription state machine

```
trial -> active -> past_due -> canceled
              -> paused -> resumed
```

### PCI DSS 12 requirements (summary)

1. Firewall config  2. No default passwords  3. Protect stored data
4. Encrypt in transit  5. Anti-malware  6. Secure development
7. Need-to-know access  8. Unique user IDs  9. Physical security
10. Audit logging  11. Regular testing  12. Security policy

### Test card numbers (Stripe)

| Scenario           | Number             |
|--------------------|--------------------|
| Success            | 4242 4242 4242 4242 |
| Declined           | 4000 0000 0000 0002 |
| 3D Secure required | 4000 0025 0000 3155 |
| Insufficient funds | 4000 0000 0000 9995 |

## When to Use

- Integrating Stripe or PayPal checkout flows
- Building SaaS subscription billing with dunning and proration
- Implementing PCI-compliant payment handling or preparing for a PCI audit
- Processing refunds, disputes, or chargebacks
- Setting up webhook-driven order fulfillment
