"""
채팅 API 스키마
"""

from pydantic import BaseModel
from typing import Optional, Union

"""멀티모달 콘텐츠 파트"""
class ContentPart(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[dict] = None

"""
채팅 메시지

단순: {"role": "user", "content": "안녕"} → 단순 텍스트 메시지만 가능
배열: {"role": "user", "content": [{"type": "text", "text": "안녕"}]} → 멀티모달 형식으로 이미지도 넣을 수 있음.
"""
class ChatMessage(BaseModel):
    role: str
    content: Union[str, list[ContentPart]]

    def get_text_content(self) -> str:
        if isinstance(self.content, str):
            return self.content
        return "\n".join(p.text for p in self.content if p.type == "text" and p.text)

"""
일반 채팅 요청
사용자(User)가 llm 모델(Gemma3)에게 요청(Req)하는 것
"""
class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    stop: Optional[list[str]] = None

"""
일반 채팅 응답
llm 모델(Gemma3)가 사용자(User)에게 응답(Res)하는 것
"""
class ChatCompletionResponse(BaseModel):
    message: ChatMessage
    usage: dict

"""
쇼핑몰 에이전트에게 요청
사용자(User)가 쇼핑몰 Agent에게 요청(Req)하는 것
"""
class AgentChatRequest(BaseModel):
    message:str

"""
쇼핑몰 에이전트가 응답
쇼핑몰 Agent가 사용자(User)에게 응답(Res)하는 것
"""
class AgentChatResponse(BaseModel):
    response: str