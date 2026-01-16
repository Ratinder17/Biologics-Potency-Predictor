# app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

def create_app() -> FastAPI:
    """
    Application factory for FastAPI.
    Keeps app creation deterministic and testable.
    """
    app = FastAPI()

    # ---- Middleware ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # adjust for your frontend domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Routers ----
    app.include_router(api_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001, log_level="info")
