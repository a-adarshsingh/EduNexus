from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..models.tables import User
from ..services import language, llm
from .deps import current_user

router = APIRouter(prefix="/api", tags=["tools"])
P = {
 "notes": "Create clear, well-organized study notes from the following content or topic.",
 "explain": "Explain this topic simply, step by step, with an example and an analogy.",
 "simplify": "Simplify this paragraph so a beginner can understand it. Keep the meaning.",
 "summary": "Summarize the following text concisely.",
 "flashcards": "Create 8 flashcards as 'Q:' and 'A:' pairs from the following.",
 "mcq": "Create 5 multiple-choice questions (A-D) with an answer key at the end.",
 "questions": "List 8 important exam questions with short model answers.",
 "definitions": "Extract key terms and give a clear definition for each.",
 "vocabulary": "List difficult vocabulary with simple meanings and an example sentence each.",
 "revision": "Create quick revision material: key points, important facts, and a 5-line recap.",
 "qa": "Generate 6 question-answer pairs covering the main ideas.",
 "grammar": "Correct grammar, spelling and punctuation. Keep meaning and style. Return only the corrected text.",
 "rewrite": "Rewrite the text to be clearer and more polished. Return only the result.",
 "expand": "Expand the text with more detail and examples. Return only the result.",
 "shorten": "Shorten the text, keeping key points. Return only the result.",
 "tone": "Rewrite the text in a {tone} tone. Return only the result.",
 "headings": "Suggest a title and section headings for this text.",
 "bullets": "Convert the text into concise bullet points."}

class ToolIn(BaseModel):
    kind: str
    text: str = Field(min_length=1, max_length=8000)
    language: str = "auto"
    tone: str = "professional"
    model: str | None = None

@router.post("/tools")
def run_tool(b: ToolIn, u: User = Depends(current_user)):
    if b.kind not in P: raise HTTPException(400, "Unknown tool.")
    lang = llm.out_lang(u, b.language, b.text)
    out = llm.run(P[b.kind].format(tone=b.tone), b.text, lang, b.model)
    return {"result": out, "language": lang}
