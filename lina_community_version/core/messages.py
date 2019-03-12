from typing import Dict, Any, List, Union, Optional
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
    reply_message: Optional[Dict[str, Any]]
    important: bool
    random_id: int
    attachments: List[Any]
    is_hidden: bool
    raw_text: Optional[str] = None

    def __post_init__(self):
        self.text = self.text.lower()

    def __str__(self):
        return "%s --- User %s say: %s" % (self.peer_id,
                                           self.from_id,
                                           self.text)

    def __repr__(self):
        return 'Message in conversation %s from user %s: %s' % (self.peer_id,
                                                                self.from_id,
                                                                self.text)


def message_factory(_type: str,
                    data: Dict[str, Any]) -> Union[NewMessage, Confirmation]:
    if _type == MessageType.NewMessage.value:
        return NewMessage(**data)
    elif _type == MessageType.Confirmation.value:
        return Confirmation()
    else:
        raise ValueError
