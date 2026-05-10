from fastapi import FastAPI

app = FastAPI(title="pareto-tagger")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}
