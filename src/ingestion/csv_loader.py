import os
from typing import Dict

import pandas as pd
from loguru import logger


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic")


def load_all_data(data_dir: str = DATA_DIR) -> Dict[str, pd.DataFrame]:
    """Load all synthetic CSV files into DataFrames.

    Returns:
        Dictionary mapping table name to DataFrame.
    """
    tables = {}
    csv_files = {
        "departments": "departments.csv",
        "products": "products.csv",
        "employees": "employees.csv",
        "customers": "customers.csv",
        "sales_transactions": "sales_transactions.csv",
    }

    for name, filename in csv_files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            logger.warning(f"Missing data file: {path}")
            continue
        df = pd.read_csv(path)
        tables[name] = df
        logger.info(f"Loaded {name}: {len(df)} rows")

    return tables
