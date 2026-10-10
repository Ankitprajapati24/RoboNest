
import os
from contextlib import asynccontextmanager
from uuid import uuid4

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

load_dotenv()


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
        print("Purchase Service connected to PostgreSQL.")
    except Exception as error:
        print(f"PostgreSQL connection failed: {error}")
        raise

    yield


app = FastAPI(
    title="RoboNest Purchase Service",
    description="API for managing purchase requests in RoboNest",
    version="1.0.0",
    lifespan=lifespan,
)


class PurchaseRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0)


class PurchaseResponse(BaseModel):
    purchase_id: str
    product_id: str
    quantity: int
    status: str


@app.get("/health")
def health_check():
    return {
        "service": "purchase",
        "status": "healthy",
    }


@app.post(
    "/purchases",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(request: PurchaseRequest):
    purchase_id = uuid4()

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO purchases
                        (purchase_id, product_id, quantity, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING purchase_id, product_id, quantity, status;
                    """,
                    (
                        purchase_id,
                        request.product_id,
                        request.quantity,
                        "PENDING",
                    ),
                )

                row = cursor.fetchone()

        return PurchaseResponse(
            purchase_id=str(row[0]),
            product_id=row[1],
            quantity=row[2],
            status=row[3],
        )

    except psycopg.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the purchase.",
        )


@app.get(
    "/purchases/{purchase_id}",
    response_model=PurchaseResponse,
)


@app.get(
    "/purchases",
    response_model=list[PurchaseResponse],
)
def get_all_purchases():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT purchase_id, product_id, quantity, status
                    FROM purchases
                    ORDER BY created_at DESC;
                    """
                )
                rows = cursor.fetchall()

        return [
            PurchaseResponse(
                purchase_id=str(row[0]),
                product_id=row[1],
                quantity=row[2],
                status=row[3],
            )
            for row in rows
        ]

    except psycopg.Error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve purchases.",
        )

def get_purchase(purchase_id: str):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT purchase_id, product_id, quantity, status
                    FROM purchases
                    WHERE purchase_id = %s;
                    """,
                    (purchase_id,),
                )
                row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Purchase not found.",
            )

        return PurchaseResponse(
            purchase_id=str(row[0]),
            product_id=row[1],
            quantity=row[2],
            status=row[3],
        )

    except HTTPException:
        raise

    except psycopg.Error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve the purchase.",
        )
class PurchaseStatusUpdate(BaseModel):
    status: str = Field(
        pattern="^(PENDING|CONFIRMED|CANCELLED)$"
    )


@app.patch(
    "/purchases/{purchase_id}/status",
    response_model=PurchaseResponse,
)
def update_purchase_status(
    purchase_id: str,
    request: PurchaseStatusUpdate,
):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE purchases
                    SET status = %s
                    WHERE purchase_id = %s
                    RETURNING purchase_id, product_id, quantity, status;
                    """,
                    (request.status, purchase_id),
                )
                row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Purchase not found.",
            )

        return PurchaseResponse(
            purchase_id=str(row[0]),
            product_id=row[1],
            quantity=row[2],
            status=row[3],
        )

    except HTTPException:
        raise

    except psycopg.Error:
        raise HTTPException(
            status_code=500,
            detail="Could not update the purchase status.",
        )