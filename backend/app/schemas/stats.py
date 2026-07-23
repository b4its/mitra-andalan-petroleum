from pydantic import BaseModel


class SingleStat(BaseModel):
    title: str
    icon: str
    value: int | str
    variation: float = 0
    to: str = "#"


class StatsResponse(BaseModel):
    stats: list[SingleStat]
