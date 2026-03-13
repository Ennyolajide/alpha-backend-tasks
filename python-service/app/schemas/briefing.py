from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# --- Request Schemas ---

class BriefingMetricCreate(BaseModel):
    name: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class BriefingCreate(BaseModel):
    # Using camelCase for input to match frontend JSON standards if needed,
    # though snake_case is more standard for pure Python APIs.
    companyName: str = Field(..., min_length=1)
    ticker: str = Field(..., min_length=1)
    sector: str = Field(..., min_length=1)
    analystName: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    recommendation: str = Field(..., min_length=1)
    
    # Ensure we actually have data to show in the UI
    keyPoints: List[str] = Field(..., min_length=2)
    risks: List[str] = Field(..., min_length=1)
    
    metrics: Optional[List[BriefingMetricCreate]] = None

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, v: str) -> str:
        return v.upper()

    @model_validator(mode="after")
    def check_unique_metric_names(self):
        if self.metrics:
            names = [m.name.lower() for m in self.metrics]
            if len(names) != len(set(names)):
                raise ValueError("Duplicate metric names found")
        return self


# --- Response Schemas ---

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
    company_name: str
    ticker: str
    sector: str
    analyst_name: str
    summary: str
    recommendation: str
    status: str
    
    # Nested lists for the full briefing object
    points: List[BriefingPointResponse]
    risks: List[BriefingRiskResponse]
    metrics: List[BriefingMetricResponse]