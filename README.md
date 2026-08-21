# Expense Tracker & Analytics

A full-stack Python application for recording personal expenses, setting monthly budgets, and understanding spending patterns through an interactive dashboard.

This project was built as a Week 8 Full-Stack Python Capstone. It demonstrates a clean frontend-backend architecture using Streamlit, FastAPI, SQLAlchemy, SQLite/PostgreSQL, testing, CI, and Docker.

## Features

- Add, view, edit, delete, search, filter, and sort expenses
- Track expense amount, category, description, date, and payment method
- Predefined categories: Food, Transportation, Shopping, Bills, Entertainment, Healthcare, Education, Travel, Rent, and Other
- Dashboard metrics for total spending, current-month spending, transaction count, average daily expense, highest expense, and top category
- Analytics for spending by category, month, day, and payment method
- Top-expense table for the selected date range
- Date filters for today, this week, this month, last month, and a custom range
- Monthly budget tracking with remaining-budget and percentage-used calculations
- Warnings when spending reaches 80% of a budget or exceeds it
- FastAPI interactive documentation at `/docs` and `/redoc`
- pytest API tests with a separate in-memory test database
- GitHub Actions workflow that runs tests on pushes and pull requests
- Docker and PostgreSQL-ready configuration for deployment

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | Streamlit |
| Backend | FastAPI and Uvicorn |
| Database ORM | SQLAlchemy 2.x |
| Local Database | SQLite |
| Production Database | PostgreSQL |
| Validation | Pydantic |
| Testing | pytest, httpx, FastAPI TestClient |
| CI | GitHub Actions |
| Deployment | Docker / Docker Compose |

## Architecture

```text
User
 |
 v
Streamlit Frontend
 |
 | HTTP/REST
 v
FastAPI Backend
 |
 v
SQLAlchemy ORM
 |
 v
SQLite locally / PostgreSQL in production
```

The Streamlit frontend does not access the database directly. It calls the FastAPI backend through REST endpoints, and FastAPI handles validation, analytics, and database access.

## Project Structure

```text
expense-tracker-analytics/
├── backend/
│   ├── main.py                # FastAPI application and router setup
│   ├── database.py            # Database engine and session dependency
│   ├── models.py              # SQLAlchemy Expense and Budget models
│   ├── schemas.py             # Pydantic validation schemas
│   ├── crud.py                # Reusable database operations
│   ├── routers/               # Expenses, analytics, and budget endpoints
│   └── services/analytics.py  # Business logic and calculations
├── frontend/
│   ├── app.py                 # Streamlit interface
│   ├── api_client.py          # HTTP client for FastAPI calls
│   └── components/filters.py  # Shared date-filter component
├── tests/                     # API tests
├── .github/workflows/tests.yml
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/waqas-ullah-10/expense-tracker-analytics.git
cd expense-tracker-analytics
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

The local defaults in `.env` are:

```dotenv
DATABASE_URL=sqlite:///./expense_tracker.db
API_BASE_URL=http://127.0.0.1:8000
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

## Run the Application

### Start the FastAPI backend

Open a terminal in the project root and run:

```powershell
venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

### Start the Streamlit frontend

Open a second terminal in the same project folder and run:

```powershell
venv\Scripts\Activate.ps1
python -m streamlit run frontend/app.py
```

Streamlit normally opens at `http://localhost:8501`.

## API Documentation

FastAPI automatically provides interactive documentation while the backend is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Main API endpoints:

```text
GET, POST                 /api/expenses
GET, PUT, DELETE          /api/expenses/{expense_id}
GET                       /api/analytics/summary
GET                       /api/analytics/categories
GET                       /api/analytics/monthly
GET                       /api/analytics/daily
GET                       /api/analytics/payment-methods
GET                       /api/analytics/top-expenses
GET, POST                 /api/budgets
PUT, DELETE               /api/budgets/{budget_id}
GET                       /api/budgets/overview
```

## Run Tests

```powershell
venv\Scripts\Activate.ps1
pytest
```

The tests use a separate in-memory SQLite database, so they do not modify your local expense data.

## Continuous Integration

GitHub Actions is configured in `.github/workflows/tests.yml`.

On every push and pull request, GitHub Actions:

1. Sets up Python 3.11
2. Installs dependencies
3. Runs pytest
4. Reports whether the test suite passes or fails

## Docker

To run the FastAPI backend and PostgreSQL with Docker Compose:

```powershell
docker compose up --build
```

For production, replace the sample PostgreSQL credentials in `docker-compose.yml` with secure environment variables.

## Deployment

For production deployment:

1. Create a managed PostgreSQL database, such as Neon, Supabase, Render PostgreSQL, or Railway PostgreSQL.
2. Deploy the FastAPI backend to Render, Railway, or Fly.io.
3. Set `DATABASE_URL` to your PostgreSQL connection URL.
4. Set `CORS_ORIGINS` to your deployed Streamlit frontend URL.
5. Deploy the Streamlit frontend to Streamlit Community Cloud or Render.
6. Set `API_BASE_URL` in the frontend environment to the public FastAPI URL.

Example production database URL:

```dotenv
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME
```

SQLite is suitable for local development, but PostgreSQL is recommended for production persistence.

## Security Notes

- Never commit `.env`, passwords, API keys, or database credentials.
- Validate all input through Pydantic schemas.
- Configure approved browser origins through `CORS_ORIGINS`.
- Keep development database files and virtual environments out of Git.

## Author
**Waqas Ullah**
This application was completed as an internship task to demonstrate practical full-stack Python development skills, including API development, database design, frontend integration, testing, CI basics, and deployment readiness.

## Live Demo

```text
Streamlit URL: Add after deployment
FastAPI URL: Add after deployment
API Docs URL: Add after deployment/docs
GitHub Repository: https://github.com/waqas-ullah-10/expense-tracker-analytics
```
