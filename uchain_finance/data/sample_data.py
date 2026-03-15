import pandas as pd


def build_generators():

    data = [
        {
            "generator_id": "GEN_SOL_001",
            "technology": "solar",
            "annual_mwh": 24000,
            "platform_fee_per_mwh": 3.5,
            "imbalance_cost_per_mwh": 0.8,
            "contract_years": 5,
            "payment_delay_days": 30
        },
        {
            "generator_id": "GEN_WIND_001",
            "technology": "wind",
            "annual_mwh": 36000,
            "platform_fee_per_mwh": 3.0,
            "imbalance_cost_per_mwh": 1.0,
            "contract_years": 6,
            "payment_delay_days": 30
        },
        {
            "generator_id": "GEN_HYDRO_001",
            "technology": "hydro",
            "annual_mwh": 12000,
            "platform_fee_per_mwh": 4.0,
            "imbalance_cost_per_mwh": 0.4,
            "contract_years": 8,
            "payment_delay_days": 30
        }
    ]

    return pd.DataFrame(data)


def build_customers():

    data = [
        {
            "customer_id": "CUS_MFG_001",
            "sector": "manufacturing",
            "annual_mwh": 30000,
            "price_per_mwh": 82,
            "cost_to_serve": 6.5,
            "churn_probability": 0.04,
            "payment_delay_days": 45
        },
        {
            "customer_id": "CUS_DC_001",
            "sector": "data_centre",
            "annual_mwh": 26000,
            "price_per_mwh": 88,
            "cost_to_serve": 7.2,
            "churn_probability": 0.03,
            "payment_delay_days": 45
        },
        {
            "customer_id": "CUS_EDU_001",
            "sector": "education",
            "annual_mwh": 10000,
            "price_per_mwh": 79,
            "cost_to_serve": 5.5,
            "churn_probability": 0.06,
            "payment_delay_days": 60
        }
    ]

    return pd.DataFrame(data)
