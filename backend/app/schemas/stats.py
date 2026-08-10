from datetime import datetime

from pydantic import BaseModel, Field


class SingleStat(BaseModel):
    title: str
    icon: str
    value: int | str
    variation: float = 0
    to: str = "#"


class RevenuePoint(BaseModel):
    date: str
    label: str
    amount: float


class RevenueResponse(BaseModel):
    period: str
    start: datetime
    end: datetime
    points: list[RevenuePoint]


class StatsResponse(BaseModel):
    stats: list[SingleStat]


class AdminBreakdown(BaseModel):
    key: str
    label: str
    value: float


class AdminTrend(BaseModel):
    key: str
    label: str
    offering_letters: int = 0
    purchase_orders: int = 0
    delivery_orders: int = 0
    invoices: int = 0
    sales_amount: float = 0


class AdminMetric(BaseModel):
    key: str
    title: str
    value: float
    unit: str = "count"
    icon: str
    description: str


class AdminActivity(BaseModel):
    domain: str
    title: str
    subtitle: str
    created_at: datetime | None = None
    to: str | None = None


class AdminStatsResponse(BaseModel):
    date_from: datetime
    date_to: datetime
    metrics: list[AdminMetric]
    trends: list[AdminTrend]
    distributions: dict[str, list[AdminBreakdown]]
    notifications: list[AdminActivity] = Field(default_factory=list)
    activities: list[AdminActivity] = Field(default_factory=list)


class AdminDrilldownItem(BaseModel):
    id: str
    title: str
    subtitle: str
    status: str | None = None
    value: float | None = None
    created_at: datetime | None = None
    to: str | None = None


class AdminDrilldownResponse(BaseModel):
    metric: str
    title: str
    description: str
    total: int
    total_value: float
    page: int
    page_size: int
    items: list[AdminDrilldownItem]
