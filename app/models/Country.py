from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Country(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int = Field(..., ge=0, description="population must be positive", nullable=False)
    currency_code: str = Field(nullable=True)
    exchange_rate: float = Field(..., ge=0, description="exchange rate must be positive", nullable=True)
    estimated_gdp: Optional[float] = Field(..., ge=0, description="estimated gdp must be positive")
    flag_url: str
    last_refreshed_at: datetime = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    

