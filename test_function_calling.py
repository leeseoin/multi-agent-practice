"""
1단계: Gemma-3 4B Function Calling 테스트

목표: 사용자 질문을 보고 어떤 함수를 호출해야 하는지 판단할 수 있는지에 대한 판단 여부 가능성 확인을 위한 테스트 코드
"""

from llama_cpp import Llama

MODEL_PATH = "/Users/iseoin/Python_Project/multi-agent/gemma-3-4b-it-q4_0.gguf"

# 사용 가능한 함수 목록
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

# 테스트할 사용자 질문들
TEST_QUERIES = [
    "내 장바구니 보여줘",
    "노트북 검색해줘",
    "주문 내역 확인하고 싶어",
    "반품 어떻게 해?",
    "내 정보 보여줘",
    "현재 user_id의 상세 정보 보여줘",
    
]

"""
Function Calling용 프롬프트 생성
"""
def build_function_calling_prompt(user_query: str) -> str:
    prompt = f"""<start_of_turn>user
[시스템 지시사항]
너는 쇼핑몰 AI 어시스턴트야. 사용자의 질문을 보고 어떤 함수를 호출해야 하는지 결정해.

사용 가능한 함수:
{AVAILABLE_FUNCTIONS}

사용자의 현재 user_id는 "U001"이야.

아래 형식으로만 답변해:
함수: 함수명
파라미터: {{"param1": "value1", "param2": "value2"}}

사용자 질문: {user_query}<end_of_turn>
<start_of_turn>model
"""
    return prompt


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

    for query in TEST_QUERIES:
        print("=" * 60)
        print(f"[사용자 질문] {query}")
        print("=" * 60)

        prompt = build_function_calling_prompt(query)

        output = llm(
            prompt=prompt,
            max_tokens=150,
            temperature=0.1,  # 낮은 temperature로 일관된 출력
            stop=["<end_of_turn>"],
        )

        response = output["choices"][0]["text"].strip()
        print(f"[모델 응답]\n{response}\n")


if __name__ == "__main__":
    main()
