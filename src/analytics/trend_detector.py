from collections import defaultdict
from typing import Any, Dict, List

from loguru import logger

from src.graph.base_store import BaseGraphStore


class TrendDetector:
    """Detect trends and patterns from the knowledge graph."""

    def __init__(self, graph_store: BaseGraphStore):
        self.graph_store = graph_store

    def get_all_insights(self) -> Dict[str, Any]:
        """Run all trend detection analyses and return aggregated insights."""
        return {
            "quarterly_revenue": self.quarterly_revenue_trend(),
            "top_products": self.top_products_by_revenue(),
            "top_customers": self.top_customers_by_spend(),
            "department_performance": self.department_performance(),
            "regional_distribution": self.regional_distribution(),
            "category_breakdown": self.category_breakdown(),
            "graph_statistics": self.graph_store.get_statistics(),
        }

    def quarterly_revenue_trend(self) -> List[Dict[str, Any]]:
        """Calculate revenue by quarter from SOLD_IN relationships."""
        edges = self.graph_store.get_all_edges()
        quarter_revenue = defaultdict(float)

        for edge in edges:
            if edge.get("relation") == "SOLD_IN":
                target = edge.get("target", "")
                amount = edge.get("amount", 0)
                if target.startswith("QTR-"):
                    quarter_name = target.replace("QTR-", "")
                    quarter_revenue[quarter_name] += float(amount)

        # Sort chronologically
        sorted_quarters = sorted(
            quarter_revenue.items(),
            key=lambda x: (x[0].split("-")[1], x[0].split("-")[0]),
        )

        return [
            {"quarter": q, "revenue": round(r, 2)}
            for q, r in sorted_quarters
        ]

    def top_products_by_revenue(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find top products by total revenue from SOLD edges."""
        edges = self.graph_store.get_all_edges()
        product_revenue = defaultdict(float)
        product_count = defaultdict(int)

        for edge in edges:
            if edge.get("relation") == "SOLD":
                product_id = edge.get("target", "")
                amount = edge.get("amount", 0)
                if product_id.startswith("PROD-"):
                    product_revenue[product_id] += float(amount)
                    product_count[product_id] += 1

        results = []
        for pid, revenue in sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:limit]:
            node = self.graph_store.get_node(pid)
            name = node.get("name", pid) if node else pid
            results.append({
                "product_id": pid,
                "product_name": name,
                "total_revenue": round(revenue, 2),
                "transaction_count": product_count[pid],
            })

        return results

    def top_customers_by_spend(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find top customers by total spending from PURCHASED edges."""
        edges = self.graph_store.get_all_edges()
        customer_spend = defaultdict(float)
        customer_count = defaultdict(int)

        for edge in edges:
            if edge.get("relation") == "PURCHASED":
                customer_id = edge.get("source", "")
                amount = edge.get("amount", 0)
                if customer_id.startswith("CUST-"):
                    customer_spend[customer_id] += float(amount)
                    customer_count[customer_id] += 1

        results = []
        for cid, spend in sorted(customer_spend.items(), key=lambda x: x[1], reverse=True)[:limit]:
            node = self.graph_store.get_node(cid)
            name = node.get("name", cid) if node else cid
            results.append({
                "customer_id": cid,
                "customer_name": name,
                "total_spend": round(spend, 2),
                "purchase_count": customer_count[cid],
            })

        return results

    def department_performance(self) -> List[Dict[str, Any]]:
        """Analyze department performance based on employee sales."""
        edges = self.graph_store.get_all_edges()
        nodes = self.graph_store.get_all_nodes()

        # Map employees to departments
        emp_dept = {}
        for edge in edges:
            if edge.get("relation") == "WORKS_IN":
                emp_dept[edge["source"]] = edge["target"]

        # Aggregate sales by department
        dept_revenue = defaultdict(float)
        dept_sales_count = defaultdict(int)
        dept_employees = defaultdict(set)

        for edge in edges:
            if edge.get("relation") == "SOLD":
                emp_id = edge.get("source", "")
                amount = edge.get("amount", 0)
                dept_id = emp_dept.get(emp_id, "Unknown")
                dept_revenue[dept_id] += float(amount)
                dept_sales_count[dept_id] += 1
                dept_employees[dept_id].add(emp_id)

        results = []
        for dept_id in dept_revenue:
            node = self.graph_store.get_node(dept_id)
            name = node.get("name", dept_id) if node else dept_id
            emp_count = len(dept_employees[dept_id])
            results.append({
                "department_id": dept_id,
                "department_name": name,
                "total_revenue": round(dept_revenue[dept_id], 2),
                "sales_count": dept_sales_count[dept_id],
                "active_sellers": emp_count,
                "revenue_per_seller": round(dept_revenue[dept_id] / emp_count, 2) if emp_count else 0,
            })

        return sorted(results, key=lambda x: x["total_revenue"], reverse=True)

    def regional_distribution(self) -> List[Dict[str, Any]]:
        """Analyze customer and revenue distribution by region."""
        edges = self.graph_store.get_all_edges()

        # Map customers to regions
        customer_region = {}
        for edge in edges:
            if edge.get("relation") == "LOCATED_IN" and edge["source"].startswith("CUST-"):
                customer_region[edge["source"]] = edge["target"]

        # Aggregate by region
        region_revenue = defaultdict(float)
        region_customers = defaultdict(set)

        for edge in edges:
            if edge.get("relation") == "PURCHASED":
                cust_id = edge.get("source", "")
                amount = edge.get("amount", 0)
                region_id = customer_region.get(cust_id, "Unknown")
                region_revenue[region_id] += float(amount)
                region_customers[region_id].add(cust_id)

        results = []
        for region_id in region_revenue:
            node = self.graph_store.get_node(region_id)
            name = node.get("name", region_id) if node else region_id
            results.append({
                "region_id": region_id,
                "region_name": name,
                "total_revenue": round(region_revenue[region_id], 2),
                "customer_count": len(region_customers[region_id]),
            })

        return sorted(results, key=lambda x: x["total_revenue"], reverse=True)

    def category_breakdown(self) -> List[Dict[str, Any]]:
        """Analyze product category performance."""
        edges = self.graph_store.get_all_edges()

        # Map products to categories
        product_category = {}
        for edge in edges:
            if edge.get("relation") == "IN_CATEGORY":
                product_category[edge["source"]] = edge["target"]

        # Aggregate sales by category
        cat_revenue = defaultdict(float)
        cat_count = defaultdict(int)

        for edge in edges:
            if edge.get("relation") == "SOLD":
                product_id = edge.get("target", "")
                amount = edge.get("amount", 0)
                cat_id = product_category.get(product_id, "Unknown")
                cat_revenue[cat_id] += float(amount)
                cat_count[cat_id] += 1

        results = []
        for cat_id in cat_revenue:
            node = self.graph_store.get_node(cat_id)
            name = node.get("name", cat_id) if node else cat_id
            results.append({
                "category_id": cat_id,
                "category_name": name,
                "total_revenue": round(cat_revenue[cat_id], 2),
                "transaction_count": cat_count[cat_id],
            })

        return sorted(results, key=lambda x: x["total_revenue"], reverse=True)
