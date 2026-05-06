import pytest
import pandas as pd

from src.ingestion.entity_extractor import extract_from_structured_data
from src.ingestion.graph_builder import build_graph
from src.graph.networkx_store import NetworkXGraphStore


@pytest.fixture
def sample_tables():
    departments = pd.DataFrame([
        {"id": "DEPT-001", "name": "Engineering", "budget": 2500000, "head": "EMP-001"},
    ])
    products = pd.DataFrame([
        {"id": "PROD-001", "name": "CloudSync Pro", "category": "SaaS", "base_price": 299.99, "department": "DEPT-001"},
    ])
    employees = pd.DataFrame([
        {"id": "EMP-001", "name": "Alice", "email": "alice@co.com", "department_id": "DEPT-001",
         "role": "Department Head", "hire_date": "2022-01-15", "salary": 120000, "region": "North America"},
    ])
    customers = pd.DataFrame([
        {"id": "CUST-001", "company_name": "Acme Corp", "contact_name": "John",
         "industry": "Technology", "region": "North America", "tier": "Enterprise", "since": "2022-06-01"},
    ])
    transactions = pd.DataFrame([
        {"id": "TX-0001", "date": "2023-06-15", "product_id": "PROD-001", "customer_id": "CUST-001",
         "employee_id": "EMP-001", "quantity": 5, "unit_price": 299.99, "discount": 0.1,
         "total_amount": 1349.96, "region": "North America", "status": "Completed"},
    ])
    return {
        "departments": departments,
        "products": products,
        "employees": employees,
        "customers": customers,
        "sales_transactions": transactions,
    }


def test_extract_from_structured_data(sample_tables):
    result = extract_from_structured_data(sample_tables)
    assert "entities" in result
    assert "relationships" in result
    assert len(result["entities"]) > 0
    assert len(result["relationships"]) > 0

    entity_types = {e["type"] for e in result["entities"]}
    assert "Department" in entity_types
    assert "Product" in entity_types
    assert "Employee" in entity_types
    assert "Customer" in entity_types


def test_extract_creates_quarters(sample_tables):
    result = extract_from_structured_data(sample_tables)
    quarter_entities = [e for e in result["entities"] if e["type"] == "Quarter"]
    assert len(quarter_entities) > 0
    assert quarter_entities[0]["name"].startswith("Q")


def test_build_graph(sample_tables):
    extracted = extract_from_structured_data(sample_tables)
    store = NetworkXGraphStore()
    build_graph(store, extracted)

    stats = store.get_statistics()
    assert stats["total_nodes"] > 0
    assert stats["total_edges"] > 0
    assert store.get_node("DEPT-001") is not None
    assert store.get_node("PROD-001") is not None
