import streamlit as st
import ccxt,pytz,time,requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import pandas_ta as ta
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title='Market Breath', page_icon=':chart_with_upwards_trend:', layout='wide', initial_sidebar_state='expanded')
###------Theme




###------Theme



st.title("Market Breath - Market Distribution and Change")
st.sidebar.image("https://lh6.googleusercontent.com/28Z-ruLPUFRdtMzGIOIgb0atJPNJgTtvhanzgho7cZDPrDQfyKHhL05yJXDGOd_Z9co=w2400", use_column_width=True)
# Create dropdown menus for instrument and Tframe
instrument = st.sidebar.selectbox("Select Instrument", ['BTC/USDT','BNB/USDT', 'ETH/USDT', "SOL/USDT", "DOT/USDT", "FIL/USDT"])
Tframe = st.sidebar.selectbox("Select Time Frame", ['1m', '5m', '15m', '1h', '1d'])
percent_range = st.sidebar.slider("Percent of Closing Value", 0, 100, 95)
lim = 1000
bybit = ccxt.bybit()

# get kline data
klines = bybit.fetch_ohlcv(instrument, timeframe=Tframe, limit= lim, since=None)

# filter klines to only include data from the past month
from datetime import datetime, timedelta
one_month_ago = datetime.now() - timedelta(days=1500)
filtered_klines = [kline for kline in klines if datetime.fromtimestamp(kline[0]/1000) >= one_month_ago]

# convert the klines list to a DataFrame
df = pd.DataFrame(filtered_klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# convert the timestamp column to a datetime type
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# set the timestamp column as the index
df.set_index('timestamp', inplace=True)
df["closePercentChange"] = abs(df["close"].pct_change()*100)
df = df.drop(columns=["volume", "high", "low"])
df = df.drop(df.index[0])



maxChange = df["closePercentChange"].quantile(percent_range/100)
maxChange = round(maxChange, 2)

last_close = df["close"].iloc[-1]
last_close2 = df["close"].iloc[-2]
highest_close = df["close"].max()
lowest_close = df["close"].min()
higherBound = round(last_close + (last_close * maxChange/100),2)
lowerBound = round(last_close - (last_close * maxChange/100),2)
 


st.header(f'{instrument} - {Tframe} Metrics')

col1, col2, col3 = st.columns(3)
col1.metric("Current Value Now", last_close, delta= round(last_close - last_close2,2), delta_color = "normal")
col2.metric("Upper Bound Value", higherBound, delta= round(higherBound - last_close,2), delta_color = "normal")
col3.metric("Lower Bound Value", lowerBound, delta=  round(lowerBound - last_close,2) , delta_color = "normal")



fig = go.Figure()
fig.add_trace(go.Scatter(y=df['closePercentChange'], mode='markers'))
fig.update_layout(
    shapes=[
        # Line Horizontal
        go.layout.Shape(
            type="line",
            x0=0,
            y0=maxChange,
            x1=999,
            y1=maxChange,
            line=dict(
                color="red",
                width=3,
                dash="dot"
            )
        )
    ],
    title= f'{percent_range}% of the last {len(df)} candles closed within {maxChange}% range of previous closing price',
    yaxis_title="Value",
    xaxis_visible=False
)
st.plotly_chart(fig,use_container_width=True)

fig = px.histogram(df, x="closePercentChange", nbins=50)
st.plotly_chart(fig, use_container_width=True)

instrument = instrument.replace("/", "")
timeframe = Tframe
if "m" in timeframe:
  timeframe = timeframe.replace("m", "")
elif "h" in timeframe:
  timeframe = timeframe.replace("h", "")
  timeframe = int(timeframe) * 60
elif "d" in timeframe:
  timeframe = timeframe.replace("d", "")
  timeframe = int(timeframe) * (60*24)



chart_url = f'https://s.tradingview.com/widgetembed/?frameElementId=tradingview_8e87c&symbol=BINANCE%3A{instrument}&interval={timeframe}&hidesidetoolbar=1&saveimage=0&toolbarbg=f1f3f6&studies=&theme=Dark&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&referral_id=6310'

# display the trading chart in an iframe
st.components.v1.iframe(chart_url, width=800, height=600)


st.sidebar.markdown(

    """
    -----------
    # Other App(s):
 
    1. [Weather App](https://weather-dash.streamlit.app/)
    2. [Crypto Converter](https://crypto-conv.streamlit.app/)
    
    """)
    
    
st.sidebar.markdown(

    """
    -----------
    # Let's connect
 
    [![Segun Oladipo](https://img.shields.io/badge/Author-@SegunOladipo-gray.svg?colorA=gray&colorB=dodgergreen&logo=github)](https://github.com/SegunDave)
    [![Segun Oladipo](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logoColor=white)](https://www.linkedin.com/in/segun-oladipo-44174796/)
    [![Segun Oladipo](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=gray)](https://twitter.com/Segunoladeepo)
    """)
   
