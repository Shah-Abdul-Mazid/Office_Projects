from fastapi import FastAPI

from app.batch import run_batch
from app.schemas import BatchRequest, GenerateRequest
from app.service import generate_content

app = FastAPI(title='Transform to Liberation AI API', version='0.1.0')


@app.get('/health')
async def health() -> dict:
    return {'status': 'ok'}


@app.post('/generate')
async def generate(payload: GenerateRequest) -> dict:
    return await generate_content(payload)


@app.post('/batch')
async def batch(payload: BatchRequest) -> dict:
    return await run_batch(payload)
