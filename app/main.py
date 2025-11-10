import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import AskRequest, AskResponse
from .pipeline import answer_question
from .retriever import invalidate_cache, fetch_messages
from .config import settings

app = FastAPI(title="Member QA Service", version="1.0.0")
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")  # optional convenience

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
async def ask_post(payload: AskRequest):
    resp = await answer_question(payload.question)
    return JSONResponse(resp.dict())

@app.get("/ask", response_model=AskResponse)
async def ask_get(question: str = Query(..., description="Natural-language question")):
    resp = await answer_question(question)
    return JSONResponse(resp.dict())

@app.post("/cache/refresh")
async def cache_refresh():
    invalidate_cache()
    return {"status": "refreshed"}
    
    
@app.get("/debug/search")
async def debug_search(q: str = Query(..., description="substring to search")):
    try:
        msgs = await fetch_messages()
    except Exception as e:
        return {"query": q, "error": str(e)}
    hits = [m for m in msgs if q.lower() in (m.text or "").lower()]
    return {
        "query": q,
        "count": len(hits),
        "examples": [
            {"id": m.id, "member": m.member_name, "snippet": (m.text or "")[:200]}
            for m in hits[:10]
        ],
    }

@app.get("/debug/names")
async def debug_names():
    msgs = await fetch_messages()
    names = sorted({m.member_name for m in msgs if m.member_name})
    return {"count": len(names), "names": names[:200]}  # trim if huge

@app.get("/debug/find")
async def debug_find(member: str, q: str):
    msgs = await fetch_messages()
    hits = [m for m in msgs if m.member_name and member.lower() in m.member_name.lower() and q.lower() in m.text.lower()]
    return {"member": member, "query": q, "count": len(hits),
            "examples": [{"id": m.id, "snippet": m.text[:220]} for m in hits[:10]]}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
