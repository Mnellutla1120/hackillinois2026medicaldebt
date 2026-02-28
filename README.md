# Medical Debt Risk & Repayment Planning API (MediPay)

REST API for assessing medical debt risk, generating repayment plans with **interest** and **down payments**, and processing payments via Stripe. Usable **without the frontend** via cURL, Postman, or any HTTP client.

**Built for HackIllinois 2026.**

---

## 1. Project overview

- **Purpose**: Create and manage medical debt records, get risk scores and repayment plans (with optional interest and down payment), and pay via Stripe (monthly, down payment, or custom amount).
- **Stateful**: POST creates/updates data; state is persisted (SQLite or PostgreSQL).
- **Queryable over HTTP**: All endpoints are HTTP GET/POST/PATCH/DELETE and return JSON.

---

## 2. Tech stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+, FastAPI |
| Frontend | React 19, Vite (optional) |
| Payments | Stripe Checkout |
| Server | Uvicorn (ASGI) |
| Database | SQLite (local) / PostgreSQL (optional) |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic v2 |

---

## 3. How to run locally

```bash
# Clone and enter project
cd hackillinois2026medicaldebt

# Backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: frontend (for combined app)
cd frontend && npm install && npm run build && cd ..

# Run API (and serve frontend if built)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the combined script:

```bash
./run.sh
```

- **Base URL (local)**: `http://localhost:8000`
- **Interactive API docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Stripe

Copy `.env.example` to `.env` and set:

```env
STRIPE_SECRET_KEY=sk_test_...
```

Get test keys at [Stripe Dashboard → API Keys](https://dashboard.stripe.com/test/apikeys).

### Seed data

```bash
python scripts/seed_data.py
```

---

## 4. Using the API without the frontend

The API is designed to be **fully usable with cURL or Postman**. No browser or frontend required.

- **Content-Type**: `application/json` for request bodies.
- **No auth**: No JWT or cookies required for these endpoints.

---

## 5. API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/debts` | List debts (pagination, filtering) |
| GET | `/debts/{id}` | Get one debt |
| GET | `/debts/{id}/summary` | Get summary (payoff, interest, remaining) |
| POST | `/debts` | Create debt (risk + repayment with interest/down payment) |
| PATCH | `/debts/{id}` | Update debt (recomputes plan) |
| DELETE | `/debts/{id}` | Delete debt |
| POST | `/stripe/create-checkout-session` | Create Stripe Checkout (monthly, down payment, or custom amount) |
| GET | `/health` | Health check |

### Query parameters for `GET /debts`

| Param | Type | Description |
|-------|------|-------------|
| `risk_level` | string | `Low`, `Medium`, or `High` |
| `provider` | string | Partial match |
| `patient_name` | string | Partial match |
| `limit` | int | 1–100 (default 20) |
| `offset` | int | Pagination (default 0) |

---

## 6. Example requests and responses

### Create a debt (POST `/debts`)

**Request:**

```bash
curl -X POST "http://localhost:8000/debts" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Doe",
    "income": 55000,
    "debt_amount": 12000,
    "credit_score": 640,
    "provider": "Carle Hospital",
    "interest_rate": 0.05,
    "down_payment": 2000,
    "repayment_months": 24
  }'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "risk_score": 0.0187,
  "risk_level": "Low",
  "recommended_monthly_payment": 441.43,
  "total_interest": 594.32,
  "amount_after_down_payment": 10000,
  "estimated_payoff_months": 24
}
```

Minimal body (no interest, no down payment):

```bash
curl -X POST "http://localhost:8000/debts" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Doe",
    "income": 55000,
    "debt_amount": 12000,
    "credit_score": 640,
    "provider": "Carle Hospital"
  }'
```

---

### List debts (GET `/debts`)

```bash
curl "http://localhost:8000/debts?risk_level=Medium&limit=10&offset=0"
```

**Response (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "patient_name": "Jane Doe",
      "income": 55000,
      "debt_amount": 12000,
      "credit_score": 640,
      "provider": "Carle Hospital",
      "interest_rate": 0.05,
      "down_payment": 2000,
      "repayment_months": 24,
      "risk_score": 0.0187,
      "risk_level": "Low",
      "recommended_monthly_payment": 441.43,
      "total_interest": 594.32,
      "created_at": "2026-02-28T12:00:00",
      "updated_at": "2026-02-28T12:00:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

### Get one debt (GET `/debts/{id}`)

```bash
curl "http://localhost:8000/debts/1"
```

**Response (200 OK):** Same shape as one object in `items` above.

---

### Get debt summary (GET `/debts/{id}/summary`)

```bash
curl "http://localhost:8000/debts/1/summary"
```

**Response (200 OK):**

```json
{
  "id": 1,
  "patient_name": "Jane Doe",
  "provider": "Carle Hospital",
  "debt_amount": 12000,
  "down_payment": 2000,
  "amount_remaining": 10000,
  "risk_level": "Low",
  "recommended_monthly_payment": 441.43,
  "total_interest": 594.32,
  "estimated_payoff_months": 24
}
```

---

### Update a debt (PATCH `/debts/{id}`)

```bash
curl -X PATCH "http://localhost:8000/debts/1" \
  -H "Content-Type: application/json" \
  -d '{"down_payment": 3000, "repayment_months": 18}'
```

**Response (200 OK):** Full debt object (recomputed risk and repayment).

---

### Delete a debt (DELETE `/debts/{id}`)

```bash
curl -X DELETE "http://localhost:8000/debts/1"
```

**Response (204 No Content):** Empty body.

---

### Create Stripe Checkout session (POST `/stripe/create-checkout-session`)

**Monthly payment (default):**

```bash
curl -X POST "http://localhost:8000/stripe/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{
    "debt_id": 1,
    "success_url": "http://localhost:8000/?payment=success",
    "cancel_url": "http://localhost:8000/?payment=cancelled"
  }'
```

**Down payment or custom amount:**

```bash
curl -X POST "http://localhost:8000/stripe/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{
    "debt_id": 1,
    "amount": 2000,
    "payment_type": "down_payment"
  }'
```

**Response (200 OK):**

```json
{
  "url": "https://checkout.stripe.com/...",
  "session_id": "cs_..."
}
```

Redirect the user to `url` to complete payment.

---

## 7. Error responses

All errors return JSON with a `detail` field.

| Status | Meaning | Example `detail` |
|--------|---------|------------------|
| 400 | Bad request | `"Down payment must be less than debt amount"` |
| 404 | Not found | `"Debt not found"` |
| 422 | Validation error | Pydantic body (field-level errors) |
| 500 | Server error | `"An unexpected error occurred. Please try again."` |
| 503 | Stripe not configured | `"Stripe is not configured. Set STRIPE_SECRET_KEY in environment."` |

**Example (400):**

```json
{
  "detail": "Down payment must be less than debt amount"
}
```

**Example (404):**

```json
{
  "detail": "Debt not found"
}
```

**Example (422 validation):**

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "income"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

## 8. Repayment logic (interest & down payment)

- **Principal** = `debt_amount - down_payment` (must be &gt; 0).
- **No interest** (`interest_rate` = 0):  
  `recommended_monthly_payment = principal / repayment_months`
- **With interest** (`interest_rate` &gt; 0, e.g. 0.05 = 5% annual):  
  Amortization formula so the loan pays off in `repayment_months`; `total_interest` is returned.

Risk score is unchanged:  
`risk_score = (debt_amount / income) × (700 - credit_score) / 700`  
(Low &lt; 0.2, Medium 0.2–0.5, High ≥ 0.5.)

---

## 9. PostgreSQL (optional)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/medical_debt
```

```bash
pip install psycopg2-binary
```

---

## 10. Project structure

```
├── app/
│   ├── main.py             # FastAPI app, serves React build + API
│   ├── models.py            # SQLAlchemy MedicalDebt
│   ├── schemas.py           # Pydantic request/response
│   ├── database.py          # SQLite/PostgreSQL + migration
│   ├── services/
│   │   └── risk_engine.py   # Risk + amortization
│   └── routers/
│       ├── debts.py
│       └── stripe_router.py
├── frontend/               # React (optional)
├── scripts/
│   └── seed_data.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 11. Checklist for judges

- At least one HTTP endpoint: **Yes** (multiple GET/POST/PATCH/DELETE).
- Queryable over HTTP: **Yes** (JSON, no browser required).
- Works on localhost: **Yes** (`http://localhost:8000`).
- Testable with Postman/cURL: **Yes** (examples above).
- README with base URL, endpoints, sample request/response, errors: **Yes** (this file).
- Proper status codes: **Yes** (200, 201, 204, 400, 404, 422, 500, 503).
- Stateful / POST: **Yes** (create/update debts, Stripe sessions).
- OpenAPI/Swagger: **Yes** at `/docs`.
