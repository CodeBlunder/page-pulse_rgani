
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auditor import audit_url
from urllib.parse import urlparse

app = FastAPI(title="Page Pulse API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False

@app.get("/audit")
async def audit(url: str = Query(..., description="URL to audit")):
    if not is_valid_url(url):
        return {"error": "Invalid URL. Must start with http:// or https://"}
    
    result = await audit_url(url)
    return result
