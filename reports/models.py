from typing import Optional

from pydantic import BaseModel


class ClientSettings(BaseModel):

    r_type: Optional[int]
    r_format: Optional[str]
    user_id: Optional[int]
