A smart pipeline based on **LangGraph** + **LLM (GPT-4 or GPT-mini)** that receives Excel files containing travel data from agencies in **various formats** and consolidates them into a centralized schema (`TripRecord`).

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────────┐
│   Client   │────▶│  FastAPI (/upload)│────▶│  Create process (status:   │
│  (Excel)    │     │                  │     │  created) + init pipeline   │
└─────────────┘     └──────────────────┘     └─────────────┬───────────────┘
                                                            │
                                      ┌─────────────────────┘
                                      ▼
                          ┌──────────────────────┐
                          │  LangGraph Pipeline   │
                          │  (background task)    │
                          │                       │
                          │  parse_excel ──────┐  │
                          │  infer_schema  ← LLM│  │
                          │  map_fields    ← LLM│  │
                          │  transform ────────┐│  │
                          │  validate ────────┐│  │
                          │  output ──────────┐│  │
                          └─────────┬─────────┘│  │
                                    │          │  │
                                    ▼          ▼  ▼
                          ┌──────────────────────────┐
                          │  Multiple destinity      │
                          │  ┌─────┐ ┌──────┐ ┌────┐ │
                          │  │JSON │ │Mongo │ │API │ │
                          │  └─────┘ └──────┘ └────┘ │
                          └──────────────────────────┘
```


A pipeline orchestrated with LangGraph that:

1. Automatically **detects** the input format via LLM
2. **Maps** the detected columns to the unified schema
3. **Transforms** and cleans the data
4. **Validates** data integrity
5. **Persists** the result to multiple destinations (JSON, MongoDB, API response)