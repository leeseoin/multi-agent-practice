

import gradio as gr
import json
import re
from typing import Dict, List, Any, Tuple, Optional
from llama_cpp import Llama

# 모델 로드
MODEL_PATH = "/Users/iseoin/Python_Project/multi-agent/gemma-3-4b-it-q4_0.gguf"
print(f"{MODEL_PATH} 모델 로딩 중..")
llm = Llama(
    model=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=-1,
    verbose=False
)
print(f"{MODEL_PATH} 모델 로딩 완료!!!\n")

sampling_params = SamplingParams(temperature=0, max_tokens=1024)


class ConversationManager:
    def __init__(self, llm):
        self.history = []
        self.system_prompt = """당신은 서인몰의 AI 상담사입니다. 성심성의껏 상담하십시오.

로그인한 사용자의 현재 ID: U006
오늘 날짜: 2024-02-02

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "add_to_cart", "description": "사용자의 장바구니에 지정된 상품(product_id)과 수량(quantity)을 추가합니다. 동일 상품이 이미 있으면 수량을 증가시키고, 새 항목으로 추가합니다.", "parameters": {"type": "object", "properties": {"user_id": {"type": "string", "description": "장바구니에 상품을 추가할 사용자의 고유 식별자 (예: 'U001')"}, "product_id": {"type": "string", "description": "장바구니에 추가할 상품의 고유 식별자 (예: 'P003')"}, "quantity": {"type": "integer", "description": "추가할 상품 수량 (기본값: 1)", "default": 1, "minimum": 1}}, "required": ["user_id", "product_id"], "additionalProperties": false}}}
{"type": "function", "function": {"name": "view_order_history", "description": "사용자의 전체 주문 내역을 반환합니다. 각 주문에 대해 주문 번호, 주문 일자, 총 결제 금액, 결제 상태, 배송 상태, 택배사, 운송장 번호, 배송 진행 단계, 주문에 포함된 상품명 목록을 제공합니다. 이 함수로도 최근 주문의 배송 상태를 확인할 수 있습니다.", "parameters": {"type": "object", "properties": {"user_id": {"type": "string", "description": "주문 내역을 조회할 사용자의 고유 식별자 (예: 'U001')"}}, "required": ["user_id"], "additionalProperties": false}}}
{"type": "function", "function": {"name": "view_user_profile", "description": "사용자의 기본 프로필 정보(이름, 이메일, 전화번호, 주소, 포인트, 멤버십)와 보유 쿠폰 정보를 반환합니다.", "parameters": {"type": "object", "properties": {"user_id": {"type": "string", "description": "프로필을 조회할 사용자의 고유 식별자, 예: 'U001'"}}, "required": ["user_id"], "additionalProperties": false}}}
{"type": "function", "function": {"name": "show_cart", "description": "지정된 사용자(user_id)의 현재 장바구니에 담긴 모든 상품을 반환합니다. 각 항목에 대해 상품 ID, 상품명, 가격, 수량, 장바구니에 추가된 일시를 포함합니다.", "parameters": {"type": "object", "properties": {"user_id": {"type": "string", "description": "장바구니를 조회할 사용자의 고유 식별자 (예: 'U001')"}}, "required": ["user_id"], "additionalProperties": false}}}
{"type": "function", "function": {"name": "remove_from_cart", "description": "사용자의 장바구니에서 상품명을 포함하는 키워드(keyword) 또는 특정 상품 ID(product_id)를 사용해 항목을 제거합니다. keyword 또는 product_id 중 하나를 반드시 지정해야 합니다.", "parameters": {"type": "object", "properties": {"user_id": {"type": "string", "description": "장바구니에서 상품을 제거할 사용자의 고유 식별자 (예: 'U001')"}, "keyword": {"type": "string", "description": "상품명에 포함된 키워드로 제거 대상을 지정 (예: '우산')"}, "product_id": {"type": "string", "description": "제거할 정확한 상품 ID (예: 'P005')"}}, "required": ["user_id"], "anyOf": [{"required": ["keyword"]}, {"required": ["product_id"]}], "additionalProperties": false}}}
{"type": "function", "function": {"name": "search_policy_info", "description": "지정된 키워드에 대한 상준몰 정책/약관 정보를 검색합니다. 예: '주문 취소', '반품', '환불', '배송', '재입고'에 관련된 약관만 질문하세요.", "parameters": {"type": "object", "properties": {"keyword": {"type": "string", "description": "정책을 검색할 키워드 (예: '주문 취소', '반품', '환불', '배송', '재입고'만 넣을 수 있습니다.)"}}, "required": ["keyword"], "additionalProperties": false}}}
{"type": "function", "function": {"name": "view_order_details", "description": "특정 주문(order_id)의 상세 내역을 조회합니다. 주문에 포함된 각 상품의 ID, 상품명, 수량, 단가, 할인 적용 가격을 반환합니다.", "parameters": {"type": "object", "properties": {"user_id": {"type": "string", "description": "주문 상세를 조회할 사용자의 고유 식별자 (예: 'U001')"}, "order_id": {"type": "string", "description": "상세 내역을 조회할 주문의 고유 식별자 (예: 'O001')"}}, "required": ["user_id", "order_id"], "additionalProperties": false}}}
{"type": "function", "function": {"name": "search_product", "description": "상품명에 특정 키워드를 포함하는 제품을 검색하고, 평점 순으로 정렬된 결과를 반환합니다. 필요시 카테고리(category)로 추가 필터링이 가능합니다.", "parameters": {"type": "object", "properties": {"keyword": {"type": "string", "description": "검색할 상품명 키워드 (예: '노트북')"}, "category": {"type": "string", "description": "선택적 카테고리 필터 (예: '전자기기')"}}, "required": ["keyword"], "additionalProperties": false}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>"""

        # 외부에서 받은 LLM 사용
        self.llm = llm
        self.sampling_params = sampling_params
        
        # 함수 호출 정규 표현식 패턴
        self.tool_call_pattern = re.compile(r'<tool_call>(.*?)</tool_call>', re.DOTALL)
        
        # 마지막 프롬프트 저장 변수
        self.last_prompt = ""
        
    def format_conversation(self):
        """대화 이력을 Qwen 2.5의 입력 형식으로 변환"""
        formatted_messages = [f"<|im_start|>system\n{self.system_prompt}<|im_end|>"]
        
        for message in self.history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                formatted_messages.append(f"<|im_start|>user\n{content}<|im_end|>")
            elif role == "assistant":
                formatted_messages.append(f"<|im_start|>assistant\n{content}<|im_end|>")
        
        # 항상 assistant 시작 태그 추가
        prompt = "\n".join(formatted_messages)
        prompt += f"\n<|im_start|>assistant"
        
        return prompt
    
    def extract_tool_call(self, assistant_message):
        """어시스턴트 메시지에서 함수 호출 정보를 추출"""
        match = self.tool_call_pattern.search(assistant_message)
        if match:
            try:
                tool_call_json = json.loads(match.group(1))
                return tool_call_json
            except json.JSONDecodeError:
                return None
        return None
    
    def add_message(self, role, content):
        """대화 이력에 메시지 추가"""
        self.history.append({"role": role, "content": content})
    
    def get_assistant_response(self, user_message):
        """사용자 메시지에 대한 어시스턴트 응답 생성"""
        self.add_message("user", user_message)
        prompt = self.format_conversation()
        
        # 마지막 프롬프트 저장 (디버깅용)
        self.last_prompt = prompt
        
        # vLLM으로 응답 생성
        outputs = self.llm.generate(prompt, self.sampling_params)
        assistant_reply = outputs[0].outputs[0].text.strip()
        
        self.add_message("assistant", assistant_reply)
        return assistant_reply
    
    def process_function_result(self, function_result):
        """함수 실행 결과를 처리하고 응답 생성"""
        tool_response = f"<tool_response>\n{function_result}\n</tool_response>"
        # 내부 대화 이력에는 추가하지 않고, 임시 프롬프트만 생성
        temp_history = self.history.copy()
        temp_history.append({"role": "user", "content": tool_response})
        
        # 임시 프롬프트 생성
        formatted_messages = [f"<|im_start|>system\n{self.system_prompt}<|im_end|>"]
        
        for message in temp_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                formatted_messages.append(f"<|im_start|>user\n{content}<|im_end|>")
            elif role == "assistant":
                formatted_messages.append(f"<|im_start|>assistant\n{content}<|im_end|>")
        
        # 항상 assistant 시작 태그 추가
        prompt = "\n".join(formatted_messages)
        prompt += f"\n<|im_start|>assistant"
        
        # 마지막 프롬프트 저장
        self.last_prompt = prompt
        
        # 응답 생성
        outputs = self.llm.generate(prompt, self.sampling_params)
        assistant_reply = outputs[0].outputs[0].text.strip()
        
        # 응답 반환 (내부 대화 이력에는 추가하지 않음)
        return assistant_reply
