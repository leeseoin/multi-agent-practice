"""
Gemma-3 4B 채팅 API 서버

포트: 8081
엔드포인트:
    - GET /health : 서버 상태
    - POST /v1/chat/completions : 채팅
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_cpp import Llama
import uvicorn

from schemas import (
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
)

MODEL_PATH = "/Users/iseoin/Python_Project/multi-agent/gemma-3-4b-it-q4_0.gguf"

llm: Llama | None = None
model_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm, model_loaded

    print(f"모델 로딩 중: {MODEL_PATH}")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_threads=4,
        n_gpu_layers=-1,
        verbose=True
    )
    model_loaded = True
    print("모델 로딩 완료!")

    yield

    llm = None
    model_loaded = False


app = FastAPI(
    title="Gemma-3 4B Chat API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_gemma3_prompt(messages: list[ChatMessage]) -> str:
    """
    메시지 → Gemma-3 프롬프트 변환
    아래에 있는 프롬프트 방식은 gemma-3-4b-it_chatTamplate.json을 따름.
    출처: https://huggingface.co/google/gemma-3-4b-it/blob/main/chat_template.json
    """
    prompt = ""

    for msg in messages:
        text = msg.get_text_content()

        if msg.role == "system":
            prompt += f"<start_of_turn>system\n[시스템 지시사항]\n{text}<end_of_turn>\n"
        elif msg.role == "user":
            prompt += f"<start_of_turn>user\n{text}<end_of_turn>\n"
        elif msg.role == "assistant":
            prompt += f"<start_of_turn>model\n{text}<end_of_turn>\n"

    prompt += "<start_of_turn>model\n"
    return prompt


@app.get("/health")
async def health_check():
    return {
        "status": "ok" if model_loaded else "loading",
        "model_loaded": model_loaded,
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if not model_loaded or llm is None:
        raise HTTPException(status_code=503, detail="모델 로딩 중")

    prompt = build_gemma3_prompt(request.messages)

    output = llm(
        prompt=prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        stop=request.stop or ["<end_of_turn>", "<start_of_turn>"],
    )

    return ChatCompletionResponse(
        message=ChatMessage(role="system", content=output["choices"][0]["text"].strip()),
        usage=output.get("usage", {})
    )


if __name__ == "__main__":
    uvicorn.run(
        "serving-gemma-3-4b-it-gguf:app",
        host="localhost",
        port=8081,
        reload=True
    )
