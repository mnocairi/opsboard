from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    severity: str
    status: str = "OPEN"


class IncidentResponse(IncidentCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)