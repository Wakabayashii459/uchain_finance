import pandas as pd


def build_cashflow(generator_net, customer_net, opex, assumptions):

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    seasonality = [0.08,0.07,0.08,0.09,0.10,0.11,0.11,0.10,0.09,0.07,0.05,0.05]

    rows = []

    cash = assumptions["opening_cash"]
    min_cash = assumptions["minimum_cash_buffer"]
    debt = 0

    for i, m in enumerate(months):

        inflow = (generator_net + customer_net) * seasonality[i]

        monthly_opex = opex / 12

        net_cash = inflow - monthly_opex

        cash += net_cash

        if cash < min_cash:
            debt_draw = min_cash - cash
            debt += debt_draw
            cash += debt_draw
        else:
            debt_draw = 0

        rows.append(
            {
                "month": m,
                "cashflow": net_cash,
                "cash_balance": cash,
                "debt_draw": debt_draw,
                "total_debt": debt
            }
        )

    return pd.DataFrame(rows)
