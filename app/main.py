import uuid
import json
import io
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from docx import Document

from app.prompts.templates import build_prompt
from app.services.llm_service import generate_article_stream

app = FastAPI(title="SEO Bot — Династия")

# In-memory session storage (single user)
sessions: dict[str, list[dict]] = {}

app.mount("/static", StaticFiles(directory="static"), name="static")


class ArticleRequest(BaseModel):
    topic: str
    content_type: str = "article"
    main_keywords: str
    lsi_keywords: str = ""
    word_count: int = 3000
    structure: str = ""
    competitors: str = ""
    additional: str = ""


class ChatMessage(BaseModel):
    session_id: str
    message: str


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/api/upload-brief")
async def upload_brief(file: UploadFile = File(...)):
    """Parse an uploaded DOCX/TXT brief and return its text content."""
    content = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif filename.endswith(".txt"):
        text = content.decode("utf-8")
    else:
        return {"error": "Поддерживаются только .docx и .txt файлы"}

    return {"text": text}


@app.post("/api/generate")
async def generate(req: ArticleRequest):
    """Generate a new article from a brief form. Returns a streaming response."""
    session_id = str(uuid.uuid4())

    user_prompt = build_prompt(
        topic=req.topic,
        content_type=req.content_type,
        main_keywords=req.main_keywords,
        lsi_keywords=req.lsi_keywords,
        word_count=req.word_count,
        structure=req.structure,
        competitors=req.competitors,
        additional=req.additional,
    )

    messages = [{"role": "user", "content": user_prompt}]
    sessions[session_id] = messages.copy()

    async def stream():
        full_response = ""
        async for chunk in generate_article_stream(messages):
            full_response += chunk
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"

        sessions[session_id].append({"role": "assistant", "content": full_response})
        yield f"data: {json.dumps({'done': True, 'session_id': session_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


class BriefTextRequest(BaseModel):
    text: str


@app.post("/api/generate-from-brief")
async def generate_from_brief(req: BriefTextRequest):
    """Generate an article from uploaded brief text. Returns a streaming response."""
    session_id = str(uuid.uuid4())

    user_prompt = f"Вот ТЗ на статью. Напиши статью строго по этому ТЗ:\n\n{req.text}"

    messages = [{"role": "user", "content": user_prompt}]
    sessions[session_id] = messages.copy()

    async def stream():
        full_response = ""
        async for chunk in generate_article_stream(messages):
            full_response += chunk
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"

        sessions[session_id].append({"role": "assistant", "content": full_response})
        yield f"data: {json.dumps({'done': True, 'session_id': session_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/api/chat")
async def chat(req: ChatMessage):
    """Continue conversation for article refinement."""
    if req.session_id not in sessions:
        return {"error": "Сессия не найдена. Сгенерируйте статью заново."}

    sessions[req.session_id].append({"role": "user", "content": req.message})

    async def stream():
        full_response = ""
        async for chunk in generate_article_stream(sessions[req.session_id]):
            full_response += chunk
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"

        sessions[req.session_id].append({"role": "assistant", "content": full_response})
        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/sessions")
async def list_sessions():
    """List active sessions."""
    return {
        sid: {"messages_count": len(msgs), "topic": msgs[0]["content"][:100]}
        for sid, msgs in sessions.items()
    }
