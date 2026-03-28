import streamlit as st
from pathlib import Path
import warnings
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

warnings.filterwarnings('ignore')
df = pd.read_csv(Path(__file__).parent / 'dataset.csv')

for column in df.columns:
	if pd.api.types.is_object_dtype(df[column]):
		try:
			df[column] = pd.to_datetime(df[column])
		except Exception as _:
			pass


agg = df.groupby(['day_name','time_of_day','hour_of_day','coffee_name'], as_index=False)['net_price'].sum()
fig = px.bar(
    agg,
    x='hour_of_day',
    y='net_price',
    color='coffee_name',
    facet_row='day_name',
    facet_col='time_of_day',
    category_orders={'day_name': ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
                     'time_of_day': ['Morning','Afternoon','Night'],
                     'hour_of_day': list(range(0,24))},
    labels={'net_price':'Revenue (USD)','hour_of_day':'Hour of Day'},
    title='Hourly Revenue by Coffee, Day of Week, and Time of Day (April 2024)'
)
fig.update_layout(
    legend_title_text='Coffee Product',
    height=1200,
    width=1200,
    margin=dict(l=50,r=50,t=80,b=50)
)

st.plotly_chart(fig, on_select='ignore')
