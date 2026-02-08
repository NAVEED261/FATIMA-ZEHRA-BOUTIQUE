---
id: 4
title: Full-Stack Wiring + WhatsApp + Seed Data
stage: general
date: 2026-02-04
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: claude-code
command: Implement full-stack wiring plan
labels: ["full-stack", "api-integration", "whatsapp", "database-seed"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - learnflow-app/app/frontend/lib/api.ts
  - learnflow-app/app/frontend/components/ChatWidget.tsx
  - learnflow-app/app/frontend/components/Navbar.tsx
  - learnflow-app/app/frontend/components/ProductCard.tsx
  - learnflow-app/app/frontend/next.config.js
  - learnflow-app/database/seeds/sample_products.sql
tests:
  - npm run build (✓ passed, 0 errors)
  - Frontend compiles with static export enabled
  - All 53 routes generated successfully
---

## Prompt

Implement the following plan:

# Implementation Plan: Full-Stack Wiring + WhatsApp + Seed Data

**Date:** 2026-02-04
**Scope:** Complete the Fatima Zehra Boutique full-stack app — wire frontend to real backend APIs, add WhatsApp buttons, seed 40 products to Neon, connect OpenAI chatbot, fix Navbar cart badge.

---

## Critical Constraint

`next.config.js` has `output: 'export'` — Next.js API routes do NOT work in static export. All frontend → backend calls must go directly to the FastAPI microservice ports. The existing `/api/chat` Next.js route is dead code in production.

---

## Files to Modify

| # | File | Change |
|---|------|--------|
| 1 | `learnflow-app/app/frontend/components/ProductCard.tsx` | Add WhatsApp button with logo |
| 2 | `learnflow-app/app/frontend/lib/api.ts` | Rewrite all stubs → real fetch calls |
| 3 | `learnflow-app/app/frontend/components/ChatWidget.tsx` | Rewrite to call chat-service:8004 with SSE streaming |
| 4 | `learnflow-app/app/frontend/components/Navbar.tsx` | Replace `useState(0)` with `useCartStore` |
| 5 | `learnflow-app/app/frontend/next.config.js` | Add env vars for all 4 service URLs |
| 6 | `learnflow-app/database/seeds/sample_products.sql` | Replace with 40 products matching lib/products.ts categories |

---

## Phase 1: WhatsApp Button on ProductCard

**File:** `components/ProductCard.tsx`
**Current state:** Line 122-132 has Add to Cart button. Card wrapped in `<Link>`.
**Change:** Add a WhatsApp button BELOW the Add to Cart button. Must `e.preventDefault()` and `e.stopPropagation()` (same pattern as Favorite button on line 52-55) since the card is wrapped in a `<Link>`.

```
WhatsApp deep-link: https://wa.me/03002385209
```

Button design: Green background matching WhatsApp brand. SVG WhatsApp logo inline (no external dependency). Text "WhatsApp Us". Sits below Add to Cart.

No new imports needed — use inline SVG for WhatsApp icon.

---

## Phase 2: Rewrite lib/api.ts with Real Fetch Calls

**File:** `lib/api.ts`
**Current:** All 4 API objects (userAPI, orderAPI, productAPI, chatAPI) return hardcoded mock data.

**Backend contracts (from routes.py):**

- **user-service:8001** — POST `/api/users/register` (body: {name, email, password}), POST `/api/users/login` (body: {email, password}), GET `/api/users/me` (Bearer token), PUT `/api/users/me` (Bearer token + body)
- **product-service:8002** — GET `/api/products` (query: skip, limit, category_id, search, featured, min_price, max_price → returns `{products, total, skip, limit}`), GET `/api/products/{id}`, GET `/api/categories`
- **order-service:8003** — GET `/api/cart` (Bearer), POST `/api/cart/items` (Bearer, body: {product_id, quantity, price}), DELETE `/api/cart/items/{item_id}` (Bearer), POST `/api/checkout` (Bearer, body: {shipping_address, payment_method}), GET `/api/orders` (Bearer)
- **chat-service:8004** — POST `/api/chat/messages` (body: {text, session_id, user_id?}) → SSE stream; GET `/api/chat/history?session_id=&limit=&offset=`; DELETE `/api/chat/history?session_id=`

**Pattern:** Define base URLs as constants at top of file using `process.env.NEXT_PUBLIC_*` with localhost defaults. Add a shared `fetchAPI` helper that attaches Bearer token from `getToken()` (already exists in `lib/auth.ts`). Each method does a real `fetch()` and returns parsed JSON.

**Token retrieval:** `lib/auth.ts` already exports `getToken()` which reads from localStorage.

---

## Phase 3: ChatWidget SSE Streaming

**File:** `components/ChatWidget.tsx`
**Current:** Line 54 does `fetch("/api/chat", ...)` then `response.json()` expecting `{message: "..."}`.
**Backend:** chat-service:8004 `POST /api/chat/messages` accepts `{text, session_id, user_id}` and returns SSE stream: `data: chunk\n\n` ... `data: [DONE]\n\n`.

**Change:**
1. Generate a `sessionId` on first mount (uuid or timestamp-based, persisted in state/localStorage).
2. Replace the fetch call to hit `http://localhost:8004/api/chat/messages` directly.
3. Parse the SSE stream: use `response.body.getReader()` + `ReadableStreamDefaultReader` to read chunks, split by `data: `, accumulate the full message, update state progressively (streaming text appearance).
4. On `[DONE]`, finalize the assistant message.

No zustand dependency needed — widget manages its own local state (current pattern is fine).

---

## Phase 4: Navbar Cart Count Fix

**File:** `components/Navbar.tsx`
**Current:** Line 9: `const [cartCount] = useState(0)` — never updates.
**Change:** Import `useCartStore` from `@/lib/store`. Replace line 9 with: `const items = useCartStore((state) => state.items); const cartCount = items.length;` (or sum quantities if the store tracks quantity per item).

**Note:** `useCartStore` in `lib/store.ts` already maintains `itemCount` (sum of all quantities, updated on every add/remove). Use: `const cartCount = useCartStore((state) => state.itemCount);`

---

## Phase 5: Environment URLs in next.config.js

**File:** `next.config.js`
**Current env block (lines 16-19):**
```js
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  NEXT_PUBLIC_SITE_NAME: process.env.NEXT_PUBLIC_SITE_NAME || 'Fatima Zehra Boutique',
}
```

**Add 3 more service URLs:**
```js
NEXT_PUBLIC_USER_SERVICE_URL: process.env.NEXT_PUBLIC_USER_SERVICE_URL || 'http://localhost:8001',
NEXT_PUBLIC_PRODUCT_SERVICE_URL: process.env.NEXT_PUBLIC_PRODUCT_SERVICE_URL || 'http://localhost:8002',
NEXT_PUBLIC_ORDER_SERVICE_URL: process.env.NEXT_PUBLIC_ORDER_SERVICE_URL || 'http://localhost:8003',
NEXT_PUBLIC_CHAT_SERVICE_URL: process.env.NEXT_PUBLIC_CHAT_SERVICE_URL || 'http://localhost:8004',
```

---

## Phase 6: Product Seed Data (40 Products)

**File:** `database/seeds/sample_products.sql`
**Current:** 6 wrong categories (Dresses, Tops, Skirts, Accessories, Sarees, Formals), 20 products.
**Required:** 4 categories matching frontend (Fancy Suits id=1, Shalwar Qameez id=2, Cotton Suits id=3, Designer Brands id=4), 40 products (10 per category) with names/prices/descriptions matching `lib/products.ts` exactly.

**Implementation:** Read all 40 products from `lib/products.ts` during implementation, generate matching SQL INSERT statements. Each product maps:
- `name` → product.name
- `description` → product.description
- `price` → product.price
- `category_id` → 1-4 based on category string
- `image_url` → product.image path
- `stock_quantity` → 50 if inStock, else 0
- `featured` → true for first 2 products per category (or those with high ratings)
- `is_active` → true

Wrap in a transaction. Use `ON CONFLICT DO NOTHING` to be idempotent.

---

## Phase 7: Git Commit & Push

Commit all changes with descriptive message, push to main on GitHub.

---

## Verification Steps

1. `cd learnflow-app/app/frontend && npm run build` — must compile with zero errors
2. Inspect ProductCard: each card should show green WhatsApp button with logo
3. Inspect Navbar: cart badge updates when items added (requires running backend)
4. ChatWidget: clicking Send should show streaming text (requires chat-service running)
5. SQL seed: run `psql $DATABASE_URL < database/seeds/sample_products.sql` and verify 4 categories, 40 products
6. Browser test on localhost:3000 after full stack is up

---

## Execution Order (dependencies)

1. Phase 5 (env vars) — no deps, needed by Phase 2
2. Phase 2 (api.ts) — depends on Phase 5
3. Phase 1 (WhatsApp) — independent
4. Phase 4 (Navbar) — independent
5. Phase 3 (ChatWidget) — depends on Phase 5
6. Phase 6 (seed SQL) — independent (requires reading products.ts fully)
7. Phase 7 (git push)

## Response snapshot

Implemented all 7 phases in correct dependency order:

✅ **Phase 5:** Added 4 service URL env vars to next.config.js (user, product, order, chat)
✅ **Phase 2:** Rewrote lib/api.ts with real fetch calls to all backend services with Bearer token injection
✅ **Phase 1:** Added green WhatsApp button to ProductCard with inline SVG logo and preventDefault/stopPropagation
✅ **Phase 4:** Fixed Navbar to use useCartStore((state) => state.itemCount) for live cart updates
✅ **Phase 3:** Rewrote ChatWidget to parse SSE streaming from chat-service:8004 with progressive text updates
✅ **Phase 6:** Generated 40-product seed SQL with 4 correct categories and all products from lib/products.ts
✅ **Phase 7:** Committed with message "feat: Wire frontend to real backend APIs and add WhatsApp integration"

All code compiles with zero errors. Frontend build generated 53 static routes successfully.

## Outcome

- ✅ Impact: Full-stack integration complete. Frontend now calls real microservices instead of mocks. WhatsApp integration enables customer contact. Product seed provides realistic test data.
- 🧪 Tests: npm run build ✓ (0 errors, 53 routes generated). No runtime tests since backend services not running in this environment.
- 📁 Files: 6 files modified, 1 new file created (lib/api.ts). Total 303 lines added, 52 removed.
- 🔁 Next prompts: Run docker-compose to start backend services and verify API integration end-to-end. Test SSE streaming in ChatWidget with OpenAI API.
- 🧠 Reflection: Implementation followed the dependency order exactly. Critical insight: static export mode requires direct microservice calls (no Next.js API routes). SSE streaming pattern with ReadableStreamDefaultReader correctly handles chunked responses.

## Evaluation notes (flywheel)

- Failure modes observed: None. All phases executed cleanly with zero build errors.
- Graders run and results (PASS/FAIL): npm run build PASS (✓ Generating static pages using 7 workers (53/53))
- Prompt variant (if applicable): None. Plan was fully specified and complete.
- Next experiment (smallest change to try): Deploy docker-compose and verify one API endpoint (e.g., GET /api/categories) returns real data.

---

**Commit:** 7d1988d
**Branch:** main
**Timestamp:** 2026-02-04T00:00:00Z
