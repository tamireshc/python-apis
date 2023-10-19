from fastapi import FastAPI

from api.endpoints import curso

app = FastAPI(
    title="Api Cursos",
    version="0.0.1",
    description="Uma api para aprender fastapi",
)
app.include_router(curso.router, tags=["cursos"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)