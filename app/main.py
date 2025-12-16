from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.children import router as children_router

app = FastAPI(title="MEDKids OrderUp Backend")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(children_router)

@app.get("/")
def health_check():
    return {"status": "ok"}