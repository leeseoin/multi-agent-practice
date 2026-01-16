"""
2단계: 함수 실행 연동: LLM 출력 파싱 → 실제 함수 실행
3단계: 함수 실행 연동 + 자연어 응답 생성 테스트

목표:
- LLM 출력을 파싱해서 실제 함수를 실행하고 결과를 받아오기
- 함수 결과를 자연어로 변환해서 사용자에게 응답
"""

import json
import re
from llama_cpp import Llama

# create_dataset.py에서 함수들 import
from create_dataset import (
    show_cart,
    search_product,
    add_to_cart,
    remove_from_cart,
    view_order_history,
    view_order_details,
    view_user_profile,
    search_policy_info,
)

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

# --------------------------------------------------------------------------
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


def generate_response(llm, user_query: str, func_result: dict) -> str:
    """함수 결과를 자연어 응답으로 변환"""
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
전체 파이프라인 테스트: 질문 → LLM → 파싱 → 함수 실행 → 자연어 응답
"""
def test_full_pipeline(llm, user_query: str):
    print("=" * 60)
    print(f"[사용자 질문] {user_query}")
    print("=" * 60)

    # 1. LLM에게 함수 결정 요청
    prompt = build_function_calling_prompt(user_query)
    output = llm(
        prompt=prompt,
        max_tokens=150,
        temperature=0.1,
        stop=["<end_of_turn>"],
    )
    print(output)
    llm_response = output["choices"][0]["text"].strip()
    print(f"\n[1. LLM 응답]\n{llm_response}")

    # 2. LLM 출력 파싱
    func_name, params = parse_llm_output(llm_response)
    print(f"\n[2. 파싱 결과]")
    print(f"   함수: {func_name}")
    print(f"   파라미터: {params}")

    if func_name is None:
        print("\n❌ 함수를 파싱할 수 없습니다.")
        return

    # 3. 함수 실행
    result = execute_function(func_name, params)
    print(f"\n[3. 함수 실행 결과]")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 4. 자연어 응답 생성
    response = generate_response(llm, user_query, result)
    print(f"\n[4. 최종 응답]")
    print(response)

    return response


def main():
    print("모델 로딩 중...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_threads=4,
        n_gpu_layers=-1,
        verbose=False
    )
    print("모델 로딩 완료!\n")

    # 테스트 질문들
    test_queries = [
        "내 장바구니 보여줘",
        "노트북 검색해줘",
        "주문 내역 확인하고 싶어",
        "반품 어떻게 해?",
    ]

    for query in test_queries:
        test_full_pipeline(llm, query)
        print("\n")


if __name__ == "__main__":
    main()
