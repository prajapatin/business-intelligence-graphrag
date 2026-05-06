import json
from typing import Any, Dict, List

import pandas as pd
from loguru import logger

from src.llm.base_provider import BaseLLMProvider


EXTRACTION_SYSTEM_PROMPT = """You are a knowledge graph entity extractor for a business intelligence system.
Given structured corporate data records, extract entities and relationships.

Return ONLY valid JSON with this schema:
{
  "entities": [
    {"id": "unique_id", "type": "EntityType", "name": "display_name", "properties": {}}
  ],
  "relationships": [
    {"source": "entity_id", "target": "entity_id", "relation": "RELATION_TYPE", "properties": {}}
  ]
}

Entity types: Department, Employee, Product, Customer, Region, Industry, Quarter, Category
Relationship types: WORKS_IN, HEADS, SOLD_BY, PURCHASED_BY, BELONGS_TO, LOCATED_IN, IN_INDUSTRY, PRODUCED_BY, IN_CATEGORY"""


def extract_from_structured_data(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict[str, Any]]]:
    """Extract entities and relationships directly from structured CSV data.

    This is the deterministic extraction path — no LLM needed.
    Produces consistent, complete graph from the known schema.
    """
    entities = []
    relationships = []

    # --- Departments ---
    if "departments" in tables:
        for _, row in tables["departments"].iterrows():
            entities.append({
                "id": row["id"],
                "type": "Department",
                "name": row["name"],
                "properties": {"budget": float(row["budget"])},
            })

    # --- Products ---
    if "products" in tables:
        categories = set()
        for _, row in tables["products"].iterrows():
            entities.append({
                "id": row["id"],
                "type": "Product",
                "name": row["name"],
                "properties": {
                    "base_price": float(row["base_price"]),
                    "category": row["category"],
                },
            })
            relationships.append({
                "source": row["id"],
                "target": row["department"],
                "relation": "PRODUCED_BY",
                "properties": {},
            })
            cat_id = f"CAT-{row['category']}"
            if row["category"] not in categories:
                entities.append({
                    "id": cat_id,
                    "type": "Category",
                    "name": row["category"],
                    "properties": {},
                })
                categories.add(row["category"])
            relationships.append({
                "source": row["id"],
                "target": cat_id,
                "relation": "IN_CATEGORY",
                "properties": {},
            })

    # --- Regions ---
    regions_seen = set()

    # --- Employees ---
    if "employees" in tables:
        for _, row in tables["employees"].iterrows():
            entities.append({
                "id": row["id"],
                "type": "Employee",
                "name": row["name"],
                "properties": {
                    "role": row["role"],
                    "salary": float(row["salary"]),
                    "hire_date": row["hire_date"],
                },
            })
            relationships.append({
                "source": row["id"],
                "target": row["department_id"],
                "relation": "WORKS_IN",
                "properties": {},
            })
            if row["role"] == "Department Head":
                relationships.append({
                    "source": row["id"],
                    "target": row["department_id"],
                    "relation": "HEADS",
                    "properties": {},
                })
            region = row["region"]
            region_id = f"REG-{region.replace(' ', '_')}"
            if region not in regions_seen:
                entities.append({
                    "id": region_id,
                    "type": "Region",
                    "name": region,
                    "properties": {},
                })
                regions_seen.add(region)
            relationships.append({
                "source": row["id"],
                "target": region_id,
                "relation": "LOCATED_IN",
                "properties": {},
            })

    # --- Customers ---
    industries_seen = set()
    if "customers" in tables:
        for _, row in tables["customers"].iterrows():
            entities.append({
                "id": row["id"],
                "type": "Customer",
                "name": row["company_name"],
                "properties": {
                    "contact": row["contact_name"],
                    "tier": row["tier"],
                    "since": row["since"],
                },
            })
            region = row["region"]
            region_id = f"REG-{region.replace(' ', '_')}"
            if region not in regions_seen:
                entities.append({
                    "id": region_id,
                    "type": "Region",
                    "name": region,
                    "properties": {},
                })
                regions_seen.add(region)
            relationships.append({
                "source": row["id"],
                "target": region_id,
                "relation": "LOCATED_IN",
                "properties": {},
            })
            industry = row["industry"]
            ind_id = f"IND-{industry.replace(' ', '_')}"
            if industry not in industries_seen:
                entities.append({
                    "id": ind_id,
                    "type": "Industry",
                    "name": industry,
                    "properties": {},
                })
                industries_seen.add(industry)
            relationships.append({
                "source": row["id"],
                "target": ind_id,
                "relation": "IN_INDUSTRY",
                "properties": {},
            })

    # --- Sales Transactions ---
    quarters_seen = set()
    if "sales_transactions" in tables:
        for _, row in tables["sales_transactions"].iterrows():
            date_str = row["date"]
            month = int(date_str.split("-")[1])
            year = date_str.split("-")[0]
            quarter = f"Q{(month - 1) // 3 + 1}-{year}"
            quarter_id = f"QTR-{quarter}"

            if quarter not in quarters_seen:
                entities.append({
                    "id": quarter_id,
                    "type": "Quarter",
                    "name": quarter,
                    "properties": {"year": int(year), "quarter": (month - 1) // 3 + 1},
                })
                quarters_seen.add(quarter)

            # Employee sold product
            relationships.append({
                "source": row["employee_id"],
                "target": row["product_id"],
                "relation": "SOLD",
                "properties": {
                    "transaction_id": row["id"],
                    "amount": float(row["total_amount"]),
                    "quantity": int(row["quantity"]),
                    "date": date_str,
                    "status": row["status"],
                },
            })
            # Customer purchased product
            relationships.append({
                "source": row["customer_id"],
                "target": row["product_id"],
                "relation": "PURCHASED",
                "properties": {
                    "transaction_id": row["id"],
                    "amount": float(row["total_amount"]),
                    "quantity": int(row["quantity"]),
                    "date": date_str,
                },
            })
            # Transaction in quarter
            relationships.append({
                "source": row["product_id"],
                "target": quarter_id,
                "relation": "SOLD_IN",
                "properties": {
                    "amount": float(row["total_amount"]),
                },
            })

    logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
    return {"entities": entities, "relationships": relationships}


def extract_with_llm(llm: BaseLLMProvider, text_chunk: str) -> Dict[str, List[Dict[str, Any]]]:
    """Use LLM to extract entities and relationships from unstructured text.

    This is the LLM-based extraction path for unstructured data.
    """
    prompt = f"""Extract all business entities and their relationships from the following corporate data:

---
{text_chunk}
---

Return valid JSON only."""

    try:
        response = llm.extract_json(prompt, system_prompt=EXTRACTION_SYSTEM_PROMPT)
        # Strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        result = json.loads(cleaned.strip())
        return result
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse LLM extraction response: {e}")
        return {"entities": [], "relationships": []}
