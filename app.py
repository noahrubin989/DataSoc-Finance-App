import streamlit as st
import statsmodels.api as sm
from multiapp import MultiApp
from apps import (Hedging, MinVar)

app = MultiApp()

st.markdown("""
            # Finance App
            
            ### Created By: DataSoc Education Portfolio
            
            📊 [LinkedIn](https://www.linkedin.com/company/datasoc/)  

            """)

# Add all your applications here
app.add_app("Hedging", Hedging.app)
app.add_app("Minimum Variance", MinVar.app)

# The main app
app.run()