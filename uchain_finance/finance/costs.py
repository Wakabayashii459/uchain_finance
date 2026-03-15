import pandas as pd


def annual_operating_costs() -> pd.DataFrame:
    data = [
        {"cost_item": "Staff", "annual_cost_gbp": 420000},
        {"cost_item": "Cloud", "annual_cost_gbp": 60000},
        {"cost_item": "Data", "annual_cost_gbp": 35000},
        {"cost_item": "Office", "annual_cost_gbp": 50000},
        {"cost_item": "Professional Fees", "annual_cost_gbp": 40000},
    ]
    return pd.DataFrame(data)
