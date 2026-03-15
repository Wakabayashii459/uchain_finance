import sys
import pandas as pd
from rich.console import Console
from rich.table import Table

from uchain_finance.data.loaders import load_generators, load_customers
from uchain_finance.data.assumptions import corporate_assumptions, operating_costs
from uchain_finance.finance.revenue import generator_metrics, customer_metrics
from uchain_finance.finance.cashflow import build_cashflow
from uchain_finance.finance.scenarios import (
    scenario_definitions,
    apply_scenario_to_generators,
    apply_scenario_to_customers,
    apply_scenario_to_opex,
)
from uchain_finance.finance.valuation import dcf_valuation
from uchain_finance.finance.capital import (
    build_capital_strategy,
    capital_strategy_summary,
)
from uchain_finance.reporting.export import export_dataframe

console = Console()


def calculate_base_case():
    generators = load_generators()
    customers = load_customers()
    assumptions = corporate_assumptions()
    opex_df = operating_costs()

    gen = generator_metrics(generators)
    cust = customer_metrics(customers)

    gen_net = gen["net_generator_contribution"].sum()
    cust_net = cust["net_customer_contribution"].sum()
    opex = opex_df["annual_cost"].sum()

    total_contribution = gen_net + cust_net
    operating_profit = total_contribution - opex

    base_revenue = gen["platform_fee_revenue"].sum() + cust["gross_revenue"].sum()

    cashflow = build_cashflow(gen_net, cust_net, opex, assumptions)

    return {
        "generators": generators,
        "customers": customers,
        "gen": gen,
        "cust": cust,
        "opex_df": opex_df,
        "assumptions": assumptions,
        "gen_net": gen_net,
        "cust_net": cust_net,
        "opex": opex,
        "total_contribution": total_contribution,
        "operating_profit": operating_profit,
        "base_revenue": base_revenue,
        "cashflow": cashflow,
    }


def calculate_scenario_case(name, scenario, generators, customers, base_opex, assumptions):
    gen_scn = apply_scenario_to_generators(generators, scenario)
    cust_scn = apply_scenario_to_customers(customers, scenario)
    opex_scn = apply_scenario_to_opex(base_opex, scenario)

    gen = generator_metrics(gen_scn)
    cust = customer_metrics(cust_scn)

    gen_net = gen["net_generator_contribution"].sum()
    cust_net = cust["net_customer_contribution"].sum()
    opex = opex_scn["annual_cost"].sum()

    total_contribution = gen_net + cust_net
    operating_profit = total_contribution - opex
    base_revenue = gen["platform_fee_revenue"].sum() + cust["gross_revenue"].sum()

    cashflow = build_cashflow(gen_net, cust_net, opex, assumptions)
    ending_cash = cashflow["cash_balance"].iloc[-1]
    total_debt = cashflow["total_debt"].iloc[-1]

    valuation = dcf_valuation(
        base_revenue=base_revenue,
        base_opex=opex,
        discount_rate=assumptions["discount_rate"],
        tax_rate=assumptions["tax_rate"],
        depreciation_percent_of_revenue=assumptions["depreciation_percent_of_revenue"],
        capex_percent_of_revenue=assumptions["capex_percent_of_revenue"],
        working_capital_percent_of_revenue=assumptions["working_capital_percent_of_revenue"],
        growth_rate=0.05,
        terminal_growth_rate=0.02,
        projection_years=5,
    )

    debt_df = build_capital_strategy(
        generator_net=gen_net,
        customer_net=cust_net,
        annual_opex=opex,
        assumptions=assumptions,
        funding_mode="debt",
    )
    equity_df = build_capital_strategy(
        generator_net=gen_net,
        customer_net=cust_net,
        annual_opex=opex,
        assumptions=assumptions,
        funding_mode="equity",
    )

    debt_summary = capital_strategy_summary(debt_df)
    equity_summary = capital_strategy_summary(equity_df)

    return {
        "scenario": name,
        "generator_net_contribution": gen_net,
        "customer_net_contribution": cust_net,
        "total_contribution": total_contribution,
        "opex": opex,
        "operating_profit": operating_profit,
        "ending_cash": ending_cash,
        "cashflow_total_debt": total_debt,
        "enterprise_value": valuation["enterprise_value"],
        "debt_ending_cash": debt_summary["ending_cash_gbp"],
        "debt_total_debt": debt_summary["total_debt_gbp"],
        "debt_interest_expense": debt_summary["total_interest_expense_gbp"],
        "equity_ending_cash": equity_summary["ending_cash_gbp"],
        "equity_total_equity_raised": equity_summary["total_equity_raised_gbp"],
    }


def show_summary():
    result = calculate_base_case()

    summary = Table(title="Commercial Finance Summary")
    summary.add_column("Metric")
    summary.add_column("Value", justify="right")

    summary.add_row("Generator net contribution (£)", f"{result['gen_net']:,.0f}")
    summary.add_row("Customer net contribution (£)", f"{result['cust_net']:,.0f}")
    summary.add_row("Total contribution (£)", f"{result['total_contribution']:,.0f}")
    summary.add_row("Annual opex (£)", f"{result['opex']:,.0f}")
    summary.add_row("Operating profit (£)", f"{result['operating_profit']:,.0f}")

    console.print(summary)


def show_cashflow():
    result = calculate_base_case()
    cashflow_df = result["cashflow"]

    summary = Table(title="Cash Flow Summary")
    summary.add_column("Metric")
    summary.add_column("Value", justify="right")

    summary.add_row("Generator net contribution (£)", f"{result['gen_net']:,.0f}")
    summary.add_row("Customer net contribution (£)", f"{result['cust_net']:,.0f}")
    summary.add_row("Annual opex (£)", f"{result['opex']:,.0f}")
    summary.add_row("Operating profit (£)", f"{result['operating_profit']:,.0f}")
    summary.add_row(
        "Ending cash balance (£)",
        f"{cashflow_df['cash_balance'].iloc[-1]:,.0f}",
    )
    summary.add_row(
        "Total debt drawn (£)",
        f"{cashflow_df['total_debt'].iloc[-1]:,.0f}",
    )

    console.print(summary)

    monthly = Table(title="Monthly Cash Flow")
    monthly.add_column("Month")
    monthly.add_column("Cashflow (£)", justify="right")
    monthly.add_column("Cash Balance (£)", justify="right")
    monthly.add_column("Debt Draw (£)", justify="right")

    for _, row in cashflow_df.iterrows():
        monthly.add_row(
            row["month"],
            f"{row['cashflow']:,.0f}",
            f"{row['cash_balance']:,.0f}",
            f"{row['debt_draw']:,.0f}",
        )

    console.print(monthly)


def get_scenario_results():
    generators = load_generators()
    customers = load_customers()
    assumptions = corporate_assumptions()
    base_opex = operating_costs()

    scenarios = scenario_definitions()

    results = []
    for name, scenario in scenarios.items():
        results.append(
            calculate_scenario_case(
                name=name,
                scenario=scenario,
                generators=generators,
                customers=customers,
                base_opex=base_opex,
                assumptions=assumptions,
            )
        )

    return pd.DataFrame(results)


def show_scenarios():
    results_df = get_scenario_results()

    summary = Table(title="Scenario Analysis Summary")
    summary.add_column("Scenario")
    summary.add_column("Operating Profit (£)", justify="right")
    summary.add_column("Enterprise Value (£)", justify="right")
    summary.add_column("Ending Cash (£)", justify="right")

    for _, r in results_df.iterrows():
        summary.add_row(
            r["scenario"],
            f"{r['operating_profit']:,.0f}",
            f"{r['enterprise_value']:,.0f}",
            f"{r['ending_cash']:,.0f}",
        )

    console.print(summary)

    capital = Table(title="Scenario Capital Comparison")
    capital.add_column("Scenario")
    capital.add_column("Debt Total (£)", justify="right")
    capital.add_column("Debt Interest (£)", justify="right")
    capital.add_column("Equity Raised (£)", justify="right")

    for _, r in results_df.iterrows():
        capital.add_row(
            r["scenario"],
            f"{r['debt_total_debt']:,.0f}",
            f"{r['debt_interest_expense']:,.0f}",
            f"{r['equity_total_equity_raised']:,.0f}",
        )

    console.print(capital)


def get_valuation_results():
    result = calculate_base_case()
    assumptions = result["assumptions"]

    valuation = dcf_valuation(
        base_revenue=result["base_revenue"],
        base_opex=result["opex"],
        discount_rate=assumptions["discount_rate"],
        tax_rate=assumptions["tax_rate"],
        depreciation_percent_of_revenue=assumptions["depreciation_percent_of_revenue"],
        capex_percent_of_revenue=assumptions["capex_percent_of_revenue"],
        working_capital_percent_of_revenue=assumptions["working_capital_percent_of_revenue"],
        growth_rate=0.05,
        terminal_growth_rate=0.02,
        projection_years=5,
    )

    return result, valuation


def show_valuation():
    result, valuation = get_valuation_results()
    assumptions = result["assumptions"]
    projected_df = valuation["projected_df"]

    summary = Table(title="DCF Valuation Summary")
    summary.add_column("Metric")
    summary.add_column("Value", justify="right")

    summary.add_row("Base revenue (£)", f"{result['base_revenue']:,.0f}")
    summary.add_row("Base opex (£)", f"{result['opex']:,.0f}")
    summary.add_row("Discount rate", f"{assumptions['discount_rate']:.1%}")
    summary.add_row("Tax rate", f"{assumptions['tax_rate']:.1%}")
    summary.add_row("Terminal value (£)", f"{valuation['terminal_value']:,.0f}")
    summary.add_row(
        "Discounted terminal value (£)",
        f"{valuation['discounted_terminal_value']:,.0f}",
    )
    summary.add_row("Enterprise value (£)", f"{valuation['enterprise_value']:,.0f}")

    console.print(summary)

    detail = Table(title="Projected Financials and Free Cash Flow")
    detail.add_column("Year")
    detail.add_column("Revenue (£)", justify="right")
    detail.add_column("EBIT (£)", justify="right")
    detail.add_column("Tax (£)", justify="right")
    detail.add_column("Capex (£)", justify="right")
    detail.add_column("ΔWC (£)", justify="right")
    detail.add_column("FCF (£)", justify="right")
    detail.add_column("PV of FCF (£)", justify="right")

    for _, row in projected_df.iterrows():
        detail.add_row(
            str(int(row["year"])),
            f"{row['revenue']:,.0f}",
            f"{row['ebit']:,.0f}",
            f"{row['tax']:,.0f}",
            f"{row['capex']:,.0f}",
            f"{row['delta_working_capital']:,.0f}",
            f"{row['free_cash_flow']:,.0f}",
            f"{row['present_value_fcf']:,.0f}",
        )

    console.print(detail)


def show_capital():
    result = calculate_base_case()
    assumptions = result["assumptions"]

    debt_df = build_capital_strategy(
        generator_net=result["gen_net"],
        customer_net=result["cust_net"],
        annual_opex=result["opex"],
        assumptions=assumptions,
        funding_mode="debt",
    )

    equity_df = build_capital_strategy(
        generator_net=result["gen_net"],
        customer_net=result["cust_net"],
        annual_opex=result["opex"],
        assumptions=assumptions,
        funding_mode="equity",
    )

    debt_summary = capital_strategy_summary(debt_df)
    equity_summary = capital_strategy_summary(equity_df)

    summary = Table(title="Capital Strategy Comparison")
    summary.add_column("Metric")
    summary.add_column("Debt Funding", justify="right")
    summary.add_column("Equity Funding", justify="right")

    summary.add_row("Ending cash (£)", f"{debt_summary['ending_cash_gbp']:,.0f}", f"{equity_summary['ending_cash_gbp']:,.0f}")
    summary.add_row("Total debt (£)", f"{debt_summary['total_debt_gbp']:,.0f}", f"{equity_summary['total_debt_gbp']:,.0f}")
    summary.add_row("Total equity raised (£)", f"{debt_summary['total_equity_raised_gbp']:,.0f}", f"{equity_summary['total_equity_raised_gbp']:,.0f}")
    summary.add_row("Interest expense (£)", f"{debt_summary['total_interest_expense_gbp']:,.0f}", f"{equity_summary['total_interest_expense_gbp']:,.0f}")

    console.print(summary)

    detail = Table(title="Monthly Funding Detail")
    detail.add_column("Month")
    detail.add_column("Debt Draw (£)", justify="right")
    detail.add_column("Debt Cash (£)", justify="right")
    detail.add_column("Equity Raise (£)", justify="right")
    detail.add_column("Equity Cash (£)", justify="right")

    for i in range(len(debt_df)):
        detail.add_row(
            debt_df.iloc[i]["month"],
            f"{debt_df.iloc[i]['debt_draw_gbp']:,.0f}",
            f"{debt_df.iloc[i]['cash_balance_gbp']:,.0f}",
            f"{equity_df.iloc[i]['equity_raise_gbp']:,.0f}",
            f"{equity_df.iloc[i]['cash_balance_gbp']:,.0f}",
        )

    console.print(detail)


def export_reports():
    result = calculate_base_case()
    scenario_df = get_scenario_results()
    _, valuation = get_valuation_results()

    commercial_summary_df = pd.DataFrame(
        [
            {"metric": "generator_net_contribution_gbp", "value": result["gen_net"]},
            {"metric": "customer_net_contribution_gbp", "value": result["cust_net"]},
            {"metric": "total_contribution_gbp", "value": result["total_contribution"]},
            {"metric": "annual_opex_gbp", "value": result["opex"]},
            {"metric": "operating_profit_gbp", "value": result["operating_profit"]},
            {"metric": "base_revenue_gbp", "value": result["base_revenue"]},
        ]
    )

    cashflow_df = result["cashflow"].copy()
    valuation_df = valuation["projected_df"].copy()

    paths = []
    paths.append(export_dataframe(commercial_summary_df, "commercial_summary.csv"))
    paths.append(export_dataframe(cashflow_df, "monthly_cashflow.csv"))
    paths.append(export_dataframe(scenario_df, "scenario_summary.csv"))
    paths.append(export_dataframe(valuation_df, "valuation_detail.csv"))

    console.print("[green]Export completed.[/green]")
    for path in paths:
        console.print(path)


def show_help():
    console.print("[bold cyan]Usage:[/bold cyan]")
    console.print("python -m uchain_finance.cli.main summary")
    console.print("python -m uchain_finance.cli.main cashflow")
    console.print("python -m uchain_finance.cli.main scenario")
    console.print("python -m uchain_finance.cli.main valuation")
    console.print("python -m uchain_finance.cli.main capital")
    console.print("python -m uchain_finance.cli.main export")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "summary":
        show_summary()
    elif command == "cashflow":
        show_cashflow()
    elif command == "scenario":
        show_scenarios()
    elif command == "valuation":
        show_valuation()
    elif command == "capital":
        show_capital()
    elif command == "export":
        export_reports()
    else:
        console.print(f"[red]Unknown command:[/red] {command}")
        show_help()


if __name__ == "__main__":
    main()
