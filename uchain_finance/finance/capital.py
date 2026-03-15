import pandas as pd


def build_capital_strategy(
    generator_net: float,
    customer_net: float,
    annual_opex: float,
    assumptions: dict,
    funding_mode: str = "debt",
) -> pd.DataFrame:
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    seasonality = [0.08, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11, 0.10, 0.09, 0.07, 0.05, 0.05]

    cash = assumptions["opening_cash"]
    min_cash = assumptions["minimum_cash_buffer"]
    annual_interest_rate = assumptions["debt_interest_rate"]
    monthly_interest_rate = annual_interest_rate / 12

    total_debt = 0.0
    total_equity_raised = 0.0

    rows = []

    for i, month in enumerate(months):
        inflow = (generator_net + customer_net) * seasonality[i]
        monthly_opex = annual_opex / 12

        interest_expense = total_debt * monthly_interest_rate
        net_cashflow_before_funding = inflow - monthly_opex - interest_expense

        cash += net_cashflow_before_funding

        debt_draw = 0.0
        equity_raise = 0.0

        if cash < min_cash:
            funding_needed = min_cash - cash

            if funding_mode == "debt":
                debt_draw = funding_needed
                total_debt += debt_draw
                cash += debt_draw
            elif funding_mode == "equity":
                equity_raise = funding_needed
                total_equity_raised += equity_raise
                cash += equity_raise

        rows.append(
            {
                "month": month,
                "funding_mode": funding_mode,
                "cash_inflow_gbp": inflow,
                "opex_gbp": monthly_opex,
                "interest_expense_gbp": interest_expense,
                "net_cashflow_before_funding_gbp": net_cashflow_before_funding,
                "debt_draw_gbp": debt_draw,
                "equity_raise_gbp": equity_raise,
                "cash_balance_gbp": cash,
                "total_debt_gbp": total_debt,
                "total_equity_raised_gbp": total_equity_raised,
            }
        )

    return pd.DataFrame(rows)


def capital_strategy_summary(df: pd.DataFrame) -> dict:
    return {
        "funding_mode": df["funding_mode"].iloc[-1],
        "ending_cash_gbp": df["cash_balance_gbp"].iloc[-1],
        "total_debt_gbp": df["total_debt_gbp"].iloc[-1],
        "total_equity_raised_gbp": df["total_equity_raised_gbp"].iloc[-1],
        "total_interest_expense_gbp": df["interest_expense_gbp"].sum(),
    }
