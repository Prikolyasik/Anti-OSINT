from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.email_check import router as email_router
from routers.fake_data import router as fake_router
from routers.pdf_report import router as pdf_router

app = FastAPI(title="Digital Alibi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router)
app.include_router(fake_router)
app.include_router(pdf_router)

@app.get("/")
def root():
    return {"message": "Digital Alibi API работает!"}