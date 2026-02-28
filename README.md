# Medical Debt Risk & Repayment Planning API

A REST API for assessing medical debt risk and generating repayment plans. Built for HackIllinois 2026.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+, FastAPI |
| Server | Uvicorn (ASGI) |
| Database | SQLite (local) / PostgreSQL (optional) |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic v2 |

## Quick Start

### Backend (API)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

- **App**: http://localhost:5173

The frontend proxies `/api` to the backend. Start the backend first.

## Seed Sample Data

```bash
python scripts/seed_data.py
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/debts` | Create debt record (returns risk + repayment plan) |
| GET | `/debts` | List debts (pagination, filtering) |
| GET | `/debts/{id}` | Get debt by ID |
| GET | `/debts/{id}/summary` | Get concise summary with payoff estimate |
| PATCH | `/debts/{id}` | Partial update (recomputes risk if financial fields change) |
| DELETE | `/debts/{id}` | Delete debt (idempotent) |

### Query Parameters for `GET /debts`

| Param | Type | Description |
|-------|------|-------------|
| `risk_level` | string | Filter by Low, Medium, High |
| `provider` | string | Partial match on provider name |
| `patient_name` | string | Partial match on patient name |
| `limit` | int | Page size (1–100, default 20) |
| `offset` | int | Pagination offset (default 0) |

## Example Requests

### Create debt (POST)

```bash
curl -X POST "http://127.0.0.1:8000/debts" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Doe",
    "income": 55000,
    "debt_amount": 12000,
    "credit_score": 640,
    "provider": "Carle Hospital"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "risk_score": 0.32,
  "risk_level": "Medium",
  "recommended_monthly_payment": 500.0
}
```

### List debts with filters

```bash
curl "http://127.0.0.1:8000/debts?risk_level=Medium&limit=10&offset=0"
```

### Get debt by ID

```bash
curl "http://127.0.0.1:8000/debts/1"
```

### Get debt summary

```bash
curl "http://127.0.0.1:8000/debts/1/summary"
```

## Error Handling

| Code | When |
|------|------|
| 400 | Invalid input (e.g., debt amount ≤ 0) |
| 404 | Debt not found |
| 422 | Validation error (Pydantic) |
| 500 | Unexpected server error |

## Risk Scoring Formula

```
risk_score = (debt_amount / income) × (700 - credit_score) / 700
```

- **Low**: risk_score < 0.2
- **Medium**: 0.2 ≤ risk_score < 0.5
- **High**: risk_score ≥ 0.5

Recommended monthly payment is computed for a 24-month repayment plan.

## PostgreSQL (Optional)

Set `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/medical_debt
```

Install driver: `pip install psycopg2-binary`

## Project Structure

```
medical-debt-api/
├── app/                    # Backend (FastAPI)
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── services/
│   │   └── risk_engine.py
│   └── routers/
│       └── debts.py
├── frontend/               # React (Vite)
│   ├── src/
│   │   ├── api.js         # API client
│   │   ├── components/
│   │   │   ├── CreateDebtForm.jsx
│   │   │   ├── DebtList.jsx
│   │   │   ├── DebtCard.jsx
│   │   │   └── DebtDetail.jsx
│   │   └── App.jsx
│   └── package.json
├── scripts/
│   └── seed_data.py
├── requirements.txt
└── README.md
```
