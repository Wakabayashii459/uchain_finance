import pandas as pd


def scenario_definitions():
    return {
        "base": {
            "customer_price_multiplier": 1.00,
            "customer_volume_multiplier": 1.00,
            "generator_volume_multiplier": 1.00,
            "cost_to_serve_multiplier": 1.00,
            "imbalance_cost_multiplier": 1.00,
            "opex_multiplier": 1.00,
        },
        "downside": {
            "customer_price_multiplier": 0.95,
            "customer_volume_multiplier": 0.92,
            "generator_volume_multiplier": 0.95,
            "cost_to_serve_multiplier": 1.10,
            "imbalance_cost_multiplier": 1.20,
            "opex_multiplier": 1.08,
        },
        "upside": {
            "customer_price_multiplier": 1.04,
            "customer_volume_multiplier": 1.08,
            "generator_volume_multiplier": 1.05,
            "cost_to_serve_multiplier": 0.98,
            "imbalance_cost_multiplier": 0.95,
            "opex_multiplier": 1.03,
        },
    }


def apply_scenario_to_generators(generators: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    df = generators.copy()

    df["annual_mwh"] = df["annual_mwh"] * scenario["generator_volume_multiplier"]
    df["imbalance_cost_per_mwh"] = (
        df["imbalance_cost_per_mwh"] * scenario["imbalance_cost_multiplier"]
    )

    return df


def apply_scenario_to_customers(customers: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    df = customers.copy()

    df["annual_mwh"] = df["annual_mwh"] * scenario["customer_volume_multiplier"]
    df["price_per_mwh"] = df["price_per_mwh"] * scenario["customer_price_multiplier"]
    df["cost_to_serve"] = df["cost_to_serve"] * scenario["cost_to_serve_multiplier"]

    return df


def apply_scenario_to_opex(opex_df: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    df = opex_df.copy()
    df["annual_cost"] = df["annual_cost"] * scenario["opex_multiplier"]
    return df
