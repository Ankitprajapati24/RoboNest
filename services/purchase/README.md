# RoboNest — Purchase Service

The Purchase Service is a backend microservice in the RoboNest e-commerce platform. It manages purchase records, stores them in PostgreSQL, retrieves purchase information, and updates purchase statuses.

## Technology Stack

- **Python** — Backend programming
- **FastAPI** — REST API development
- **PostgreSQL** — Database
- **Psycopg** — PostgreSQL connectivity
- **Pydantic** — Request validation
- **Uvicorn** — ASGI server
- **python-dotenv** — Environment configuration

## Features

- Create a purchase with an initial `PENDING` status.
- Retrieve all purchases.
- Retrieve a purchase by its ID.
- Update a purchase's status.
- Check service health.
- Store purchase records in PostgreSQL.

## Project Structure

```text
services/purchase/
├── app/
│   └── main.py
└── README.md
```

## Database Schema

**Database:** `robonest_purchase`  
**Table:** `purchases`

| Column | Type | Description |
|---|---|---|
| `purchase_id` | UUID | Primary key |
| `product_id` | VARCHAR(100) | Product identifier |
| `quantity` | INTEGER | Purchase quantity; must be greater than zero |
| `status` | VARCHAR(30) | Purchase status; defaults to `PENDING` |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |

## Setup and Installation

### Prerequisites

- Python
- PostgreSQL
- Git

### 1. Create a virtual environment

From the repository root:

```bash
py -m venv .venv
```

Activate it on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 2. Install dependencies

```bash
py -m pip install fastapi uvicorn "psycopg[binary]" python-dotenv
```

### 3. Configure environment variables

Create a `.env` file in the repository root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=robonest_purchase
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

Replace the password placeholder with your local PostgreSQL password. Ensure the database and `purchases` table exist before running the service.

**Security:** Never commit `.env` or actual database credentials to GitHub.

## Running the Service

From the repository root, run:

```bash
py -m uvicorn services.purchase.app.main:app --reload
```

The service will be available at:

`http://127.0.0.1:8000`

On successful startup, the application confirms its PostgreSQL connection.

## API Reference

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check service health |
| POST | `/purchases` | Create a purchase |
| GET | `/purchases` | Retrieve all purchases |
| GET | `/purchases/{purchase_id}` | Retrieve a purchase by ID |
| PATCH | `/purchases/{purchase_id}/status` | Update purchase status |

### Create a Purchase

**Request:** `POST /purchases`

```json
{
  "product_id": "PROD-101",
  "quantity": 2
}
```

Returns `201 Created` with the generated purchase ID, product ID, quantity, and initial `PENDING` status.

### Retrieve Purchases

- `GET /purchases` returns a list of purchases, newest first.
- `GET /purchases/{purchase_id}` returns a specific purchase or `404 Not Found` if it does not exist.

### Update Purchase Status

**Request:** `PATCH /purchases/{purchase_id}/status`

```json
{
  "status": "CONFIRMED"
}
```

Supported values: `PENDING`, `CONFIRMED`, `CANCELLED`.

Returns the updated purchase record. If the purchase does not exist, the service returns `404 Not Found`. The current implementation validates status values but does not enforce status-transition rules.

### Health Check

**Request:** `GET /health`

Example response:

```json
{
  "service": "purchase",
  "status": "healthy"
}
```

## API Documentation and Testing

When the service is running:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI schema:** `http://127.0.0.1:8000/openapi.json`

Use Swagger UI to execute requests and inspect responses.

Recommended tests include creating a purchase, retrieving it, updating its status, submitting invalid input, and requesting a nonexistent purchase.

## Error Responses

| HTTP status | Meaning |
|---|---|
| `200 OK` | Request successful |
| `201 Created` | Purchase created |
| `404 Not Found` | Purchase does not exist |
| `422 Unprocessable Entity` | Request validation failed |
| `500 Internal Server Error` | Database operation failed |

## Future Integration

The current service supports REST APIs and PostgreSQL persistence. Planned work may include:

- gRPC communication with other RoboNest services.
- Kafka events for purchase creation and status updates.
- Automated tests and Docker-based deployment.
- CI/CD integration.

These integrations are planned and are not yet implemented in this service.

## Development

**Git branch:** `feature/purchase-service`

Commit and push changes to the feature branch. Follow the team's agreed review and integration process before merging.

---

*RoboNest — Robotics, electronics, and maker components marketplace.*
