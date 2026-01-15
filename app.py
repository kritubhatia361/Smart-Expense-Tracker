import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------ Page Config ------------------
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")

# ------------------ Theme Toggle (Top Right) ------------------
col1, col2 = st.columns([9,1])
with col2:
    dark_mode = st.checkbox("🌗 Dark Mode", value=False)

if dark_mode:
    st.markdown(
        """
        <style>
        body {background-color: #0e1117; color: white;}
        .stTextInput>div>input, .stNumberInput>div>input {background-color: #222831; color: white;}
        .stButton>button {background-color: #222831; color: white;}
        .stDataFrame div {color: white;}
        </style>
        """, unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        body {background-color: white; color: black;}
        </style>
        """, unsafe_allow_html=True
    )

st.title("💰 Smart Expense Tracker")
st.subheader("Track. Analyze. Improve your spending habits.")

# ------------------ Auto Categorization ------------------
def auto_categorize(description):
    description = description.lower()
    category_map = {
        "Food": ["swiggy", "zomato", "restaurant", "cafe", "pizza", "burger"],
        "Transport": ["uber", "ola", "bus", "metro", "taxi"],
        "Shopping": ["amazon", "flipkart", "mall", "shopping"],
        "Entertainment": ["movie", "netflix", "spotify", "game"],
        "Bills": ["electricity", "water", "wifi", "rent", "recharge"]
    }
    for category, keywords in category_map.items():
        for word in keywords:
            if word in description:
                return category
    return "Other"

# ------------------ Data Setup ------------------
DATA_FILE = "expenses.csv"
if not pd.io.common.file_exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Description", "Category", "Amount"]).to_csv(DATA_FILE, index=False)

# ------------------ Add Expense ------------------
st.markdown("### ➕ Add New Expense")
with st.form("expense_form", clear_on_submit=True):
    date = st.date_input("Date", value=datetime.today())
    description = st.text_input("Description (e.g., Swiggy lunch)")
    auto_category = auto_categorize(description)
    category = st.selectbox(
        "Category (Auto-detected)",
        ["Food", "Transport", "Shopping", "Entertainment", "Bills", "Other"],
        index=["Food", "Transport", "Shopping", "Entertainment", "Bills", "Other"].index(auto_category)
    )
    amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
    submitted = st.form_submit_button("Add Expense")

if submitted:
    new_row = pd.DataFrame([[date, description, category, amount]], columns=["Date", "Description", "Category", "Amount"])
    new_row.to_csv(DATA_FILE, mode="a", header=False, index=False)
    st.success("Expense added successfully!")

# ------------------ Read Data ------------------
df = pd.read_csv(DATA_FILE)
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

# ------------------ Expense Records ------------------
st.markdown("### 📊 Expense Records")
if df.empty:
    st.info("No expenses added yet.")
else:
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

# ------------------ Insights & Trends ------------------
st.markdown("### 📈 Insights & Trends")
if not df.empty:
    # Total spent this month
    now = datetime.now()
    monthly_df = df[(df["Date"].dt.month == now.month) & (df["Date"].dt.year == now.year)]
    total_spent = monthly_df["Amount"].sum()
    st.write(f"💸 Total spent this month: ₹{total_spent:.2f}")

    # Category-wise spending pie chart (native Streamlit)
    category_totals = monthly_df.groupby("Category")["Amount"].sum()
    if not category_totals.empty:
        st.bar_chart(category_totals)

    # Monthly spending trend
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_trend = df.groupby('Month')["Amount"].sum()
    st.line_chart(monthly_trend)

    # Category Alerts
    st.markdown("### ⚠️ Category Alerts")
    category_budget = {
        "Food": 5000,
        "Transport": 2000,
        "Shopping": 3000,
        "Entertainment": 1500,
        "Bills": 4000,
        "Other": 1000
    }
    for cat, spent in category_totals.items():
        if cat in category_budget:
            if spent > category_budget[cat]:
                st.error(f"⚠️ Overspending in {cat}: ₹{spent:.2f} (Budget: ₹{category_budget[cat]})")
            elif spent > 0.8 * category_budget[cat]:
                st.warning(f"⚠️ You’ve used 80% of your {cat} budget: ₹{spent:.2f}")
