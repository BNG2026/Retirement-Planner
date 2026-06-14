import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Retirement Planner - June",
    page_icon="💰",
    layout="wide",
)


def get_user_inputs() -> dict:
    st.sidebar.header("Retirement Inputs")

    current_age = st.sidebar.number_input(
        "Current age", min_value=18, max_value=100, value=35
    )
    retirement_age = st.sidebar.number_input(
        "Retirement age", min_value=current_age, max_value=100, value=65
    )
    life_expectancy = st.sidebar.number_input(
        "Life expectancy", min_value=retirement_age, max_value=120, value=90
    )

    st.sidebar.subheader("Current balances")
    traditional_ira_balance = st.sidebar.number_input(
        "Current Traditional IRA balance",
        min_value=0.0,
        value=100000.0,
        step=1000.0,
        format="%.2f",
    )
    roth_ira_balance = st.sidebar.number_input(
        "Current Roth IRA balance",
        min_value=0.0,
        value=50000.0,
        step=1000.0,
        format="%.2f",
    )
    mutual_fund_balance = st.sidebar.number_input(
        "Current mutual fund balance",
        min_value=0.0,
        value=75000.0,
        step=1000.0,
        format="%.2f",
    )

    annual_contribution = st.sidebar.number_input(
        "Annual contribution amount",
        min_value=0.0,
        value=10000.0,
        step=500.0,
        format="%.2f",
    )

    st.sidebar.subheader("Return and inflation")
    return_before_retirement = st.sidebar.number_input(
        "Expected annual return before retirement (%)",
        min_value=0.0,
        max_value=30.0,
        value=6.0,
        step=0.1,
    )
    return_after_retirement = st.sidebar.number_input(
        "Expected annual return after retirement (%)",
        min_value=0.0,
        max_value=20.0,
        value=4.0,
        step=0.1,
    )
    inflation_rate = st.sidebar.number_input(
        "Inflation rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        step=0.1,
    )

    st.sidebar.subheader("Retirement income and spending")
    annual_spending_goal = st.sidebar.number_input(
        "Annual retirement spending goal",
        min_value=0.0,
        value=60000.0,
        step=1000.0,
        format="%.2f",
    )
    monthly_pension = st.sidebar.number_input(
        "Monthly pension amount",
        min_value=0.0,
        value=1000.0,
        step=50.0,
        format="%.2f",
    )
    pension_start_age = st.sidebar.number_input(
        "Pension start age",
        min_value=current_age,
        max_value=120,
        value=65,
    )
    monthly_social_security = st.sidebar.number_input(
        "Monthly Social Security amount",
        min_value=0.0,
        value=1500.0,
        step=50.0,
        format="%.2f",
    )
    social_security_start_age = st.sidebar.number_input(
        "Social Security start age",
        min_value=current_age,
        max_value=120,
        value=67,
    )

    st.sidebar.subheader("Tax assumptions")
    traditional_ira_tax_rate = st.sidebar.number_input(
        "Estimated tax rate for Traditional IRA withdrawals (%)",
        min_value=0.0,
        max_value=50.0,
        value=20.0,
        step=0.5,
    )
    mutual_fund_tax_rate = st.sidebar.number_input(
        "Estimated tax rate for mutual fund withdrawals (%)",
        min_value=0.0,
        max_value=50.0,
        value=15.0,
        step=0.5,
    )

    return {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "life_expectancy": life_expectancy,
        "traditional_ira_balance": traditional_ira_balance,
        "roth_ira_balance": roth_ira_balance,
        "mutual_fund_balance": mutual_fund_balance,
        "annual_contribution": annual_contribution,
        "return_before_retirement": return_before_retirement / 100.0,
        "return_after_retirement": return_after_retirement / 100.0,
        "inflation_rate": inflation_rate / 100.0,
        "annual_spending_goal": annual_spending_goal,
        "monthly_pension": monthly_pension,
        "pension_start_age": pension_start_age,
        "monthly_social_security": monthly_social_security,
        "social_security_start_age": social_security_start_age,
        "traditional_ira_tax_rate": traditional_ira_tax_rate / 100.0,
        "mutual_fund_tax_rate": mutual_fund_tax_rate / 100.0,
    }


@st.cache_data
def calculate_projection(inputs: dict) -> pd.DataFrame:
    current_age = inputs["current_age"]
    retirement_age = inputs["retirement_age"]
    life_expectancy = inputs["life_expectancy"]
    traditional_ira = inputs["traditional_ira_balance"]
    roth_ira = inputs["roth_ira_balance"]
    mutual_fund = inputs["mutual_fund_balance"]
    annual_contribution = inputs["annual_contribution"]
    return_before_retirement = inputs["return_before_retirement"]
    return_after_retirement = inputs["return_after_retirement"]
    inflation_rate = inputs["inflation_rate"]
    annual_spending_goal = inputs["annual_spending_goal"]
    monthly_pension = inputs["monthly_pension"]
    pension_start_age = inputs["pension_start_age"]
    monthly_social_security = inputs["monthly_social_security"]
    social_security_start_age = inputs["social_security_start_age"]
    traditional_ira_tax_rate = inputs["traditional_ira_tax_rate"]
    mutual_fund_tax_rate = inputs["mutual_fund_tax_rate"]

    projection_years = list(range(current_age, life_expectancy + 1))
    results = []
    current_spending = annual_spending_goal
    funds_depleted_age = None

    for age in projection_years:
        before_retirement = age < retirement_age
        after_retirement = age >= retirement_age

        if before_retirement:
            traditional_ira *= 1 + return_before_retirement
            roth_ira *= 1 + return_before_retirement
            mutual_fund *= 1 + return_before_retirement
            traditional_ira += annual_contribution * 0.5
            roth_ira += annual_contribution * 0.3
            mutual_fund += annual_contribution * 0.2
        else:
            traditional_ira *= 1 + return_after_retirement
            roth_ira *= 1 + return_after_retirement
            mutual_fund *= 1 + return_after_retirement

        pension_income = 0.0
        social_security_income = 0.0
        withdrawal_traditional = 0.0
        withdrawal_mutual = 0.0
        withdrawal_roth = 0.0
        withdrawal_taxes = 0.0
        shortfall = 0.0

        if after_retirement:
            if age == retirement_age:
                current_spending = annual_spending_goal
            else:
                current_spending *= 1 + inflation_rate

            if age >= pension_start_age:
                pension_income = monthly_pension * 12
            if age >= social_security_start_age:
                social_security_income = monthly_social_security * 12

            income_needed = current_spending
            guaranteed_income = pension_income + social_security_income
            shortfall = max(0.0, income_needed - guaranteed_income)

            withdrawal_traditional = min(traditional_ira, shortfall)
            traditional_ira -= withdrawal_traditional
            shortfall -= withdrawal_traditional

            withdrawal_mutual = min(mutual_fund, shortfall)
            mutual_fund -= withdrawal_mutual
            shortfall -= withdrawal_mutual

            withdrawal_roth = min(roth_ira, shortfall)
            roth_ira -= withdrawal_roth
            shortfall -= withdrawal_roth

            withdrawal_taxes = (
                withdrawal_traditional * traditional_ira_tax_rate
                + withdrawal_mutual * mutual_fund_tax_rate
            )

            if funds_depleted_age is None and total_balance := traditional_ira + roth_ira + mutual_fund:
                if total_balance <= 0.01 and any(
                    x > 0 for x in [withdrawal_traditional, withdrawal_mutual, withdrawal_roth]
                ):
                    funds_depleted_age = age

        total_balance = traditional_ira + roth_ira + mutual_fund
        results.append(
            {
                "Age": age,
                "Traditional IRA": round(traditional_ira, 2),
                "Roth IRA": round(roth_ira, 2),
                "Mutual Fund": round(mutual_fund, 2),
                "Total Balance": round(total_balance, 2),
                "Annual Spending Goal": round(current_spending if after_retirement else 0.0, 2),
                "Pension Income": round(pension_income, 2),
                "Social Security Income": round(social_security_income, 2),
                "Shortfall": round(shortfall if after_retirement else 0.0, 2),
                "Withdrawn from Traditional IRA": round(withdrawal_traditional, 2),
                "Withdrawn from Mutual Fund": round(withdrawal_mutual, 2),
                "Withdrawn from Roth IRA": round(withdrawal_roth, 2),
                "Withdrawal Taxes": round(withdrawal_taxes, 2),
            }
        )

    df = pd.DataFrame(results)
    df["Total Balance"] = df["Total Balance"].astype(float)
    df["Age"] = df["Age"].astype(int)
    df.attrs["funds_depleted_age"] = funds_depleted_age
    return df


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def main() -> None:
    st.title("Retirement Planning Simulator - June Project")
    st.write(
        "Enter your retirement assumptions on the left, then review the projected balances, income sources, "
        "and withdrawal schedule in the main panel."
    )

    inputs = get_user_inputs()

    if inputs["retirement_age"] <= inputs["current_age"]:
        st.error("Retirement age must be greater than current age.")
        return

    if inputs["life_expectancy"] <= inputs["retirement_age"]:
        st.error("Life expectancy should be greater than retirement age.")
        return

    projection_df = calculate_projection(inputs)
    funds_depleted_age = projection_df.attrs.get("funds_depleted_age")

    retirement_df = projection_df[projection_df["Age"] >= inputs["retirement_age"]]
    retirement_balance = projection_df.loc[projection_df["Age"] == inputs["retirement_age"], "Total Balance"].iloc[0]

    st.header("Projection Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Projected balance at retirement", format_currency(retirement_balance))
    col2.metric("Projection end age", inputs["life_expectancy"])
    col3.metric(
        "Estimated funds depleted age",
        funds_depleted_age if funds_depleted_age is not None else "Not within projection",
    )

    st.header("Retirement Income and Withdrawal Details")
    st.write(
        "Review income sources, estimated shortfall, and withdrawal amounts during retirement years."
    )
    st.dataframe(
        retirement_df[
            [
                "Age",
                "Annual Spending Goal",
                "Pension Income",
                "Social Security Income",
                "Shortfall",
                "Withdrawn from Traditional IRA",
                "Withdrawn from Mutual Fund",
                "Withdrawn from Roth IRA",
                "Withdrawal Taxes",
            ]
        ].reset_index(drop=True)
    )

    st.header("Portfolio Balance Over Time")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(projection_df["Age"], projection_df["Total Balance"], marker="o", linestyle="-", color="#0b5394")
    ax.set_xlabel("Age")
    ax.set_ylabel("Total Portfolio Balance")
    ax.set_title("Projected Total Portfolio Balance by Age")
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

    st.header("Full Projection Table")
    st.dataframe(projection_df)

    st.markdown("---")
    st.subheader("Run this app locally")
    st.markdown(
        "1. Install Streamlit with `pip install streamlit pandas matplotlib`.<br>"
        "2. Run `streamlit run retirement_planner_june.py` from this folder.<br>"
        "3. Open the browser window that Streamlit opens automatically.",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
