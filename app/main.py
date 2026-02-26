import uuid
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from docx import Document

from app.prompts.templates import build_prompt
from app.services.llm_service import generate_article

app = FastAPI(title="SEO Bot — Деликатная Терапия Души")

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
    aeo_questions: str = ""
    meta_title: str = ""
    meta_description: str = ""
    competitors: str = ""
    additional: str = ""


class ChatMessage(BaseModel):
    session_id: str
    message: str


class BriefTextRequest(BaseModel):
    text: str


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
    """Generate a new article from a brief form."""
    session_id = str(uuid.uuid4())

    user_prompt = build_prompt(
        topic=req.topic,
        content_type=req.content_type,
        main_keywords=req.main_keywords,
        lsi_keywords=req.lsi_keywords,
        word_count=req.word_count,
        structure=req.structure,
        aeo_questions=req.aeo_questions,
        meta_title=req.meta_title,
        meta_description=req.meta_description,
        competitors=req.competitors,
        additional=req.additional,
    )

    messages = [{"role": "user", "content": user_prompt}]
    sessions[session_id] = messages.copy()

    try:
        result = generate_article(messages)
        sessions[session_id].append({"role": "assistant", "content": result})
        return {"text": result, "session_id": session_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/generate-from-brief")
async def generate_from_brief(req: BriefTextRequest):
    """Generate an article from uploaded brief text."""
    session_id = str(uuid.uuid4())

    user_prompt = (
        "Вот ТЗ на статью. Напиши статью строго по этому ТЗ.\n\n"
        "ВАЖНО:\n"
        "- Соблюдай указанную структуру (H2/H3 заголовки)\n"
        "- Используй все ключевые слова в точной форме и указанной частотности\n"
        "- Соблюдай указанный объём в символах без пробелов\n"
        "- Обеспечь логические переходы между всеми разделами\n"
        "- Верни результат в формате ---META--- и ---ARTICLE---\n\n"
        f"{req.text}"
    )

    messages = [{"role": "user", "content": user_prompt}]
    sessions[session_id] = messages.copy()

    try:
        result = generate_article(messages)
        sessions[session_id].append({"role": "assistant", "content": result})
        return {"text": result, "session_id": session_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/chat")
async def chat(req: ChatMessage):
    """Continue conversation for article refinement."""
    if req.session_id not in sessions:
        return JSONResponse(status_code=404, content={"error": "Сессия не найдена. Сгенерируйте статью заново."})

    sessions[req.session_id].append({"role": "user", "content": req.message})

    try:
        result = generate_article(sessions[req.session_id])
        sessions[req.session_id].append({"role": "assistant", "content": result})
        return {"text": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
