import time
import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

ALLOWED_ORIGIN = "https://dash-6mcmum.example.com"
EMAIL = "24f2008930@ds.study.iitm.ac.in"   # <-- CHANGE THIS to your logged-in email

app = FastAPI()

# 1) CORS middleware: only your one origin is allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],      # no "*"
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# 2) Header middleware: added AFTER CORS so it wraps everything,
#    including preflight (OPTIONS) responses
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response

@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        nums = [int(v) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }