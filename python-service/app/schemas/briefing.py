from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Basic metric pair; name and value are both required if the metric object exists
class BriefingMetricCreate(BaseModel):
    name: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class BriefingCreate(BaseModel):
    # CamelCase naming here to match the JSON payload from the frontend
    companyName: str = Field(..., min_length=1)
    ticker: str = Field(..., min_length=1)
    sector: str = Field(..., min_length=1)
    analystName: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    recommendation: str = Field(..., min_length=1)
    
    # Enforcing the business rules: 2+ points and 1+ risk
    keyPoints: List[str] = Field(..., min_length=2, description="At least 2 key points are required")
    risks: List[str] = Field(..., min_length=1, description="At least 1 risk is required")
    
    metrics: Optional[List[BriefingMetricCreate]] = None

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, v: str) -> str:
        # standardizing ticker case before it hits the database
        return v.upper()

    @model_validator(mode="after")
    def check_unique_metric_names(self):
        # prevents duplicate metric keys in the same briefing request
        if self.metrics:
            names = [m.name for m in self.metrics]
            if len(names) != len(set(names)):
                raise ValueError("Metric names must be unique within the same briefing")
        return self


# Response schemas use from_attributes=True so they can parse SQLAlchemy ORM objects directly
class BriefingMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    value: str


class BriefingPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str


class BriefingRiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str


class BriefingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # Note: snake_case here matches the DB columns for the response JSON
    company_name: str
    ticker: str
    sector: str
    analyst_name: str
    summary: str
    recommendation: str
    status: str
    # Nested relationships
    points: List[BriefingPointResponse]
    risks: List[BriefingRiskResponse]
    metrics: List[BriefingMetricResponse]