import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import statsmodels.api as sm

def app():
    st.title("Portfolio diversification")

    # Hardcoded list of stocks
    stocks1 = ["AAPL", "GOOG", "MSFT", "AMZN", "META", "JPM"]
    stocks2 = ["V", "JNJ", "WMT", "PG", "IBM", "PYPL"]

    # Get the user inputs
    stock1 = st.selectbox("Select the first stock:", stocks1)
    stock2 = st.selectbox("Select the second stock:", stocks2)
    time_period = st.selectbox("Select time period:", ["2y", "3y", "4y", "5y"])
    weight = st.slider("Weight for the first stock:", 0.0, 1.0, 0.5)

    # Get the stock data and display
    if st.button("Generate Data"):
        stock1_data = yf.download(stock1, period=time_period, interval="1d")
        stock2_data = yf.download(stock2, period=time_period, interval="1d")

        df = pd.concat([stock1_data["Adj Close"], stock2_data["Adj Close"]], axis=1)
        df.columns = [stock1, stock2]
        st.write(df)

        # Calculate the daily percentage change
        df_pct = df.pct_change().dropna() 

        # Calculate the mean, standard deviation and correlation
        mean1 = df_pct[stock1].mean() * 252
        mean2 = df_pct[stock2].mean() * 252
        std1 = df_pct[stock1].std() * np.sqrt(252)
        std2 = df_pct[stock2].std() * np.sqrt(252)
        corr = np.corrcoef(df_pct[stock1], df_pct[stock2])[0, 1]

        # Create a table to display the results
        table = pd.DataFrame({
            "Stock": [stock1, stock2],
            "Mean": [f"{mean1*100:.2f}%", f"{mean2*100:.2f}%"],
            "Standard Deviation": [f"{std1*100:.2f}%", f"{std2*100:.2f}%"]
        })

        st.write(table.to_html(index=False), unsafe_allow_html=True)
        st.write("Correlation:", corr)

        # Create dataframe with portfolio data
        portfolio_data = pd.DataFrame(columns=["Weight", "Expected Return", "Standard Deviation"])
        for w in np.arange(0, 1.01, 0.01):
            ret = w * mean1 + (1 - w) * mean2
            std = np.sqrt(w ** 2 * std1 ** 2 + (1 - w) ** 2 * std2 ** 2 + 2 * w * (1 - w) * corr * std1 * std2)
            portfolio_data = portfolio_data.append({"Weight": w, "Expected Return": ret, "Standard Deviation": std},
                                                ignore_index=True)

        new_trace = go.Scatter(
            x=[np.sqrt((weight * std1) ** 2 + ((1 - weight) * std2) **2 + 2 * weight * (1 - weight) * corr * std1 * std2 )],  # specify the x-coordinate of the new point
            y=[weight * mean1 + (1 - weight) * mean2],  # specify the y-coordinate of the new point
            mode='markers',
            name='Portfolio',
            marker=dict(
                color='red',  # set the marker color to red
                size=10  # set the marker size
            ),
            hovertemplate=f"Weight: {weight:.2%}<br>Expected Value: {weight * mean1 + (1 - weight) * mean2:.2%}<br>Standard Deviation: {np.sqrt((weight * std1) ** 2 + ((1 - weight) * std2) **2 + 2 * weight * (1 - weight) * corr * std1 * std2 ):.2%}"
        )

        # Defines stock 1 point
        trace_stock1 = go.Scatter(
            x=[std1],
            y=[mean1],  # specify the y-coordinate of the new point
            mode='markers',
            name=stock1,
            marker=dict(
                color='orange',  # set the marker color to red
                size=8  # set the marker size
            ),
            hovertemplate=f"Weight: {weight:.2%}<br>Expected Value: {mean1:.2%}<br>Standard Deviation: { std1:.2%}"
        )

        min_weight = (std2 **2 - (corr * std1 * std2))/(std1 ** 2 + std2 ** 2 - 2 * corr * std1 * std2)

        trace_min = go.Scatter(
            x=[np.sqrt((min_weight * std1) ** 2 + ((1 - min_weight) * std2) **2 + 2 * min_weight * (1 - min_weight) * corr * std1 * std2 )],  # specify the x-coordinate of the new point
            y=[min_weight * mean1 + (1 - min_weight) * mean2],  # specify the y-coordinate of the new point
            mode='markers',
            name='Minimum Variance Portfolio',
            marker=dict(
                color='green',  # set the marker color to red
                size=8  # set the marker size
            ),
            hovertemplate=f"Weight: {min_weight:.2%}<br>Expected Value: {min_weight * mean1 + (1 - min_weight) * mean2:.2%}<br>Standard Deviation: {np.sqrt((min_weight * std1) ** 2 + ((1 - min_weight) * std2) **2 + 2 * min_weight * (1 - min_weight) * corr * std1 * std2 ):.2%}"
        )

        trace_stock2 = go.Scatter(
            x=[std2],
            y=[mean2],  # specify the y-coordinate of the new point
            mode='markers',
            name=stock2,
            marker=dict(
                color='orange',  # set the marker color to red
                size=8  # set the marker size
            ),
            hovertemplate=f"Weight: {weight:.2%}<br>Expected Value: {mean2:.2%}<br>Standard Deviation: { std2:.2%}"
        )

        # Add scatter plot
        fig = px.line(portfolio_data, x='Standard Deviation', y='Expected Return', 
                    hover_data={'Weight': ':.2%', 'Expected Return': ':.2%', 'Standard Deviation': ':.2%'},
                    title='Portfolio Optimization')
        fig.add_trace(new_trace)
        fig.add_trace(trace_stock1)
        fig.add_trace(trace_stock2)
        fig.add_trace(trace_min)


        st.plotly_chart(fig)
