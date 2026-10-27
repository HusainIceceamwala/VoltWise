import pandas as pd
import plotly.express as px


columns = [
    "ID",
    "Consumer Number",
    "Bill Date",
    "Units",
    "Amount",
    "AI Recommendation"
]


def prepare_dataframe(rows):

    if not rows:
        return None

    df = pd.DataFrame(rows, columns=columns)

    df["Units"] = pd.to_numeric(df["Units"], errors="coerce")

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    return df


# -----------------------------------
# Bill Amount Chart
# -----------------------------------

def bill_amount_chart(rows):

    df = prepare_dataframe(rows)

    if df is None:
        return None

    fig = px.bar(
        df,
        x="Bill Date",
        y="Amount",
        text="Amount",
        title="Monthly Electricity Bill"
    )

    fig.update_layout(
        xaxis_title="Bill Date",
        yaxis_title="Amount (₹)"
    )

    return fig


# -----------------------------------
# Units Chart
# -----------------------------------

def unit_chart(rows):

    df = prepare_dataframe(rows)

    if df is None:
        return None

    fig = px.line(
        df,
        x="Bill Date",
        y="Units",
        markers=True,
        title="Units Consumed Trend"
    )

    fig.update_layout(
        xaxis_title="Bill Date",
        yaxis_title="Units"
    )

    return fig


# -----------------------------------
# Pie Chart
# -----------------------------------

def consumption_pie(rows):

    df = prepare_dataframe(rows)

    if df is None:
        return None

    fig = px.pie(
        df,
        values="Units",
        names="Bill Date",
        title="Electricity Consumption Distribution"
    )

    return fig