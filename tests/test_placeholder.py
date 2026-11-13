"""Smoke test ensuring test suite discovery and schemas import."""

from src.ingestion.schemas import DCFInputParams


def test_schema_smoke_test() -> None:
    params = DCFInputParams(
        ticker="HPG",
        current_market_price=28000.0,
        shares_outstanding=5814785700,
        base_fcf=12000000000000.0,
        stage1_growth_rate=0.08,
        stage1_years=5,
        terminal_growth_rate=0.025,
        wacc=0.11,
        net_debt=25000000000000.0,
    )
    assert params.ticker == "HPG"
    assert params.wacc > params.terminal_growth_rate
