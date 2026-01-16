## 1. 프로젝트 구조(마지막 업데이트 일시: 2026-01-16 18:10)

```
.
├── .claude/
│   └── settings.local.json                        # 클로드 코드 세팅
├── data-archive/                                  # 내가 타 프로젝트에서 사용했던 api 명세서 dir
│   ├── kobweb-api-docs.json                       # 내가 타 프로젝트에서 사용했던 api 명세서 json 파일
│   └── kobweb-api-docs.toon                       # 내가 타 프로젝트에서 사용했던 api 명세서 toon 파일
├── multi-agent                                    # uv 가상환경
├── test-funcgemma/                                # functiongemma 모델 테스트 dir
│   ├── funtiongemma-270m-it-Q4_K_M.gguf           # functiongemma gguf 모델
│   └── serving-model-functiongemma.py             # functiongemma gguf 모델 서빙 파이썬 코드
├── test-gpt-api/                                  # gpt api 테스트 dir
│   ├── img-files                                  # 테스트용 이미지 파일 dir
│   ├── .env
│   ├── png-to-pdf.py                              # png to pdf convert 코드 파일
│   └── test-gpt-api.py                            # gpt api 테스트 코드
├── CLAUDE.md
├── create-dataset.py
├── gemma-3-4b-it_chatTamplate.json
├── gemma-3-4b-it-q4_0.gguf
├── multiturn.py
├── schemas.py
└── serving-gemma-3-4b-it-gguf.py
```

## 2026-01-16 (2)

### 2단계 완료: 함수 실행 연동

#### 1. 테스트 결과 (test_function_execution.py)

LLM 출력을 파싱해서 실제 함수를 실행하고 결과를 받아오는 전체 파이프라인 테스트 성공!

| 질문 | 함수 | 파라미터 | 실행 결과 |
|------|------|----------|-----------|
| "내 장바구니 보여줘" | `show_cart` | `{}` | ✅ 장바구니 2개 상품 조회 |
| "노트북 검색해줘" | `search_product` | `{"keyword": "노트북"}` | ✅ 노트북 1개 검색됨 |
| "주문 내역 확인하고 싶어" | `view_order_history` | `{"user_id": "U001"}` | ✅ 주문 2건 조회 |
| "반품 어떻게 해?" | `search_policy_info` | `{"keyword": "반품"}` | ✅ 반품 정책 3개 조회 |

---

#### 2. llama-cpp 출력 구조 (output["choices"][0]["text"])

llama-cpp는 **OpenAI API 형식**을 따름:

```python
output = llm(prompt="...")

# output 구조:
{
    "choices": [
        {
            "text": "모델이 생성한 텍스트",  # ← 우리가 원하는 것
            "index": 0,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 30,
        "total_tokens": 80
    }
}
```

| 키 | 설명 |
|----|------|
| `output["choices"]` | 생성된 응답 배열 |
| `output["choices"][0]["text"]` | 실제 생성된 텍스트 |
| `output["usage"]` | 토큰 사용량 |

**참고**: Gemma-3의 chat_template은 **입력** 형식, llama-cpp 출력 구조는 **결과** 형식. 서로 다른 레이어!

---

#### 3. 파라미터 추출 동작 (아직 불확실한 부분)

LLM이 파라미터를 추출하는 패턴:

| 질문 | 파라미터 | 추출 방식 |
|------|----------|-----------|
| "노트북 검색해줘" | `{"keyword": "노트북"}` | 질문에서 "노트북" 추출 |
| "반품 어떻게 해?" | `{"keyword": "반품"}` | 질문에서 "반품" 추출 |
| "내 장바구니 보여줘" | `{}` | 추출할 정보 없음 |
| "주문 내역 확인하고 싶어" | `{"user_id": "U001"}` | 프롬프트에서 알려준 정보 사용 |

**의문점**:
- LLM이 user_id를 파라미터에 넣을 때도 있고 안 넣을 때도 있음 (일관성 없음)
- 하지만 코드에서 자동으로 채워주기 때문에 실제로는 문제없음:
```python
if "user_id" not in params:
    params["user_id"] = CURRENT_USER_ID  # 자동 추가
```

---

#### 4. 현재 파이프라인 구조

```
[사용자 질문]
     │
     ▼
[build_function_calling_prompt()] ─────────────────┐
     │                                             │
     ▼                                             │
[LLM 호출] ─────────────────────────────────────────┤
     │                                             │
     ▼                                             │
[parse_llm_output()] ──────────────────────────────┤
     │  함수명, 파라미터 추출                       │
     ▼                                             │
[execute_function()] ──────────────────────────────┤
     │  create_dataset.py의 함수 실행              │
     ▼                                             │
[결과 반환] ───────────────────────────────────────┘
     │
     ▼
[TODO: 자연어 응답 생성] ← 3단계에서 구현
```

---

#### 5. TODO 업데이트

- [x] 1단계: Function Calling 테스트 ✅
- [x] 2단계: 함수 실행 연동 ✅
- [ ] 3단계: 응답 생성 - 함수 결과를 자연어로 변환
- [ ] 4단계: 전체 파이프라인 통합

---

## 2026-01-16

### 쇼핑몰 에이전트 Function Calling 구현 시작

#### 1. 오늘 진행한 테스트들

##### 1-1. 프롬프트 템플릿 테스트 (test_prompt_diff.py)

`build_gemma3_prompt()` 함수가 왜 필요한지 실험으로 확인.

| 테스트 | 설명 | 결과 |
|--------|------|------|
| 테스트 1 | 특수 토큰 없이 "안녕"만 | ❌ 이상한 응답 ("저는 챗봇입니다...") |
| 테스트 2 | `<start_of_turn>` 토큰 포함 | ✅ 정상 대화 응답 |
| 테스트 3 | 시스템 프롬프트 (해적처럼) | ✅ 해적 말투로 응답 |
| 테스트 4 | 멀티턴 (애매한 질문) | ⚠️ 이름 기억 못함 |
| 테스트 5 | 멀티턴 (명확한 질문) | ✅ 이름 기억함 |

**결론**: 특수 토큰이 없으면 LLM은 대화 구조를 이해 못함. `build_gemma3_prompt()`는 필수!

##### 1-2. Function Calling 테스트 (test_function_calling.py)

Gemma-3 4B가 사용자 질문을 보고 어떤 함수를 호출해야 하는지 판단할 수 있는지 테스트.

| 사용자 질문 | 모델 응답 | 정답 |
|------------|----------|------|
| "내 장바구니 보여줘" | `show_cart` | ✅ |
| "노트북 검색해줘" | `search_product(keyword: 노트북)` | ✅ |
| "주문 내역 확인하고 싶어" | `view_order_history` | ✅ |
| "반품 어떻게 해?" | `search_policy_info(keyword: 반품)` | ✅ |
| "내 정보 보여줘" | `view_user_profile` | ✅ |

**결론**: Gemma-3 4B는 Function Calling 결정 능력이 있음! → 2단계 진행 가능

---

#### 2. Gemma-3 Chat Template 상세 분석

##### 2-1. 핵심: `<start_of_turn>system`은 존재하지 않음!

Gemma-3의 chat_template을 보면:

```jinja2
{%- if messages[0]['role'] == 'system' -%}
    {%- set first_user_prefix = messages[0]['content'] + '\n\n' -%}
    {%- set loop_messages = messages[1:] -%}
{%- endif -%}

{%- for message in loop_messages -%}
    {%- if (message['role'] == 'assistant') -%}
        {%- set role = "model" -%}
    {%- else -%}
        {%- set role = message['role'] -%}
    {%- endif -%}
    {{ '<start_of_turn>' + role + '\n' + (first_user_prefix if loop.first else "") }}
```

##### 2-2. Gemma-3에서 지원하는 토큰

| role | 토큰 | 설명 |
|------|------|------|
| `user` | `<start_of_turn>user` | ✅ 존재 |
| `assistant` | `<start_of_turn>model` | ✅ 존재 (model로 변환됨!) |
| `system` | ❌ 없음 | 첫 user 메시지 앞에 합쳐버림 |

##### 2-3. system role 처리 방식

**입력:**
```json
[
  {"role": "system", "content": "너는 친절한 AI야"},
  {"role": "user", "content": "안녕"}
]
```

**공식 chat_template 변환 결과:**
```
<bos><start_of_turn>user
너는 친절한 AI야

안녕<end_of_turn>
<start_of_turn>model
```

→ system 내용이 첫 번째 user 턴 앞에 붙음 (별도 턴 아님!)

##### 2-4. 잘못된 사용 vs 올바른 사용

**❌ 잘못된 방식 (존재하지 않는 토큰):**
```
<start_of_turn>system
너는 쇼핑몰 AI야<end_of_turn>
<start_of_turn>user
안녕<end_of_turn>
```

**✅ 올바른 방식:**
```
<start_of_turn>user
[시스템 지시사항]
너는 쇼핑몰 AI야

안녕<end_of_turn>
```

또는 공식 방식대로:
```
<start_of_turn>user
너는 쇼핑몰 AI야

안녕<end_of_turn>
```

---

#### 3. 쇼핑몰 에이전트 파이프라인 설계

##### 3-1. 전체 흐름

```
[사용자]                    [에이전트]                    [LLM]
    │                           │                          │
    │  "내 장바구니 보여줘"      │                          │
    │  ────────────────────────>│                          │
    │                           │                          │
    │                  1. Function Calling 요청            │
    │                           │  ───────────────────────>│
    │                           │                          │
    │                           │  "show_cart(U001)"       │
    │                           │  <───────────────────────│
    │                           │                          │
    │                  2. 실제 함수 실행                    │
    │                  show_cart("U001")                   │
    │                  → {"cart_items": [...]}             │
    │                           │                          │
    │                  3. 응답 생성 요청                    │
    │                           │  ───────────────────────>│
    │                           │                          │
    │                           │  "장바구니에 노트북이..." │
    │                           │  <───────────────────────│
    │                           │                          │
    │  "장바구니에 노트북이..."  │                          │
    │  <────────────────────────│                          │
```

##### 3-2. 사용 가능한 함수 (create-dataset.py)

| 함수 | 설명 | 파라미터 |
|------|------|----------|
| `show_cart(user_id)` | 장바구니 조회 | user_id |
| `search_product(keyword, category)` | 상품 검색 | keyword, category(선택) |
| `add_to_cart(user_id, product_id, quantity)` | 장바구니 추가 | user_id, product_id, quantity |
| `remove_from_cart(user_id, keyword, product_id)` | 장바구니 제거 | user_id, keyword/product_id |
| `view_order_history(user_id)` | 주문 내역 | user_id |
| `view_order_details(user_id, order_id)` | 주문 상세 | user_id, order_id |
| `view_user_profile(user_id)` | 내 정보 | user_id |
| `search_policy_info(keyword)` | 정책 검색 | keyword |

---

#### 4. TODO (다음 단계)

- [x] 1단계: Function Calling 테스트 - 모델이 함수 결정 가능한지 ✅
- [ ] 2단계: 함수 실행 연동 - LLM 출력 파싱 → 실제 함수 실행
- [ ] 3단계: 응답 생성 - 함수 결과를 자연어로 변환
- [ ] 4단계: 전체 파이프라인 통합 - 질문 → 함수 결정 → 실행 → 응답

---

## 2026-01-13

### Chat Template 분석 및 현재 Workflow

#### 1. 현재 Workflow

```
[클라이언트]                      [서버]                           [LLM]
     │                              │                                │
     │  POST /v1/chat/completions   │                                │
     │  ───────────────────────────>│                                │
     │  {                           │                                │
     │    "messages": [             │                                │
     │      {"role": "user",        │                                │
     │       "content": "안녕"}     │                                │
     │    ]                         │                                │
     │  }                           │                                │
     │                              │                                │
     │                     1. schemas.py                             │
     │                     ChatCompletionRequest로 검증              │
     │                              │                                │
     │                     2. build_gemma3_prompt()                  │
     │                     JSON → 특수토큰 문자열 변환                │
     │                              │                                │
     │                              │  "<start_of_turn>user          │
     │                              │   안녕<end_of_turn>             │
     │                              │   <start_of_turn>model"        │
     │                              │  ────────────────────────────> │
     │                              │                                │
     │                              │        "안녕하세요!"            │
     │                              │  <──────────────────────────── │
     │                              │                                │
     │  {"message": {...}}          │                                │
     │  <───────────────────────────│                                │
```

#### 2. Chat Template이란?

HuggingFace 모델에는 `chat_template`이 포함되어 있음 (Jinja2 형식).
`gemma-3-4b-it_chatTamplate.json`이 바로 그것.

**원래 사용법 (transformers)**:
```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-4b-it")
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
```

**우리 방식 (llama-cpp)**:
llama-cpp는 GGUF만 로드하고 chat_template 기능이 없음.
→ `build_gemma3_prompt()`로 동일한 로직을 Python으로 직접 구현.

#### 3. Role별 변환 규칙 (공식 chat_template 기준)

| role | 변환 결과 |
|------|----------|
| `user` | `<start_of_turn>user\n{내용}<end_of_turn>` |
| `assistant` | `<start_of_turn>model\n{내용}<end_of_turn>` ← **model로 변환!** |
| `system` | 별도 토큰 없음, **첫 user 메시지 앞에 합쳐버림** |

#### 4. 공식 vs 우리 구현 차이

**입력:**
```json
{"messages": [
  {"role": "system", "content": "친절하게"},
  {"role": "user", "content": "안녕"}
]}
```

**공식 chat_template 결과:**
```
<bos><start_of_turn>user
친절하게

안녕<end_of_turn>
<start_of_turn>model
```
→ system을 첫 user에 합침

**우리 build_gemma3_prompt 결과 (현재):**
```
<start_of_turn>user
[시스템 지시사항]
친절하게<end_of_turn>
<start_of_turn>user
안녕<end_of_turn>
<start_of_turn>model
```
→ system을 별도 user turn으로 처리

#### 5. TODO
- [ ] 공식 chat_template과 동일하게 수정할지 검토
- [ ] 멀티턴 대화 테스트

---

## 2026-01-12

### Gemma-3 4B 채팅 서버 구현

#### 1. 엔드포인트

| 엔드포인트 | 용도 |
|-----------|------|
| `GET /health` | 서버 상태 확인 |
| `POST /v1/chat/completions` | 채팅 |

#### 2. 요청 형식 (두 가지 지원)

**단순 형식:**
```json
{
  "messages": [
    {"role": "user", "content": "안녕"}
  ]
}
```

**멀티모달 형식 (OpenAI 호환):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "안녕"}
      ]
    }
  ]
}
```

#### 3. LLM 프롬프트 변환 원리

LLM은 "텍스트 이어쓰기" 기계. 대화를 구분하려면 **특수 토큰**이 필요.

```
우리가 보내는 JSON:
{"messages": [{"role": "user", "content": "안녕"}]}

build_gemma3_prompt()가 변환:
<start_of_turn>user
안녕<end_of_turn>
<start_of_turn>model
← 여기서 모델이 이어서 생성
```

모델은 학습할 때 이 형식으로 대화 데이터를 봤기 때문에, `<start_of_turn>model` 뒤에 답변을 생성해야 한다는 걸 앎.

#### 4. 모델별 프롬프트 형식

| 모델 | User | Assistant |
|------|------|-----------|
| Gemma-3 | `<start_of_turn>user` | `<start_of_turn>model` |
| Llama-3 | `<\|start_header_id\|>user` | `<\|start_header_id\|>assistant` |
| ChatML | `<\|im_start\|>user` | `<\|im_start\|>assistant` |

**각 모델이 학습한 형식을 정확히 맞춰야 동작함!**

#### 5. 서버 실행

```bash
python serving-gemma-3-4b-it-gguf.py
# http://localhost:8081
```

#### 7. 테스트

```bash
curl -X POST http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "안녕"}]}'
```

---

## 2026-01-05

### FunctionGemma llama-cpp 서빙 정리

#### 1. FunctionGemma란?
- Google의 **Function Calling 전용 모델** (Gemma 3 270M 기반)
- 일반 채팅 X, 오직 "어떤 함수를 호출할지" 결정하는 용도
- Single Turn, Parallel 호출 지원 (Multi-Turn은 미지원)

#### 2. 핵심: 특수 토큰
FunctionGemma는 아래 토큰들로 훈련됨. **이 형식을 정확히 맞춰야 동작함!**

| 토큰 | 용도 |
|------|------|
| `<start_function_declaration>` / `<end_function_declaration>` | 함수 정의 |
| `<start_function_call>` / `<end_function_call>` | 함수 호출 (모델 출력) |
| `<start_function_response>` / `<end_function_response>` | 함수 실행 결과 전달 |
| `<escape>` | 문자열 값 구분자 |

#### 3. 프롬프트 형식

```
<bos><start_of_turn>developer
You are a model that can do function calling with the following functions<start_function_declaration>declaration:함수명{description:<escape>함수설명<escape>,parameters:{properties:{파라미터명:{description:<escape>파라미터설명<escape>,type:<escape>STRING<escape>}},required:[<escape>필수파라미터<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration><end_of_turn>
<start_of_turn>user
사용자 질문<end_of_turn>
<start_of_turn>model
```

**중요 포인트:**
- Role은 `developer` 사용 (user나 system 아님!)
- 시스템 프롬프트: `"You are a model that can do function calling with the following functions"` 필수
- 모든 문자열 값은 `<escape>값<escape>` 형식

#### 4. 모델 출력 형식

```
<start_function_call>call:함수명{파라미터:<escape>값<escape>}<end_function_call>
```

예시:
```
<start_function_call>call:get_current_weather{location:<escape>Tokyo<escape>}<end_function_call>
```
