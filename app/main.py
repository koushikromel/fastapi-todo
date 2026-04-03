from datetime import datetime, timezone
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def home():
    time = datetime.now(timezone.utc).isoformat()
    return f"asdfHello, world! Current time: {time}"
