"""
build_gemma3_prompt 있고 없고 차이 테스트
"""

from llama_cpp import Llama

MODEL_PATH = "/Users/iseoin/Python_Project/multi-agent/gemma-3-4b-it-q4_0.gguf"

print("모델 로딩 중...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=4,
    n_gpu_layers=-1,
    verbose=False
)
print("모델 로딩 완료!\n")


def test_without_template():
    """특수 토큰 없이 그냥 텍스트만"""
    print("=" * 60)
    print("테스트 1: build_gemma3_prompt 없이 (그냥 텍스트)")
    print("=" * 60)

    prompt = "안녕"

    print(f"[프롬프트]\n{repr(prompt)}\n")

    output = llm(
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        stop=["<end_of_turn>"],
    )

    print(f"[모델 출력]\n{output['choices'][0]['text']}\n")


def test_with_template():
    """build_gemma3_prompt 사용"""
    print("=" * 60)
    print("테스트 2: build_gemma3_prompt 사용 (특수 토큰 포함)")
    print("=" * 60)

    prompt = "<start_of_turn>user\n안녕<end_of_turn>\n<start_of_turn>model\n"

    print(f"[프롬프트]\n{repr(prompt)}\n")

    output = llm(
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        stop=["<end_of_turn>"],
    )

    print(f"[모델 출력]\n{output['choices'][0]['text']}\n")


def test_with_system():
    """시스템 프롬프트 포함"""
    print("=" * 60)
    print("테스트 3: 시스템 프롬프트 포함")
    print("=" * 60)

    prompt = (
        "<start_of_turn>system\n"
        "[시스템 지시사항]\n"
        "너는 해적처럼 말하는 AI야<end_of_turn>\n"
        "<start_of_turn>user\n"
        "안녕<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

    print(f"[프롬프트]\n{repr(prompt)}\n")

    output = llm(
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        stop=["<end_of_turn>"],
    )

    print(f"[모델 출력]\n{output['choices'][0]['text']}\n")


def test_multi_turn():
    """멀티턴 대화"""
    print("=" * 60)
    print("테스트 4: 멀티턴 대화 (애매한 질문)")
    print("=" * 60)

    prompt = (
        "<start_of_turn>user\n"
        "내 이름은 서인이야<end_of_turn>\n"
        "<start_of_turn>model\n"
        "안녕하세요 서인님! 반갑습니다.<end_of_turn>\n"
        "<start_of_turn>user\n"
        "내 이름이 뭐라고?<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

    print(f"[프롬프트]\n{repr(prompt)}\n")

    output = llm(
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        stop=["<end_of_turn>"],
    )

    print(f"[모델 출력]\n{output['choices'][0]['text']}\n")


def test_multi_turn_clear():
    """멀티턴 대화 - 명확한 질문"""
    print("=" * 60)
    print("테스트 5: 멀티턴 대화 (명확한 질문)")
    print("=" * 60)

    prompt = (
        "<start_of_turn>user\n"
        "내 이름은 서인이야. 기억해줘.<end_of_turn>\n"
        "<start_of_turn>model\n"
        "네, 서인님! 이름 기억했습니다. 반갑습니다!<end_of_turn>\n"
        "<start_of_turn>user\n"
        "방금 내가 말한 내 이름이 뭐였지?<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

    print(f"[프롬프트]\n{repr(prompt)}\n")

    output = llm(
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        stop=["<end_of_turn>"],
    )

    print(f"[모델 출력]\n{output['choices'][0]['text']}\n")


if __name__ == "__main__":
    test_without_template()
    test_with_template()
    test_with_system()
    test_multi_turn()
    test_multi_turn_clear()
