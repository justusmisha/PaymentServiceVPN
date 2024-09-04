import argparse

import uvicorn
from fastapi import FastAPI

from app.api import payment_router

app = FastAPI()


app.include_router(payment_router, prefix="/api/payment")


@app.on_event("startup")
async def startup_event():
    # await rabbit_mq.connect()
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI app with optional docs")
    parser.add_argument("--docs", type=bool, default=True, help="Show or hide docs")
    args = parser.parse_args()

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, docs_url="/docs" if args.docs else None)
