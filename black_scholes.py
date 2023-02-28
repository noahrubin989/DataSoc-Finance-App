import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import norm


def black_scholes(S: float, K: float, r: float, T: int, sigma: float, option_type: str='call'):
    d1 = (np.log(S/K) + T*(r + np.square(sigma)/2)) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call': 
        price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    elif option_type == 'put': 
        price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
    else:
        raise Exception("Please enter `Call` or `Put`!")
    return price


def plot_black_scholes(S_array, K: float, r: float, T: int, sigma: float, option_type: str='call'):
    y = black_scholes(S_array, K, r, T, sigma, option_type=option_type)
    ds = pd.DataFrame({'Stock Prices': S_array, f'{option_type.title()} Option Price': y})
    fig = px.line(ds, x="Stock Prices", y=f'{option_type.title()} Option Price', title=f'{option_type.title()} Option Price vs Stock Price')
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    return fig
          

def app():
    try: 
        st.write('This is the `Black Scholes Page` of this multi-page app.')
        S = st.number_input('Stock Price')
        K = st.number_input('Strike price')
        r_pct = st.number_input('Risk free interest rate (%)')
        
        r = r_pct / 100
        T = st.number_input('Time to expiration', min_value=1, step=1)
        
        sigma_pct = st.number_input('Volatility (%)', min_value=0.01)
        sigma = sigma_pct / 100.00
        chosen_option = st.radio(label='Select Option Type', options=['Call', 'Put'])
        chosen_option = chosen_option.lower()  # Preprocessing on my end
        if chosen_option:
            price = black_scholes(S, K, r, T, sigma_pct/100, option_type=chosen_option)
            st.write(price)
    except ZeroDivisionError:
        st.write("Please ensure that sigma is non-zero")
    
    # If plot then ask for min and max value, then use np.linspace(min_value, max_value, 1000)
    S_array = np.linspace(0.1, 500, 1000)
    st.plotly_chart(plot_black_scholes(S_array, K, r, T, sigma, chosen_option))