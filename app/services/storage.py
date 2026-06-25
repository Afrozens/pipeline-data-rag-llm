import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.db import get_db


class StorageService:
    def __init__(
        self,
        output_dir: Optional[str] = None,
        mongo_enabled: Optional[bool] = None,
    ):
        self.output_dir = output_dir or settings.OUTPUT_DIR
        self.mongo_enabled = (
            mongo_enabled if mongo_enabled is not None
            else bool(settings.MONGODB_URI)
        )

    def _ensure_client_dir(self, client_id: str) -> str:
        path = os.path.join(self.output_dir, client_id)
        os.makedirs(path, exist_ok=True)
        return path

    def save_to_json(
        self,
        records: List[Dict[str, Any]],
        client_id: str,
        process_id: str,
    ) -> str:
        client_dir = self._ensure_client_dir(client_id)
        filename = f"{process_id}_normalized.json"
        filepath = os.path.join(client_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return filepath

    def save_to_mongodb(
        self,
        records: List[Dict[str, Any]],
        client_id: str,
        process_id: str,
    ) -> List[str]:
        if not records:
            return []
        db = get_db()
        docs = []
        for record in records:
            record["client_id"] = client_id
            record["process_id"] = process_id
            record["created_at"] = datetime.now(timezone.utc)
            docs.append(record)
        result = db["normalized_trip_records"].insert_many(docs)
        return [str(_id) for _id in result.inserted_ids]

    def save_all(
        self,
        records: List[Dict[str, Any]],
        client_id: str,
        process_id: str,
    ) -> Dict[str, Any]:
        paths: Dict[str, Any] = {}
        json_path = self.save_to_json(records, client_id, process_id)
        paths["json"] = json_path
        if self.mongo_enabled:
            mongo_ids = self.save_to_mongodb(records, client_id, process_id)
            if mongo_ids:
                paths["mongo_collection"] = "normalized_trip_records"
                paths["mongo_ids"] = mongo_ids
        return paths

    def get_json_result(self, client_id: str, process_id: str) -> List[Dict[str, Any]]:
        filepath = os.path.join(self.output_dir, client_id, f"{process_id}_normalized.json")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_mongodb_result(self, process_id: str) -> List[Dict[str, Any]]:
        db = get_db()
        cursor = db["normalized_trip_records"].find(
            {"process_id": process_id},
            {"_id": 0},
        )
        return list(cursor)
