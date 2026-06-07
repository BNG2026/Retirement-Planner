import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Simple retirement planning app using Streamlit, pandas, and matplotlib.
# This app projects account balances year by year through life expectancy.

st.title("Retirement Planning Simulator")
st.write(
    "Enter your retirement assumptions on the left, then review the projected balances, income sources, "
    "and withdrawal schedule in the main panel."
)

# Sidebar inputs for assumptions.
st.sidebar.header("Retirement Inputs")
current_age = st.sidebar.number_input("Current age", min_value=18, max_value=100, value=35)
retirement_age = st.sidebar.number_input("Retirement age", min_value=current_age, max_value=100, value=65)
life_expectancy = st.sidebar.number_input("Life expectancy", min_value=retirement_age, max_value=120, value=90)

st.sidebar.subheader("Current balances")
traditional_ira_balance = st.sidebar.number_input("Current Traditional IRA balance", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
roth_ira_balance = st.sidebar.number_input("Current Roth IRA balance", min_value=0.0, value=50000.0, step=1000.0, format="%.2f")
mutual_fund_balance = st.sidebar.number_input("Current mutual fund balance", min_value=0.0, value=75000.0, step=1000.0, format="%.2f")

annual_contribution = st.sidebar.number_input("Annual contribution amount", min_value=0.0, value=10000.0, step=500.0, format="%.2f")

st.sidebar.subheader("Return and inflation")
return_before_retirement = st.sidebar.number_input("Expected annual return before retirement (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.1) / 100.0
return_after_retirement = st.sidebar.number_input("Expected annual return after retirement (%)", min_value=0.0, max_value=20.0, value=4.0, step=0.1) / 100.0
inflation_rate = st.sidebar.number_input("Inflation rate (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1) / 100.0

st.sidebar.subheader("Retirement income and spending")
annual_spending_goal = st.sidebar.number_input("Annual retirement spending goal", min_value=0.0, value=60000.0, step=1000.0, format="%.2f")
monthly_pension = st.sidebar.number_input("Monthly pension amount", min_value=0.0, value=1000.0, step=50.0, format="%.2f")
pension_start_age = st.sidebar.number_input("Pension start age", min_value=current_age, max_value=120, value=65)
monthly_social_security = st.sidebar.number_input("Monthly Social Security amount", min_value=0.0, value=1500.0, step=50.0, format="%.2f")
social_security_start_age = st.sidebar.number_input("Social Security start age", min_value=current_age, max_value=120, value=67)

st.sidebar.subheader("Tax assumptions")
traditional_ira_tax_rate = st.sidebar.number_input("Estimated tax rate for Traditional IRA withdrawals (%)", min_value=0.0, max_value=50.0, value=20.0, step=0.5) / 100.0
mutual_fund_tax_rate = st.sidebar.number_input("Estimated tax rate for mutual fund withdrawals (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.5) / 100.0

# Validate retirement age and life expectancy.
if retirement_age <= current_age:
    st.sidebar.error("Retirement age must be greater than current age.")
if life_expectancy <= retirement_age:
    st.sidebar.error("Life expectancy should be greater than retirement age.")

# Project year-by-year results in a DataFrame.
projection_years = list(range(current_age, life_expectancy + 1))

results = []
traditional_ira = traditional_ira_balance
roth_ira = roth_ira_balance
mutual_fund = mutual_fund_balance
current_spending = annual_spending_goal
funds_depleted_age = None

for age in projection_years:
    # Determine whether we are before or after retirement.
    before_retirement = age < retirement_age
    after_retirement = age >= retirement_age

    # Grow accounts by return.
    if before_retirement:
        traditional_ira *= 1 + return_before_retirement
        roth_ira *= 1 + return_before_retirement
        mutual_fund *= 1 + return_before_retirement
    else:
        traditional_ira *= 1 + return_after_retirement
        roth_ira *= 1 + return_after_retirement
        mutual_fund *= 1 + return_after_retirement

    # Add contributions before retirement.
    contribution = annual_contribution if before_retirement else 0.0
    if before_retirement:
        traditional_ira += contribution * 0.5
        roth_ira += contribution * 0.3
        mutual_fund += contribution * 0.2

    pension_income = 0.0
    social_security_income = 0.0
    withdrawal_traditional = 0.0
    withdrawal_mutual = 0.0
    withdrawal_roth = 0.0
    withdrawal_taxes = 0.0
    total_withdrawals_before_tax = 0.0
    income_needed = 0.0
    shortfall = 0.0

    if after_retirement:
        # Inflate spending in retirement.
        if age == retirement_age:
            current_spending = annual_spending_goal
        else:
            current_spending *= 1 + inflation_rate

        # Guaranteed income from pension and Social Security.
        if age >= pension_start_age:
            pension_income = monthly_pension * 12
        if age >= social_security_start_age:
            social_security_income = monthly_social_security * 12

        income_needed = current_spending
        guaranteed_income = pension_income + social_security_income
        shortfall = max(0.0, income_needed - guaranteed_income)

        # Withdraw from Traditional IRA first.
        withdrawal_traditional = min(traditional_ira, shortfall)
        traditional_ira -= withdrawal_traditional
        shortfall -= withdrawal_traditional

        # Withdraw from mutual funds next.
        withdrawal_mutual = min(mutual_fund, shortfall)
        mutual_fund -= withdrawal_mutual
        shortfall -= withdrawal_mutual

        # Withdraw from Roth IRA last.
        withdrawal_roth = min(roth_ira, shortfall)
        roth_ira -= withdrawal_roth
        shortfall -= withdrawal_roth

        total_withdrawals_before_tax = withdrawal_traditional + withdrawal_mutual + withdrawal_roth
        withdrawal_taxes = (withdrawal_traditional * traditional_ira_tax_rate) + (withdrawal_mutual * mutual_fund_tax_rate)

        if total_withdrawals_before_tax > 0 and funds_depleted_age is None:
            remaining_assets = traditional_ira + roth_ira + mutual_fund
            if remaining_assets <= 0.01:
                funds_depleted_age = age

    total_balance = traditional_ira + roth_ira + mutual_fund

    results.append({
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
    })

# Results DataFrame.
projection_df = pd.DataFrame(results)

# Find projected balance at retirement.
retirement_row = projection_df[projection_df["Age"] == retirement_age]
projected_balance_at_retirement = retirement_row["Total Balance"].iloc[0] if not retirement_row.empty else 0.0

# Show summary metrics.
st.header("Projection Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Projected balance at retirement", f"${projected_balance_at_retirement:,.2f}")
col2.metric("Life expectancy year", life_expectancy)
if funds_depleted_age is not None:
    col3.metric("Estimated funds run out at age", funds_depleted_age)
else:
    col3.metric("Estimated funds run out at age", "Not within projection")

# Show annual retirement income sources for the first few retirement years.
st.header("Retirement Income and Withdrawal Details")
retirement_income_df = projection_df[projection_df["Age"] >= retirement_age][
    ["Age", "Annual Spending Goal", "Pension Income", "Social Security Income", "Shortfall", "Withdrawn from Traditional IRA", "Withdrawn from Mutual Fund", "Withdrawn from Roth IRA", "Withdrawal Taxes"]
]
st.write("Retirement years income, shortfall, and withdrawals:")
st.dataframe(retirement_income_df.reset_index(drop=True))

# Show a line chart of total balance over time.
st.header("Portfolio Balance Over Time")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(projection_df["Age"], projection_df["Total Balance"], marker="o", linestyle="-", color="navy")
ax.set_xlabel("Age")
ax.set_ylabel("Total Portfolio Balance")
ax.set_title("Projected Total Portfolio Balance by Age")
ax.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig)

# Show the full yearly projection table.
st.header("Yearly Projection Table")
st.dataframe(projection_df)

st.markdown("---")
st.subheader("How to run this app locally")
st.markdown(
    "1. Install Streamlit with `pip install streamlit pandas matplotlib`.\n"
    "2. Open a terminal in this folder.\n"
    "3. Run `streamlit run retirement_planner_app.py`.\n"
    "4. The app will open in your browser. Adjust the inputs on the left to see updated projections."
)
