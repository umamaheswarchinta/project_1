# -*- coding: utf-8 -*-
# Copyright 2024-2025 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
!pip install polars
import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import polars as pl
import plotly as plt
import plotly.express as px
import matplotlib.pyplot as mtpltlb
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import date


st.set_page_config(
    page_title="Stock peer analysis dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)



df_main = pl.read_csv("my_dataset.csv")

df_main_order_date = df_main.get_column("Order Date")

df_main_division = df_main.group_by('Division').n_unique()

df_main_margin_slider_min = df_main.get_column("Gross Margin(%)").min()

df_main_margin_slider_max = df_main.get_column("Gross Margin(%)").max()

df_main_product = df_main.group_by("Product Name").n_unique()

"""
# :material/query_stats: Nassau Candy Distributor
"""

""  # Add some space.

cols = st.columns([1, 3])
# Will declare right cell later to avoid showing it when no data.



top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="top"
)

selected_product = ""

with top_left_cell:
    dates = pd.date_range(start="2023-01-01", periods=100)

    margin = 0.20 + (np.sin(np.linspace(0, 20, 100)) * 0.05) + (np.random.normal(0, 0.01, 100))
    df = pd.DataFrame({"Date": dates, "Margin": margin})

    #range_selector = st.slider("Select Date Range",value=(dates[0].date(), dates[-1].date()),
    #min_value=dates[0].date(),
    #max_value=dates[-1].date()
    #)

    selected_range = st.date_input("Select a Date Range",value=date.today())

    st.selectbox(label="Division",options=df_main_division)

    st.slider("Profit Margin", df_main_margin_slider_min, df_main_margin_slider_max)

    selected_product = st.selectbox(label="Product Name",options=df_main_product)
# Time horizon selector


right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="top",
)


Gross_profit_mean = df_main.get_column("Gross Profit").mean()

Sales_mean = df_main.get_column("Sales").mean()

units = df_main.get_column("Units").mean()

Gross_margin_in_perc = (Gross_profit_mean/Sales_mean) * 100

profit_unit = (Gross_profit_mean/units)

product_sales = df_main.group_by("Product Name").agg(pl.col("Sales").filter(pl.col("Product Name") == selected_product).sum())["Sales"].sum()

Total_sales = df_main.get_column("Sales").sum()

revenue_contribution = product_sales/Total_sales


product_profit = df_main.group_by("Product Name").agg(pl.col("Gross Profit").filter(pl.col("Product Name") == selected_product).sum())["Gross Profit"].sum()


profit_contribution = product_profit/Total_sales


margin_volatility = df_main['Gross Margin(%)'].std()



with right_cell:
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.metric("Gross Margin (%)", f"{Gross_margin_in_perc:.2f}%",border=True)

    with kpi2:
        st.metric("Profit Per Unit", f"{profit_unit:.2f}",border=True)
    
    with kpi3:
        st.metric("Revenue Contribution", f"{revenue_contribution:.2f}",border=True)

    with kpi4:
        st.metric("Profit Contribution",f"{profit_contribution:.2f}",border=True)

    with kpi5:
        st.metric("Margin Volatility",f"{margin_volatility:.2f}",border=True)





    
    




    
    tab1, tab2, tab3, tab4 = st.tabs(["Product Profitability Overview","Division Performance Dashboard","Cost vs Margin Diagnostics","Profit Concentration Analysis"])

    with tab1:
        #st.bar_chart(data=df_main,x='Product Name',y="Gross Margin(%)",sort=False,width="content")
        #st.bar_chart(data=df_main,x='Product Name',y="Gross Profit",sort=False) 
    
        chart1 = alt.Chart(df_main).mark_bar().encode(x='Product Name', y='Gross Margin(%)')
        chart2 = alt.Chart(df_main).mark_bar().encode(x='Product Name', y='Gross Profit')
        
        # Horizontal concatenation using |
        st.altair_chart(chart1 | chart2, use_container_width=True)

        
    with tab2:
        #st.line_chart(data=df_main, x="Revenue", y="Gross Profit")
        #st.line_chart(data=df_main, x="Revenue", y="Gross Margin(%)")

        chart1 = alt.Chart(df_main).mark_line().encode(x='Revenue', y='Gross Profit')
        chart2 = alt.Chart(df_main).mark_line().encode(x='Revenue', y='Gross Margin(%)')
        
        # Horizontal concatenation using |
        st.altair_chart(chart1 | chart2, use_container_width=True)



    with tab3:

        fig = px.scatter(
        df_main.to_pandas()[0:10000],
        x='Customer ID',
        y='Gross Profit',
        color_discrete_map={
            'Low': 'green',
            'Medium': 'yellow',
            'High': 'red'
        }
        )

        # 3. Render in Streamlit
        
        st.plotly_chart(fig)





    with tab4:

        def create_pareto(df, x_col, y_col):
        # Sort data for Pareto (descending)
            df = df.to_pandas().sort_values(y_col, ascending=False)
            df['cumulative_percent'] = df[y_col].cumsum() / df[y_col].sum()

            base = alt.Chart(df).encode(
                x=alt.X(f"{x_col}:N", sort="-y")
            )

            bars = base.mark_bar().encode(y=f"{y_col}:Q")
            line = base.mark_line(color='red').encode(y='cumulative_percent:Q')
            
            # Layer and resolve dual axes
            return alt.layer(bars, line).resolve_scale(y='independent').properties(width=300)

        chart1 = create_pareto(df_main, "Customer ID", "Gross Profit")
        chart2 = create_pareto(df_main, "Product Name", "Gross Profit")

        # Display them side-by-side in Streamlit
        st.altair_chart(chart1 | chart2)
