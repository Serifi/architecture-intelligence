from typing import Optional, List

from pydantic import BaseModel, Field, constr


class StatusBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)
    color: constr(strip_whitespace=True, min_length=1, max_length=50)
    position: int = Field(..., ge=0)


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    color: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None
    position: Optional[int] = Field(None, ge=0)


class StatusRead(StatusBase):
    statusID: int
    model_config = {"from_attributes": True}


class StatusResponse(BaseModel):
    message: str
    status: StatusRead


class DeleteResponse(BaseModel):
    message: str
    deleted: bool = True


class StatusReorderItem(BaseModel):
    statusID: int = Field(..., ge=1)
    position: int = Field(..., ge=0)


class StatusReorderResponse(BaseModel):
    message: str
    statuses: List[StatusRead]