import pandas as pd


def project_financials(
    base_revenue: float,
    base_opex: float,
    growth_rate: float,
    tax_rate: float,
    depreciation_percent_of_revenue: float,
    capex_percent_of_revenue: float,
    working_capital_percent_of_revenue: float,
    projection_years: int,
) -> pd.DataFrame:
    rows = []

    revenue = base_revenue
    previous_working_capital = base_revenue * working_capital_percent_of_revenue

    for year in range(1, projection_years + 1):
        if year > 1:
            revenue = revenue * (1 + growth_rate)

        opex = base_opex * ((1 + growth_rate) ** (year - 1))

        ebit = revenue - opex

        tax = max(ebit, 0) * tax_rate

        depreciation = revenue * depreciation_percent_of_revenue
        capex = revenue * capex_percent_of_revenue

        working_capital = revenue * working_capital_percent_of_revenue
        delta_working_capital = working_capital - previous_working_capital

        free_cash_flow = (
            ebit
            - tax
            + depreciation
            - capex
            - delta_working_capital
        )

        rows.append(
            {
                "year": year,
                "revenue": revenue,
                "opex": opex,
                "ebit": ebit,
                "tax": tax,
                "depreciation": depreciation,
                "capex": capex,
                "working_capital": working_capital,
                "delta_working_capital": delta_working_capital,
                "free_cash_flow": free_cash_flow,
            }
        )

        previous_working_capital = working_capital

    return pd.DataFrame(rows)


def discount_financials(df: pd.DataFrame, discount_rate: float) -> pd.DataFrame:
    out = df.copy()
    out["discount_factor"] = 1 / ((1 + discount_rate) ** out["year"])
    out["present_value_fcf"] = out["free_cash_flow"] * out["discount_factor"]
    return out


def terminal_value(
    final_year_fcf: float,
    discount_rate: float,
    terminal_growth_rate: float,
) -> float:
    return final_year_fcf * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)


def dcf_valuation(
    base_revenue: float,
    base_opex: float,
    discount_rate: float,
    tax_rate: float,
    depreciation_percent_of_revenue: float,
    capex_percent_of_revenue: float,
    working_capital_percent_of_revenue: float,
    growth_rate: float = 0.05,
    terminal_growth_rate: float = 0.02,
    projection_years: int = 5,
) -> dict:
    projected = project_financials(
        base_revenue=base_revenue,
        base_opex=base_opex,
        growth_rate=growth_rate,
        tax_rate=tax_rate,
        depreciation_percent_of_revenue=depreciation_percent_of_revenue,
        capex_percent_of_revenue=capex_percent_of_revenue,
        working_capital_percent_of_revenue=working_capital_percent_of_revenue,
        projection_years=projection_years,
    )

    discounted = discount_financials(projected, discount_rate)

    final_year_fcf = discounted["free_cash_flow"].iloc[-1]

    tv = terminal_value(
        final_year_fcf=final_year_fcf,
        discount_rate=discount_rate,
        terminal_growth_rate=terminal_growth_rate,
    )

    discounted_terminal_value = tv / ((1 + discount_rate) ** projection_years)

    enterprise_value = discounted["present_value_fcf"].sum() + discounted_terminal_value

    return {
        "projected_df": discounted,
        "terminal_value": tv,
        "discounted_terminal_value": discounted_terminal_value,
        "enterprise_value": enterprise_value,
    }
