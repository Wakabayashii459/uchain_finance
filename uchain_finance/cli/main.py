from rich.console import Console
from rich.table import Table

from uchain_finance.data.loaders import load_generators, load_customers
from uchain_finance.data.assumptions import corporate_assumptions, operating_costs
from uchain_finance.finance.revenue import generator_metrics, customer_metrics
from uchain_finance.finance.cashflow import build_cashflow

console = Console()


def main():

    generators = load_generators()
    customers = load_customers()

    assumptions = corporate_assumptions()

    gen = generator_metrics(generators)
    cust = customer_metrics(customers)

    opex = operating_costs()["annual_cost"].sum()

    gen_net = gen["net_generator_contribution"].sum()
    cust_net = cust["net_customer_contribution"].sum()

    cashflow = build_cashflow(gen_net, cust_net, opex, assumptions)

    summary = Table(title="Commercial Finance Summary")

    summary.add_column("Metric")
    summary.add_column("Value")

    summary.add_row("Generator net contribution", f"{gen_net:,.0f}")
    summary.add_row("Customer net contribution", f"{cust_net:,.0f}")
    summary.add_row("Operating expenses", f"{opex:,.0f}")
    summary.add_row("Ending cash", f"{cashflow['cash_balance'].iloc[-1]:,.0f}")
    summary.add_row("Total debt drawn", f"{cashflow['total_debt'].iloc[-1]:,.0f}")

    console.print(summary)

    table = Table(title="Monthly Cashflow")

    table.add_column("Month")
    table.add_column("Cashflow")
    table.add_column("Cash Balance")
    table.add_column("Debt Draw")

    for _, r in cashflow.iterrows():
        table.add_row(
            r["month"],
            f"{r['cashflow']:,.0f}",
            f"{r['cash_balance']:,.0f}",
            f"{r['debt_draw']:,.0f}",
        )

    console.print(table)


if __name__ == "__main__":
    main()
