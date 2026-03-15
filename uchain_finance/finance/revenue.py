import pandas as pd


def generator_metrics(df):

    df = df.copy()

    df["platform_fee_revenue"] = df["annual_mwh"] * df["platform_fee_per_mwh"]

    df["imbalance_cost"] = df["annual_mwh"] * df["imbalance_cost_per_mwh"]

    df["net_generator_contribution"] = (
        df["platform_fee_revenue"] - df["imbalance_cost"]
    )

    df["margin_per_mwh"] = (
        df["platform_fee_per_mwh"] - df["imbalance_cost_per_mwh"]
    )

    return df


def customer_metrics(df):

    df = df.copy()

    df["gross_revenue"] = df["annual_mwh"] * df["price_per_mwh"]

    df["cost_of_sales"] = df["annual_mwh"] * df["cost_to_serve"]

    df["net_customer_contribution"] = df["gross_revenue"] - df["cost_of_sales"]

    df["margin_percent"] = df["net_customer_contribution"] / df["gross_revenue"]

    return df
