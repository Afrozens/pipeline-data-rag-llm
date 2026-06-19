import json
from typing import Dict, List, Type, TypeVar

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.pipeline import DetectedFormat, FieldMapping

T = TypeVar("T", bound=BaseModel)

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
    return _llm


def get_structured_llm(model_cls: Type[T]) -> ChatOpenAI:
    return get_llm().with_structured_output(model_cls, method="json_schema")


def infer_schema(
    headers: List[str],
    sample_rows: List[Dict],
) -> DetectedFormat:
    prompt = f"""Analyze the following headers and sample data from a travel agency Excel file.

HEADERS: {headers}
SAMPLE ROWS (first 3): {json.dumps(sample_rows[:3])}

Identify:
1. What type of format it is (e.g., "Formato con cuotas", "Formato básico cliente", "Formato con viajeros")
2. What each column means semantically
3. Whether the data includes a travelers column
4. Your confidence level in the detection

Respond with the specified JSON format."""

    structured = get_structured_llm(DetectedFormat)
    result = structured.invoke(
        [SystemMessage(content="You are an expert at analyzing Excel data formats for travel agencies."),
         HumanMessage(content=prompt)]
    )
    return result


def map_fields(
    headers: List[str],
    detected_format: DetectedFormat,
) -> FieldMapping:
    prompt = f"""Map the following columns from a travel agency Excel file to the unified schema.

DETECTED COLUMNS: {detected_format.detected_columns}
FORMAT: {detected_format.format_name}

Available target schema fields:
- passenger.first_name, passenger.last_name
- trip.name, trip.start_date, trip.end_date
- plan
- amount
- installments.has_installments, installments.total_installments, installments.installment_value
- contact.phone, contact.email
- address
- identification.type, identification.number
- travelers
- notes

Rules:
- "nombre y apellido" -> passenger.first_name + passenger.last_name (split by space)
- "fechas" with range (e.g., "10-20 Mar") -> trip.start_date + trip.end_date
- "cuotas" -> installments.has_installments = True
- Columns without direct mapping -> null (stay in raw_data)

Return the mapping in JSON format."""

    structured = get_structured_llm(FieldMapping)
    result = structured.invoke(
        [SystemMessage(content="You are an expert at mapping travel agency Excel columns to a unified schema."),
         HumanMessage(content=prompt)]
    )
    return result
