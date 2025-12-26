from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any

from module_extractor import run

app = FastAPI(title="Pulse Module Extraction API")

class ExtractRequest(BaseModel):
    urls: List[str]
    max_pages: int = 200
    per_domain_limit: int = 150

@app.post("/extract")
async def extract(req: ExtractRequest) -> Any:
    try:
        result = run(req.urls, max_pages=req.max_pages, per_domain_limit=req.per_domain_limit)
        return {"modules": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
