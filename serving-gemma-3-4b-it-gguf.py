"""
Gemma-3 4B 채팅 API 서버

포트: 8081
엔드포인트:
    - GET /health : 서버 상태
    - POST /chat/completions : 일반 채팅
    - POST /agent/chat : 쇼핑몰 에이전트용 채팅
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_cpp import Llama
import uvicorn
import json
import re

from schemas import (
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    AgentChatRequest,
    AgentChatResponse
)

# create_dataset.py에서 이커머스 함수 import
from create_dataset import (
    show_cart,               # 1.장바구니 상태 조회 함수
    search_product,          # 2.제품 검색 함수(예: "노트북")
    add_to_cart,             # 3.장바구니에 상품 추가하는 함수
    remove_from_cart,        # 4.장바구니에서 상품 제거하는 함수
    view_order_history,      # 5.주문 내역 전체 보기 함수
    view_order_details,      # 6.특정 주문의 상세 내역 보기 함수
    view_user_profile,       # 7.사용자 정보 조회 함수
    search_policy_info       # 8.약관 조회 함수

)

# 사용할 모델 경로
MODEL_PATH = "/Users/iseoin/Python_Project/multi-agent/gemma-3-4b-it-q4_0.gguf"

# 함수 이름 → 실제 함수 매핑
FUNCTION_MAP = {
    "show_cart": show_cart,
    "search_product": search_product,
    "add_to_cart": add_to_cart,
    "remove_from_cart": remove_from_cart,
    "view_order_history": view_order_history,
    "view_order_details": view_order_details,
    "view_user_profile": view_user_profile,
    "search_policy_info": search_policy_info,
}

# 사용 가능한 함수 목록 (프롬프트용)
AVAILABLE_FUNCTIONS = """
1. show_cart(user_id) - 장바구니 조회
2. search_product(keyword, category=None) - 상품 검색
3. add_to_cart(user_id, product_id, quantity=1) - 장바구니에 상품 추가
4. remove_from_cart(user_id, keyword=None, product_id=None) - 장바구니에서 상품 제거
5. view_order_history(user_id) - 주문 내역 조회
6. view_order_details(user_id, order_id) - 특정 주문 상세 조회
7. view_user_profile(user_id) - 내 정보 조회
8. search_policy_info(keyword) - 정책/약관 검색 (주문취소, 반품, 환불, 배송 등)
"""

# 현재 사용자 ID (실제 서비스에서는 로그인 세션에서 가져옴)
# 하지만 지금은 단순 테스트이기 때문에 사용자 정보를 하드 코딩하는 거임
CURRENT_USER_ID = "U001"

llm: Llama | None = None
model_loaded = False                         # 기본적으로 모델은 업로드가 안되어 있는 상태기 때문에 False


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
    model_loaded = True                      # 모델이 업로드가 되면 False → True로 변환
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

# --------------------------------------------------------------------------
"""
함수 리스트(6)
1.build_gemma3_prompt()
2.build_function_calling_prompt()
3.parse_llm_output()
4.execute_function()
5.build_response_prompt()
6.generate_response()
"""
# --------------------------------------------------------------------------
"""
메시지 → Gemma-3 프롬프트 변환
아래에 있는 프롬프트 방식은 gemma-3-4b-it_chatTamplate.json을 따름.
출처: https://huggingface.co/google/gemma-3-4b-it/blob/main/chat_template.json
"""
def build_gemma3_prompt(messages: list[ChatMessage]) -> str:
    prompt = ""

    for msg in messages:
        text = msg.get_text_content()

        if msg.role == "user":
            prompt += f"<start_of_turn>user\n[시스템 지시사항]\n{text}<end_of_turn>\n"
        elif msg.role == "user":
            prompt += f"<start_of_turn>user\n{text}<end_of_turn>\n"
        elif msg.role == "assistant":
            prompt += f"<start_of_turn>model\n{text}<end_of_turn>\n"

    prompt += "<start_of_turn>model\n"
    return prompt

"""
Function Calling용 프롬프트 생성
"""
def build_function_calling_prompt(user_query: str) -> str:
    prompt = f"""<start_of_turn>user
[시스템 지시사항]
너는 쇼핑몰 AI 어시스턴트야. 사용자의 질문을 보고 어떤 함수를 호출해야 하는지 결정해.

사용 가능한 함수:
{AVAILABLE_FUNCTIONS}

사용자의 현재 user_id는 "{CURRENT_USER_ID}"야.

아래 형식으로만 답변해:
함수: 함수명
파라미터: {{"param1": "value1", "param2": "value2"}}

사용자 질문: {user_query}<end_of_turn>
<start_of_turn>model
"""
    return prompt
# --------------------------------------------------------------------------
"""
LLM 출력에서 함수명과 파라미터 추출

예시 입력:
"함수: show_cart
파라미터: {}"

반환: ("show_cart", {})
"""
def parse_llm_output(output: str) -> tuple[str, dict]:
    # 함수명 추출
    func_match = re.search(r"함수:\s*(\w+)", output)
    if not func_match:
        return None, {}

    func_name = func_match.group(1)

    # 파라미터 추출
    param_match = re.search(r"파라미터:\s*(\{.*\})", output, re.DOTALL)
    if param_match:
        try:
            params = json.loads(param_match.group(1))
        except json.JSONDecodeError:
            params = {}
    else:
        params = {}

    return func_name, params
# --------------------------------------------------------------------------
"""
함수 이름과 파라미터로 실제 함수 실행
"""
def execute_function(func_name: str, params: dict) -> dict:
    if func_name not in FUNCTION_MAP:
        return {"error": f"알 수 없는 함수: {func_name}"}

    func = FUNCTION_MAP[func_name]

    # user_id가 필요한 함수들에 자동으로 추가
    if func_name in ["show_cart", "add_to_cart", "remove_from_cart",
                    "view_order_history", "view_order_details", "view_user_profile"]:
        if "user_id" not in params:
            params["user_id"] = CURRENT_USER_ID

    try:
        result = func(**params)
        return result
    except Exception as e:
        return {"error": str(e)}
# --------------------------------------------------------------------------
"""
3단계: 함수 결과를 자연어로 변환
"""
def build_response_prompt(user_query: str, func_result: dict) -> str:
    result_str = json.dumps(func_result, ensure_ascii=False, indent=2)

    prompt = f"""<start_of_turn>user
[시스템 지시사항]
너는 쇼핑몰 '상준몰'의 친절한 AI 상담사야.
아래 함수 실행 결과를 보고 사용자에게 친절하고 자연스럽게 답변해줘.
- 가격은 천 단위로 콤마를 넣어서 보여줘 (예: 1,290,000원)
- 너무 길지 않게 핵심만 전달해줘

[사용자 질문]
{user_query}

[함수 실행 결과]
{result_str}

위 결과를 바탕으로 사용자에게 답변해줘:<end_of_turn>
<start_of_turn>model
"""
    return prompt
# --------------------------------------------------------------------------
"""
함수 결과를 자연어 응답으로 변환
"""
def generate_response(llm, user_query: str, func_result: dict) -> str:

    prompt = build_response_prompt(user_query, func_result)

    output = llm(
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
        stop=["<end_of_turn>"],
    )

    return output["choices"][0]["text"].strip()
# --------------------------------------------------------------------------

"""
API Endpoint list
1./health
2./chat/completions
3./agent/chat
"""
@app.get("/health")
async def health_check():
    return {
        "status": "ok" if model_loaded else "loading",
        "model_loaded": model_loaded,
    }


@app.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    # 모델이 로딩되지 않았으면 에러 반환
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
        message=ChatMessage(role="user", content=output["choices"][0]["text"].strip()),
        usage=output.get("usage", {})
    )

@app.post("/agent/chat/", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    # 모델이 로딩되지 않았으면 에러 반환
    if not model_loaded or llm is None:
        raise HTTPException(status_code=503, detail="모델 로딩 중")
    # 사용자 질문
    user_query = request.message
    print(user_query)
    # 1.사용자의 질문 의도 파악하기 위해 function calling 함수 사용
    prompt = build_function_calling_prompt(user_query)
    print(prompt)
    # 2.Gemma 호출하여 함수 결정
    output = llm(
        prompt=prompt,
        max_tokens=150,
        temperature=0.3,
        stop=["<end_of_turn>"]
    )
    llm_response = output["choices"][0]["text"].strip()
    print(llm_response)
    # 3.Gemma3 답변 파싱 후 func, 파라미터(params) 추출
    func_name, params = parse_llm_output(llm_response)
    print(func_name, params)
    if func_name is None:
        return AgentChatResponse(response="죄송합니다. function calling이 실패되었습니다.")
    # 4.func 실행
    result = execute_function(func_name, params)
    print(result)
    # 5.자연어 응답 Gemma3 모델이 생성
    response = generate_response(llm, user_query, result)
    print(response)
    # 6. 반환
    return AgentChatResponse(response=response)


if __name__ == "__main__":
    uvicorn.run(
        "serving-gemma-3-4b-it-gguf:app",
        host="localhost",
        port=8081,
        reload=True
    )
