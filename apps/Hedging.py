import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px


def app():
    st.title("Hedging with Stocks")

    ticker_symbols1 = ["AAPL", "GOOG", "MSFT", "AMZN", "META", "JPM", "V", "JNJ", "WMT", "PG"]
    ticker_symbols2 = ["NSRGY", "KO", "PEP", "COST", "PG"]

    base_symbol = st.selectbox("Select the base stock symbol", ticker_symbols1)
    hedging_symbol = st.selectbox("Select the hedging stock symbol", ticker_symbols2)
    selected_symbols = [base_symbol, hedging_symbol]
    start_date = st.date_input("Select start date", value=pd.to_datetime("2021-01-01"))
    end_date = st.date_input("Select end date", value=pd.to_datetime("2021-12-31"))

    if st.button("Generate Plot"):
        data = yf.download(selected_symbols, start=start_date, end=end_date)["Adj Close"]
        data_diff = data.diff().dropna()
        if base_symbol == hedging_symbol:
            correlation = 1
        else:
            correlation = data_diff.corr().iloc[0, 1]
        stddev_base = data_diff[base_symbol].std()
        stddev_hedging = data_diff[hedging_symbol].std()
        optimal_no = stddev_base / stddev_hedging * correlation

        st.write("Selected stocks price")
        st.line_chart(data)

        st.write(f"Standard deviation of daily change for {base_symbol}: {stddev_base:.4f}")
        st.write(f"Standard deviation of daily change for {hedging_symbol}: {stddev_hedging:.4f}")

        prices_df = pd.DataFrame({
            base_symbol: data_diff[base_symbol],
            hedging_symbol: data_diff[hedging_symbol]
        })

        st.write(f"Correlation between {base_symbol} and {hedging_symbol}:")
        st.write(correlation)

        fig = px.scatter(prices_df, x=base_symbol, y=hedging_symbol, trendline="ols", trendline_color_override='red')
        st.plotly_chart(fig)

        st.set_option('deprecation.showPyplotGlobalUse', False)

        st.write(f"Optimal no. stocks in {hedging_symbol} to hedge: {optimal_no:.2f}")

        hedging_price = optimal_no * data[hedging_symbol]
        hedged_price = data[base_symbol] - hedging_price
        hedged_data_pct = hedged_price.pct_change().dropna()


        st.line_chart(pd.DataFrame({base_symbol: data_diff[base_symbol], "Hedged Price": hedged_price.diff()}))
