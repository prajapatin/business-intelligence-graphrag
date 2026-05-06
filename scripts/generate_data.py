#!/usr/bin/env python3
"""Generate synthetic corporate data for the GraphRAG BI demo."""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")

# --- Configuration ---
DEPARTMENTS = [
    {"id": "DEPT-001", "name": "Engineering", "budget": 2500000, "head": None},
    {"id": "DEPT-002", "name": "Sales", "budget": 1800000, "head": None},
    {"id": "DEPT-003", "name": "Marketing", "budget": 1200000, "head": None},
    {"id": "DEPT-004", "name": "Finance", "budget": 900000, "head": None},
    {"id": "DEPT-005", "name": "Operations", "budget": 1500000, "head": None},
    {"id": "DEPT-006", "name": "Human Resources", "budget": 700000, "head": None},
]

PRODUCTS = [
    {"id": "PROD-001", "name": "CloudSync Pro", "category": "SaaS", "base_price": 299.99, "department": "DEPT-001"},
    {"id": "PROD-002", "name": "DataVault Enterprise", "category": "SaaS", "base_price": 599.99, "department": "DEPT-001"},
    {"id": "PROD-003", "name": "SecureNet Gateway", "category": "Hardware", "base_price": 1299.99, "department": "DEPT-001"},
    {"id": "PROD-004", "name": "AnalyticsDash", "category": "SaaS", "base_price": 199.99, "department": "DEPT-001"},
    {"id": "PROD-005", "name": "SmartOffice Suite", "category": "Software", "base_price": 449.99, "department": "DEPT-001"},
    {"id": "PROD-006", "name": "EdgeCompute Module", "category": "Hardware", "base_price": 899.99, "department": "DEPT-001"},
    {"id": "PROD-007", "name": "AI Assistant API", "category": "SaaS", "base_price": 149.99, "department": "DEPT-001"},
    {"id": "PROD-008", "name": "Compliance Tracker", "category": "Software", "base_price": 349.99, "department": "DEPT-004"},
]

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America"]


def generate_employees(n=60):
    employees = []
    dept_heads = {}

    for i in range(n):
        dept = random.choice(DEPARTMENTS)
        is_head = dept["id"] not in dept_heads and random.random() < 0.3
        role = "Department Head" if is_head else random.choice(
            ["Engineer", "Sales Rep", "Analyst", "Manager", "Specialist", "Coordinator"]
        )
        emp = {
            "id": f"EMP-{i+1:03d}",
            "name": fake.name(),
            "email": fake.company_email(),
            "department_id": dept["id"],
            "role": role,
            "hire_date": fake.date_between(start_date="-5y", end_date="-6m").isoformat(),
            "salary": round(random.uniform(55000, 180000), 2),
            "region": random.choice(REGIONS),
        }
        if is_head:
            dept_heads[dept["id"]] = emp["id"]
        employees.append(emp)

    # Assign heads
    for dept in DEPARTMENTS:
        dept["head"] = dept_heads.get(dept["id"], employees[0]["id"])

    return employees


def generate_customers(n=80):
    customers = []
    for i in range(n):
        customers.append({
            "id": f"CUST-{i+1:03d}",
            "company_name": fake.company(),
            "contact_name": fake.name(),
            "industry": random.choice(["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education"]),
            "region": random.choice(REGIONS),
            "tier": random.choice(["Enterprise", "Mid-Market", "SMB"]),
            "since": fake.date_between(start_date="-4y", end_date="-3m").isoformat(),
        })
    return customers


def generate_sales_transactions(employees, customers, n=500):
    transactions = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)

    sales_reps = [e for e in employees if e["role"] in ("Sales Rep", "Manager", "Department Head")]
    if not sales_reps:
        sales_reps = employees[:10]

    for i in range(n):
        product = random.choice(PRODUCTS)
        customer = random.choice(customers)
        rep = random.choice(sales_reps)
        tx_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

        # Add seasonal trends: Q4 gets a boost, Q1 dips
        month = tx_date.month
        seasonal_factor = 1.0
        if month in (10, 11, 12):
            seasonal_factor = random.uniform(1.2, 1.6)
        elif month in (1, 2):
            seasonal_factor = random.uniform(0.6, 0.85)
        elif month in (6, 7):
            seasonal_factor = random.uniform(1.05, 1.25)

        quantity = max(1, int(random.randint(1, 20) * seasonal_factor))
        unit_price = round(product["base_price"] * random.uniform(0.85, 1.15), 2)
        discount = round(random.uniform(0, 0.25), 2) if customer["tier"] == "Enterprise" else round(random.uniform(0, 0.10), 2)
        total = round(quantity * unit_price * (1 - discount), 2)

        transactions.append({
            "id": f"TX-{i+1:04d}",
            "date": tx_date.strftime("%Y-%m-%d"),
            "product_id": product["id"],
            "customer_id": customer["id"],
            "employee_id": rep["id"],
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "total_amount": total,
            "region": customer["region"],
            "status": random.choices(["Completed", "Pending", "Cancelled"], weights=[0.85, 0.10, 0.05])[0],
        })

    return transactions


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating employees...")
    employees = generate_employees(60)

    print("Generating customers...")
    customers = generate_customers(80)

    print("Generating sales transactions...")
    transactions = generate_sales_transactions(employees, customers, 500)

    # Save
    pd.DataFrame(DEPARTMENTS).to_csv(os.path.join(OUTPUT_DIR, "departments.csv"), index=False)
    pd.DataFrame(PRODUCTS).to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    pd.DataFrame(employees).to_csv(os.path.join(OUTPUT_DIR, "employees.csv"), index=False)
    pd.DataFrame(customers).to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
    pd.DataFrame(transactions).to_csv(os.path.join(OUTPUT_DIR, "sales_transactions.csv"), index=False)

    # Generate business reports
    print("Generating business reports...")
    reports = generate_business_reports(employees, customers, transactions)

    print(f"\nGenerated data saved to {OUTPUT_DIR}/")
    print(f"  - {len(DEPARTMENTS)} departments")
    print(f"  - {len(PRODUCTS)} products")
    print(f"  - {len(employees)} employees")
    print(f"  - {len(customers)} customers")
    print(f"  - {len(transactions)} sales transactions")
    print(f"  - {reports} business reports")


def generate_business_reports(employees, customers, transactions):
    """Generate synthetic business report text files from the structured data."""
    reports_dir = os.path.join(OUTPUT_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    tx_df = pd.DataFrame(transactions)
    emp_df = pd.DataFrame(employees)
    cust_df = pd.DataFrame(customers)
    prod_lookup = {p["id"]: p for p in PRODUCTS}
    dept_lookup = {d["id"]: d for d in DEPARTMENTS}

    report_count = 0

    # --- Quarterly Performance Reports (8 docs) ---
    for year in [2023, 2024]:
        for q in range(1, 5):
            q_start_month = (q - 1) * 3 + 1
            q_end_month = q * 3
            quarter_label = f"Q{q}-{year}"

            q_tx = tx_df[
                (tx_df["date"].str.startswith(str(year))) &
                (tx_df["date"].str.slice(5, 7).astype(int) >= q_start_month) &
                (tx_df["date"].str.slice(5, 7).astype(int) <= q_end_month) &
                (tx_df["status"] == "Completed")
            ]

            total_rev = q_tx["total_amount"].sum()
            tx_count = len(q_tx)
            top_prods = q_tx.groupby("product_id")["total_amount"].sum().sort_values(ascending=False).head(3)
            top_regions = q_tx.groupby("region")["total_amount"].sum().sort_values(ascending=False)
            top_reps = q_tx.groupby("employee_id")["total_amount"].sum().sort_values(ascending=False).head(5)

            lines = [
                f"{quarter_label} Quarterly Performance Report",
                f"=" * 50,
                f"",
                f"Executive Summary",
                f"-" * 30,
                f"This report covers the business performance for {quarter_label}. ",
                f"Total revenue for the quarter reached ${total_rev:,.2f} across {tx_count} completed transactions.",
                f"",
            ]

            if len(top_prods) > 0:
                lines.append("Top Performing Products")
                lines.append("-" * 30)
                for pid, rev in top_prods.items():
                    pname = prod_lookup.get(pid, {}).get("name", pid)
                    lines.append(f"- {pname}: ${rev:,.2f} in revenue")
                lines.append("")

            if len(top_regions) > 0:
                lines.append("Regional Performance")
                lines.append("-" * 30)
                for region, rev in top_regions.items():
                    pct = (rev / total_rev * 100) if total_rev > 0 else 0
                    lines.append(f"- {region}: ${rev:,.2f} ({pct:.1f}% of total)")
                lines.append("")

            if len(top_reps) > 0:
                lines.append("Top Sales Representatives")
                lines.append("-" * 30)
                for eid, rev in top_reps.items():
                    ename = emp_df[emp_df["id"] == eid]["name"].values
                    ename = ename[0] if len(ename) > 0 else eid
                    lines.append(f"- {ename}: ${rev:,.2f} in closed deals")
                lines.append("")

            seasonal = ""
            if q == 4:
                seasonal = "Q4 typically benefits from end-of-year budget spending and holiday season demand. "
            elif q == 1:
                seasonal = "Q1 often sees a dip as organizations finalize annual budgets. "
            elif q == 3:
                seasonal = "Q3 shows strong mid-year momentum as companies ramp up spending. "
            lines.append(f"Outlook: {seasonal}The team should focus on pipeline development for the next quarter.")

            filepath = os.path.join(reports_dir, f"quarterly_report_{quarter_label.lower().replace('-', '_')}.txt")
            with open(filepath, "w") as f:
                f.write("\n".join(lines))
            report_count += 1

    # --- Department Strategy Memos (6 docs) ---
    for dept in DEPARTMENTS:
        dept_emps = emp_df[emp_df["department_id"] == dept["id"]]
        dept_tx = tx_df[tx_df["employee_id"].isin(dept_emps["id"])]
        dept_rev = dept_tx[dept_tx["status"] == "Completed"]["total_amount"].sum()
        dept_products = [p for p in PRODUCTS if p["department"] == dept["id"]]

        lines = [
            f"Department Strategy Memo: {dept['name']}",
            "=" * 50,
            "",
            f"Department Overview",
            "-" * 30,
            f"The {dept['name']} department operates with an annual budget of ${dept['budget']:,.0f}. "
            f"The team consists of {len(dept_emps)} employees across various roles.",
            "",
        ]

        if dept_products:
            lines.append("Product Portfolio")
            lines.append("-" * 30)
            for p in dept_products:
                lines.append(f"- {p['name']} ({p['category']}): Base price ${p['base_price']}")
            lines.append("")

        roles = dept_emps["role"].value_counts()
        lines.append("Team Composition")
        lines.append("-" * 30)
        for role, count in roles.items():
            lines.append(f"- {role}: {count} staff")
        lines.append("")

        regions = dept_emps["region"].value_counts()
        lines.append("Geographic Distribution")
        lines.append("-" * 30)
        for region, count in regions.items():
            lines.append(f"- {region}: {count} employees")
        lines.append("")

        lines.append("Financial Performance")
        lines.append("-" * 30)
        lines.append(f"Total revenue generated by department staff: ${dept_rev:,.2f}")
        lines.append(f"Budget utilization ratio: {(dept_rev / dept['budget'] * 100):.1f}%" if dept['budget'] > 0 else "")
        lines.append("")
        lines.append(f"Strategic Priority: The {dept['name']} department should focus on expanding market reach "
                      f"and improving cross-team collaboration to drive growth in the upcoming fiscal year.")

        filepath = os.path.join(reports_dir, f"dept_memo_{dept['name'].lower().replace(' ', '_')}.txt")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        report_count += 1

    # --- Product Analysis Briefs (8 docs) ---
    for prod in PRODUCTS:
        prod_tx = tx_df[(tx_df["product_id"] == prod["id"]) & (tx_df["status"] == "Completed")]
        total_rev = prod_tx["total_amount"].sum()
        total_qty = prod_tx["quantity"].sum()
        avg_deal = prod_tx["total_amount"].mean() if len(prod_tx) > 0 else 0
        top_cust = prod_tx.groupby("customer_id")["total_amount"].sum().sort_values(ascending=False).head(3)
        region_sales = prod_tx.groupby("region")["total_amount"].sum().sort_values(ascending=False)

        lines = [
            f"Product Analysis Brief: {prod['name']}",
            "=" * 50,
            "",
            f"Product Profile",
            "-" * 30,
            f"{prod['name']} is a {prod['category']} product with a base price of ${prod['base_price']}. "
            f"It is developed and maintained by the {dept_lookup.get(prod['department'], {}).get('name', 'Unknown')} department.",
            "",
            f"Sales Performance",
            "-" * 30,
            f"Total revenue: ${total_rev:,.2f}",
            f"Total units sold: {total_qty}",
            f"Number of transactions: {len(prod_tx)}",
            f"Average deal size: ${avg_deal:,.2f}",
            "",
        ]

        if len(top_cust) > 0:
            lines.append("Top Customers")
            lines.append("-" * 30)
            for cid, rev in top_cust.items():
                cname = cust_df[cust_df["id"] == cid]["company_name"].values
                cname = cname[0] if len(cname) > 0 else cid
                lines.append(f"- {cname}: ${rev:,.2f}")
            lines.append("")

        if len(region_sales) > 0:
            lines.append("Regional Breakdown")
            lines.append("-" * 30)
            for region, rev in region_sales.items():
                lines.append(f"- {region}: ${rev:,.2f}")
            lines.append("")

        lines.append(f"Recommendation: {'Increase marketing spend to boost adoption.' if total_rev < 30000 else 'Maintain current strategy and explore upsell opportunities.'}")

        filepath = os.path.join(reports_dir, f"product_brief_{prod['id'].lower()}.txt")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        report_count += 1

    # --- Regional Market Summaries (4 docs) ---
    for region in REGIONS:
        reg_cust = cust_df[cust_df["region"] == region]
        reg_tx = tx_df[(tx_df["region"] == region) & (tx_df["status"] == "Completed")]
        reg_rev = reg_tx["total_amount"].sum()
        reg_emps = emp_df[emp_df["region"] == region]
        industries = reg_cust["industry"].value_counts()
        tiers = reg_cust["tier"].value_counts()
        top_prods = reg_tx.groupby("product_id")["total_amount"].sum().sort_values(ascending=False).head(3)

        lines = [
            f"Regional Market Summary: {region}",
            "=" * 50,
            "",
            f"Market Overview",
            "-" * 30,
            f"The {region} region has {len(reg_cust)} customers and {len(reg_emps)} employees. "
            f"Total revenue from this region is ${reg_rev:,.2f} across {len(reg_tx)} completed transactions.",
            "",
            f"Customer Segments",
            "-" * 30,
        ]

        for ind, count in industries.items():
            lines.append(f"- {ind}: {count} customers")
        lines.append("")
        lines.append("Customer Tiers")
        lines.append("-" * 30)
        for tier, count in tiers.items():
            lines.append(f"- {tier}: {count} customers")
        lines.append("")

        if len(top_prods) > 0:
            lines.append("Most Popular Products")
            lines.append("-" * 30)
            for pid, rev in top_prods.items():
                pname = prod_lookup.get(pid, {}).get("name", pid)
                lines.append(f"- {pname}: ${rev:,.2f}")
            lines.append("")

        lines.append(f"Growth Strategy: Focus on expanding the {industries.index[0] if len(industries) > 0 else 'core'} "
                      f"vertical and increasing Enterprise tier penetration in {region}.")

        filepath = os.path.join(reports_dir, f"regional_summary_{region.lower().replace(' ', '_')}.txt")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        report_count += 1

    # --- Customer Case Studies (10 docs) ---
    top_customers = tx_df[tx_df["status"] == "Completed"].groupby("customer_id")["total_amount"].sum().sort_values(ascending=False).head(10)
    for cid, total_spend in top_customers.items():
        cust_row = cust_df[cust_df["id"] == cid]
        if len(cust_row) == 0:
            continue
        cust_row = cust_row.iloc[0]
        cust_tx = tx_df[(tx_df["customer_id"] == cid) & (tx_df["status"] == "Completed")]
        products_bought = cust_tx.groupby("product_id")["total_amount"].sum().sort_values(ascending=False)

        lines = [
            f"Customer Case Study: {cust_row['company_name']}",
            "=" * 50,
            "",
            f"Company Profile",
            "-" * 30,
            f"{cust_row['company_name']} is a {cust_row['tier']} tier customer in the {cust_row['industry']} industry, "
            f"located in {cust_row['region']}. They have been a customer since {cust_row['since']}.",
            f"Primary contact: {cust_row['contact_name']}.",
            "",
            f"Purchasing History",
            "-" * 30,
            f"Total spend: ${total_spend:,.2f}",
            f"Number of purchases: {len(cust_tx)}",
            "",
            "Products Purchased",
            "-" * 30,
        ]

        for pid, rev in products_bought.items():
            pname = prod_lookup.get(pid, {}).get("name", pid)
            qty = cust_tx[cust_tx["product_id"] == pid]["quantity"].sum()
            lines.append(f"- {pname}: {qty} units, ${rev:,.2f} total")
        lines.append("")

        lines.append("Account Notes")
        lines.append("-" * 30)
        if cust_row["tier"] == "Enterprise":
            lines.append(f"{cust_row['company_name']} is a strategic enterprise account with significant growth potential. "
                          f"Consider offering volume discounts and dedicated account management.")
        elif cust_row["tier"] == "Mid-Market":
            lines.append(f"{cust_row['company_name']} shows strong engagement in the mid-market segment. "
                          f"Upselling to enterprise-grade solutions could increase account value.")
        else:
            lines.append(f"{cust_row['company_name']} is an SMB account that could benefit from our starter packages. "
                          f"Focus on demonstrating ROI to drive expansion.")

        filepath = os.path.join(reports_dir, f"case_study_{cid.lower()}.txt")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        report_count += 1

    # --- Annual Review (2 docs) ---
    for year in [2023, 2024]:
        yr_tx = tx_df[(tx_df["date"].str.startswith(str(year))) & (tx_df["status"] == "Completed")]
        yr_rev = yr_tx["total_amount"].sum()
        yr_count = len(yr_tx)
        yr_products = yr_tx.groupby("product_id")["total_amount"].sum().sort_values(ascending=False)
        yr_regions = yr_tx.groupby("region")["total_amount"].sum().sort_values(ascending=False)
        yr_quarterly = []
        for q in range(1, 5):
            qs = (q - 1) * 3 + 1
            qe = q * 3
            q_rev = yr_tx[
                (yr_tx["date"].str.slice(5, 7).astype(int) >= qs) &
                (yr_tx["date"].str.slice(5, 7).astype(int) <= qe)
            ]["total_amount"].sum()
            yr_quarterly.append((f"Q{q}", q_rev))

        lines = [
            f"{year} Annual Business Review",
            "=" * 50,
            "",
            f"Year in Review",
            "-" * 30,
            f"Fiscal year {year} generated a total revenue of ${yr_rev:,.2f} from {yr_count} completed transactions. "
            f"The company maintained steady growth across all product lines and regions.",
            "",
            "Quarterly Breakdown",
            "-" * 30,
        ]
        for qlabel, qrev in yr_quarterly:
            lines.append(f"- {qlabel}: ${qrev:,.2f}")
        lines.append("")

        lines.append("Product Revenue Rankings")
        lines.append("-" * 30)
        for pid, rev in yr_products.items():
            pname = prod_lookup.get(pid, {}).get("name", pid)
            lines.append(f"- {pname}: ${rev:,.2f}")
        lines.append("")

        lines.append("Regional Revenue Distribution")
        lines.append("-" * 30)
        for region, rev in yr_regions.items():
            pct = (rev / yr_rev * 100) if yr_rev > 0 else 0
            lines.append(f"- {region}: ${rev:,.2f} ({pct:.1f}%)")
        lines.append("")

        lines.append("Key Takeaways")
        lines.append("-" * 30)
        best_q = max(yr_quarterly, key=lambda x: x[1])
        worst_q = min(yr_quarterly, key=lambda x: x[1])
        lines.append(f"- Strongest quarter: {best_q[0]} with ${best_q[1]:,.2f}")
        lines.append(f"- Weakest quarter: {worst_q[0]} with ${worst_q[1]:,.2f}")
        if len(yr_products) > 0:
            lines.append(f"- Top product: {prod_lookup.get(yr_products.index[0], {}).get('name', yr_products.index[0])}")
        if len(yr_regions) > 0:
            lines.append(f"- Leading region: {yr_regions.index[0]}")
        lines.append("")
        lines.append(f"Looking ahead to {year + 1}, the organization should prioritize customer retention, "
                      f"product innovation, and geographic expansion to sustain growth momentum.")

        filepath = os.path.join(reports_dir, f"annual_review_{year}.txt")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        report_count += 1

    return report_count


if __name__ == "__main__":
    main()
