import json
import os
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import START, END, StateGraph

from app.core.config import settings
from app.core.db import get_db
from app.schemas.pipeline import DetectedFormat, FieldMapping
from app.schemas.trip_record import TripRecord
from app.utils.excel_utils import read_excel_data
from app.utils.llm_utils import infer_schema, map_fields


class PipelineState(TypedDict):
    file_path: str
    sheet_name: str
    headers: List[str]
    raw_rows: List[Dict[str, Any]]
    total_rows: int
    detected_format: DetectedFormat | None
    field_mapping: FieldMapping | None
    records: List[Dict[str, Any]]
    errors: List[str]


def parse_excel_node(state: PipelineState) -> dict:
    headers, rows, total = read_excel_data(
        state["file_path"],
        sheet_name=state.get("sheet_name") or None,
    )
    return {
        "headers": headers,
        "raw_rows": rows,
        "total_rows": total,
    }


def infer_schema_node(state: PipelineState) -> dict:
    sample = state["raw_rows"][:5]
    result = infer_schema(state["headers"], sample)
    return {"detected_format": result}


def map_fields_node(state: PipelineState) -> dict:
    result = map_fields(state["headers"], state["detected_format"])
    return {"field_mapping": result}


def _deep_set(target: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    for part in parts[:-1]:
        if part not in target:
            target[part] = {}
        target = target[part]
    target[parts[-1]] = value


def transform_node(state: PipelineState) -> dict:
    mapping = state["field_mapping"].mapping
    records: List[Dict[str, Any]] = []
    for row in state["raw_rows"]:
        data: Dict[str, Any] = {}
        for excel_col, schema_path in mapping.items():
            if schema_path is None:
                continue
            value = row.get(excel_col)
            _deep_set(data, schema_path, value)
        record = TripRecord(**data, raw_data=row)
        records.append(record.model_dump(mode="json"))
    return {"records": records}


def validate_node(state: PipelineState) -> dict:
    errors: List[str] = []
    for i, record in enumerate(state["records"]):
        if not record.get("passenger"):
            errors.append(f"Row {i}: missing passenger info")
        if not record.get("trip"):
            errors.append(f"Row {i}: missing trip info")
    return {"errors": errors}


def output_node(state: PipelineState) -> dict:
    output_dir = settings.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(state["file_path"]))[0]
    out_path = os.path.join(output_dir, f"{base}_transformed.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state["records"], f, ensure_ascii=False, indent=2)

    db = get_db()
    if state["records"]:
        db["trip_records"].insert_many(state["records"])

    return {}


def build_pipeline_graph() -> StateGraph:
    builder = StateGraph(PipelineState)

    builder.add_node("parse_excel", parse_excel_node)
    builder.add_node("infer_schema", infer_schema_node)
    builder.add_node("map_fields", map_fields_node)
    builder.add_node("transform", transform_node)
    builder.add_node("validate", validate_node)
    builder.add_node("output", output_node)

    builder.add_edge(START, "parse_excel")
    builder.add_edge("parse_excel", "infer_schema")
    builder.add_edge("infer_schema", "map_fields")
    builder.add_edge("map_fields", "transform")
    builder.add_edge("transform", "validate")
    builder.add_edge("validate", "output")
    builder.add_edge("output", END)

    return builder.compile()


pipeline_app = build_pipeline_graph()


def run_pipeline(file_path: str, sheet_name: str = "") -> dict:
    initial_state: PipelineState = {
        "file_path": file_path,
        "sheet_name": sheet_name,
        "headers": [],
        "raw_rows": [],
        "total_rows": 0,
        "detected_format": None,
        "field_mapping": None,
        "records": [],
        "errors": [],
    }
    return pipeline_app.invoke(initial_state)
