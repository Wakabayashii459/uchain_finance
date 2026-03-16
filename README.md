# uchain_finance

`uchain_finance` is a Python-based financial modelling prototype for an energy-platform.

The model includes:

- Commercial finance metrics (generator and customer contribution)
- Monthly cash-flow forecasting
- Scenario analysis (base / downside / upside)
- Discounted cash flow valuation
- Capital strategy comparison (debt vs equity funding)
- Exportable reporting outputs for dashboard tools such as PowerBI

The project is structured into modular components covering data inputs, financial modelling logic, capital strategy, and reporting/export functions.

## Run

```bash
python -m uchain_finance.cli.main summary
python -m uchain_finance.cli.main cashflow
python -m uchain_finance.cli.main scenario
python -m uchain_finance.cli.main valuation
python -m uchain_finance.cli.main capital
python -m uchain_finance.cli.main export
