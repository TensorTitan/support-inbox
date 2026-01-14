from pydantic import BaseModel
from typing import Literal, Optional

class WSMessageIn(BaseModel):
    conversation_id: Optional[str] = None
    sender: Literal["customer", "operator"]
    content: str