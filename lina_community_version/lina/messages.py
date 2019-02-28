from typing import Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    NewMessage = 'message_new'
    Confirmation = 'confirmation'


@dataclass()
class BaseMessage:
    pass


@dataclass()
class Confirmation(BaseMessage):
    pass


@dataclass()
class NewMessage(BaseMessage):
    date: int
    from_id: int
    id: int
    out: int
    peer_id: int
    text: str
    conversation_message_id: int
    fwd_messages: List[Any]
    important: bool
    random_id: int
    attachments: List[Any]
    is_hidden: bool


def message_factory(_type: str,
                    data: Dict[str, Any]) -> Union[NewMessage, Confirmation]:
    if _type == MessageType.NewMessage.value:
        return NewMessage(**data)
    elif _type == MessageType.Confirmation.value:
        return Confirmation()
    else:
        raise ValueError
