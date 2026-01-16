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

#### 1. 현재 구조

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

#### 2. 엔드포인트

| 엔드포인트 | 용도 |
|-----------|------|
| `GET /health` | 서버 상태 확인 |
| `POST /v1/chat/completions` | 채팅 |

#### 3. 요청 형식 (두 가지 지원)

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

#### 4. LLM 프롬프트 변환 원리

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

#### 5. 모델별 프롬프트 형식

| 모델 | User | Assistant |
|------|------|-----------|
| Gemma-3 | `<start_of_turn>user` | `<start_of_turn>model` |
| Llama-3 | `<\|start_header_id\|>user` | `<\|start_header_id\|>assistant` |
| ChatML | `<\|im_start\|>user` | `<\|im_start\|>assistant` |

**각 모델이 학습한 형식을 정확히 맞춰야 동작함!**

#### 6. 서버 실행

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
