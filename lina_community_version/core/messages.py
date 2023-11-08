import inspect

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
    important: bool
    random_id: int
    attachments: List[Any]
    is_hidden: bool
    entity_version: int
    ref: Optional[str] = None
    ref_source: Optional[str] = None
    raw_text: Optional[str] = None
    reply_message: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    payload: Optional[Any] = None

    def __post_init__(self):
        self.text = self.text.lower()

    def get_text_or_attach(self) -> str:
        if self.text != '':
            return self.text
        elif self.action is not None:
            return str(self.action.get('type'))
        else:
            return ', '.join([attach['type'] for attach in self.attachments])

    def __str__(self):
        return "%s --- User %s say: %s" % (self.peer_id,
                                           self.from_id,
                                           self.get_text_or_attach())

    def __repr__(self):
        return 'Message in conversation %s from user %s: %s' % (self.peer_id,
                                                                self.from_id,
                                                                self.text)


def message_factory(_type: str,
                    data: Dict[str, Any]) -> Union[NewMessage, Confirmation]:
    if _type == MessageType.NewMessage.value:
        field_names = set(f.name for f in dataclasses.fields(NewMessage))
        return NewMessage(**{k:v for k,v in data.items() if k in field_names})
    elif _type == MessageType.Confirmation.value:
        return Confirmation()
    else:
        raise ValueError
