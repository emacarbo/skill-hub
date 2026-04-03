---
name: stripe-integration-expert
description: Use when implementing Stripe payments -- subscriptions, checkout, webhooks, usage billing, customer portal. Covers Next.js, Express, Django patterns.
---

# Stripe Integration Expert

Production-grade Stripe: subscriptions, checkout, webhooks, usage billing, portal, invoicing.

## Subscription Lifecycle

```
FREE_TRIAL --paid--> ACTIVE --cancel--> CANCEL_PENDING --period_end--> CANCELED
     |                  |                                                   |
     |               downgrade                                         reactivate
     |                  v                                                   |
     |             DOWNGRADING --period_end--> ACTIVE (lower plan)          |
     |                                                                      |
     +--trial_end no payment--> PAST_DUE --failed 3x--> CANCELED
                                    |
                               payment_success --> ACTIVE
```

DB statuses: `trialing | active | past_due | canceled | cancel_pending | paused | unpaid`

## Client Setup

```typescript
import Stripe from "stripe"

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2024-04-10", typescript: true,
  appInfo: { name: "myapp", version: "1.0.0" },
})

export const PLANS = {
  starter: { monthly: process.env.STRIPE_STARTER_MONTHLY_PRICE_ID!, yearly: process.env.STRIPE_STARTER_YEARLY_PRICE_ID! },
  pro: { monthly: process.env.STRIPE_PRO_MONTHLY_PRICE_ID!, yearly: process.env.STRIPE_PRO_YEARLY_PRICE_ID! },
} as const
```

## Checkout Session (Next.js App Router)

```typescript
export async function POST(req: Request) {
  const user = await getAuthUser()
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const { priceId } = await req.json()

  // Get or create customer
  let stripeCustomerId = user.stripeCustomerId
  if (!stripeCustomerId) {
    const customer = await stripe.customers.create({ email: user.email, metadata: { userId: user.id } })
    stripeCustomerId = customer.id
    await db.user.update({ where: { id: user.id }, data: { stripeCustomerId } })
  }

  const session = await stripe.checkout.sessions.create({
    customer: stripeCustomerId, mode: "subscription",
    line_items: [{ price: priceId, quantity: 1 }],
    allow_promotion_codes: true,
    subscription_data: { trial_period_days: user.hasHadTrial ? undefined : 14, metadata: { userId: user.id } },
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    metadata: { userId: user.id },
  })
  return NextResponse.json({ url: session.url })
}
```

## Subscription Upgrade/Downgrade

```typescript
export async function changeSubscriptionPlan(subscriptionId: string, newPriceId: string, immediate = false) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId)
  const currentItem = subscription.items.data[0]

  return stripe.subscriptions.update(subscriptionId, {
    items: [{ id: currentItem.id, price: newPriceId }],
    proration_behavior: immediate ? "always_invoice" : "none",
    billing_cycle_anchor: "unchanged",
  })
}

// Preview proration before confirming
export async function previewProration(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId)
  const invoice = await stripe.invoices.retrieveUpcoming({
    customer: subscription.customer as string, subscription: subscriptionId,
    subscription_items: [{ id: subscription.items.data[0].id, price: newPriceId }],
    subscription_proration_date: Math.floor(Date.now() / 1000),
  })
  return { amountDue: invoice.amount_due, lineItems: invoice.lines.data }
}
```

## Webhook Handler (Idempotent)

```typescript
export async function POST(req: Request) {
  const body = await req.text()
  const signature = headers().get("stripe-signature")!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch { return NextResponse.json({ error: "Invalid signature" }, { status: 400 }) }

  if (await hasProcessedEvent(event.id)) return NextResponse.json({ received: true, skipped: true })

  try {
    switch (event.type) {
      case "checkout.session.completed": await handleCheckoutCompleted(event.data.object); break
      case "customer.subscription.created":
      case "customer.subscription.updated": await handleSubscriptionUpdated(event.data.object); break
      case "customer.subscription.deleted": await handleSubscriptionDeleted(event.data.object); break
      case "invoice.payment_failed": await handlePaymentFailed(event.data.object); break
    }
    await markEventProcessed(event.id, event.type)
    return NextResponse.json({ received: true })
  } catch (err) {
    return NextResponse.json({ error: "Processing failed" }, { status: 500 }) // Stripe retries
  }
}
```

Key webhook handlers: sync subscription status/priceId/periodEnd to DB. On payment failure, update to `past_due` and send dunning emails (final after 3 attempts).

## Usage-Based Billing

```typescript
export async function reportUsage(subscriptionItemId: string, quantity: number) {
  await stripe.subscriptionItems.createUsageRecord(subscriptionItemId, {
    quantity, timestamp: Math.floor(Date.now() / 1000), action: "increment",
  })
}
```

## Customer Portal

```typescript
export async function POST() {
  const user = await getAuthUser()
  if (!user?.stripeCustomerId) return NextResponse.json({ error: "No billing" }, { status: 400 })
  const portalSession = await stripe.billingPortal.sessions.create({
    customer: user.stripeCustomerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/settings/billing`,
  })
  return NextResponse.json({ url: portalSession.url })
}
```

## Feature Gating

```typescript
export function isSubscriptionActive(user: { subscriptionStatus: string | null, stripeCurrentPeriodEnd: Date | null }) {
  if (!user.subscriptionStatus) return false
  if (["active", "trialing"].includes(user.subscriptionStatus)) return true
  if (user.subscriptionStatus === "past_due" && user.stripeCurrentPeriodEnd)
    return user.stripeCurrentPeriodEnd > new Date()
  return false
}
```

## Testing with Stripe CLI

```bash
stripe listen --forward-to localhost:3000/api/webhooks/stripe
stripe trigger checkout.session.completed
stripe trigger invoice.payment_failed

# Test cards: Success 4242424242424242 | Auth 4000002500003155 | Decline 4000000000009995
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Webhook delivery order not guaranteed | Re-fetch from Stripe API, don't trust event data alone |
| Double-processing webhooks | Always use idempotency table |
| Trial abuse | Store `hasHadTrial: true` in DB |
| Proration surprises | Always preview before upgrade |
| Portal not configured | Enable in Stripe dashboard > Billing > Customer portal |
| Can't link subscription to user | Always pass `userId` in metadata |
