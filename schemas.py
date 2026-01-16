"""
채팅 API 스키마
"""

from pydantic import BaseModel
from typing import Optional, Union


class ContentPart(BaseModel):
    """멀티모달 콘텐츠 파트"""
    type: str
    text: Optional[str] = None
    image_url: Optional[dict] = None


class ChatMessage(BaseModel):
    """
    채팅 메시지

    단순: {"role": "user", "content": "안녕"} → 단순 텍스트 메시지만 가능
    배열: {"role": "user", "content": [{"type": "text", "text": "안녕"}]} → 멀티모달 형식으로 이미지도 넣을 수 있음.
    """
    role: str
    content: Union[str, list[ContentPart]]

    def get_text_content(self) -> str:
        if isinstance(self.content, str):
            return self.content
        return "\n".join(p.text for p in self.content if p.type == "text" and p.text)


class ChatCompletionRequest(BaseModel):
    """채팅 요청"""
    messages: list[ChatMessage]
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    stop: Optional[list[str]] = None


class ChatCompletionResponse(BaseModel):
    """채팅 응답"""
    message: ChatMessage
    usage: dict
