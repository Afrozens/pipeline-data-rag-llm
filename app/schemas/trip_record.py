from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date

class Passenger(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TripInfo(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Installments(BaseModel):
    has_installments: bool = False
    total_installments: Optional[int] = None
    installment_value: Optional[float] = None


class Contact(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None


class Identification(BaseModel):
    type: Optional[str] = None       # ej: "CC", "CI", "RIF"
    number: Optional[str] = None


class TripRecord(BaseModel):
    passenger: Optional[Passenger] = None
    trip: Optional[TripInfo] = None
    plan: Optional[str] = None
    amount: Optional[float] = None
    installments: Optional[Installments] = None
    contact: Optional[Contact] = None
    address: Optional[str] = None
    identification: Optional[Identification] = None
    travelers: Optional[int] = None
    notes: Optional[str] = None
    raw_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original, untransformed data, preserved from Excel"
    )