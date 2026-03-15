import pandas as pd


def corporate_assumptions():

    data = {
        "tax_rate": 0.25,
        "discount_rate": 0.10,
        "debt_interest_rate": 0.06,
        "minimum_cash_buffer": 150000,
        "opening_cash": 250000,
    }

    return data


def operating_costs():

    rows = [
        {"cost_item": "Staff", "annual_cost": 420000},
        {"cost_item": "Cloud", "annual_cost": 60000},
        {"cost_item": "Data", "annual_cost": 35000},
        {"cost_item": "Office", "annual_cost": 50000},
        {"cost_item": "Professional Fees", "annual_cost": 40000},
    ]

    return pd.DataFrame(rows)
