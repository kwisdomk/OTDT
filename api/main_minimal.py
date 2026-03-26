from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OT Digital Twin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ot-digital-twin"}

@app.get("/test")
async def test():
    return {"message": "API is working!"}

@app.get("/")
async def root():
    return {"message": "OT Digital Twin API is running"}
