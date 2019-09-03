from dataclasses import dataclass
from typing import Optional, Dict


@dataclass()
class UserProfile:
    id: int
    first_name: str
    last_name: str
    is_closed: bool
    can_access_closed: bool
    sex: int
    screen_name: str
    photo_50: str
    photo_100: str
    online: int
    online_info: Dict[str, bool]
    online_mobile: Optional[int] = None
    online_app: Optional[int] = None

    def __repr__(self):
        return '%s %s' % (self.first_name, self.last_name)
