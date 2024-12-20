import random
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from fastapi.middleware.cors import CORSMiddleware

# Create the FastAPI instance
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Input schema for creating transactions (excludes id and timestamp)
class CreateTransaction(BaseModel):
    type: str
    amount: float
    status: str
    details: Optional[str] = None


# Response schema (includes all fields)
class Transaction(CreateTransaction):
    id: str
    timestamp: str


# In-memory transaction storage
transactions: List[Transaction] = []

# Simulate transaction status updates in the background
async def update_transaction_status(transaction_id: str):
    await asyncio.sleep(random.randint(1, 3))  # Random delay between 3 and 10 seconds
    for transaction in transactions:
        if transaction.id == transaction_id and transaction.status == "pending":
            num = random.randint(1, 4)
            transaction.status = "failed" if num == 2 else "approved"
            print(f"Transaction {transaction_id} updated to {transaction.status}")
            return
    print(f"Transaction {transaction_id} not found or already processed.")

@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: CreateTransaction, background_tasks: BackgroundTasks):
    new_transaction = Transaction(
        id=str(uuid.uuid4()),  # Generate unique ID
        timestamp=datetime.now().isoformat(),  # Generate current timestamp
        **transaction.model_dump()  # Unpack validated input fields
    )
    transactions.append(new_transaction)
    background_tasks.add_task(update_transaction_status, new_transaction.id)  # Add background task
    return new_transaction

@app.get("/transactions/pending")
async def get_pending_transactions():
    pending = [t for t in transactions if t.status == "pending"]
    return pending

@app.put("/transactions/{transaction_id}")
async def update_transaction_status_api(transaction_id: str, status: str):
    for transaction in transactions:
        if transaction.id == transaction_id:
            transaction.status = status
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.get("/transactions")
async def get_all_transactions():
    return transactions
