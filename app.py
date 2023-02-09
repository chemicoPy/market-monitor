import streamlit as st
import ccxt,pytz,time,requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import pandas_ta as ta
import plotly.graph_objects as go
import plotly.express as px
import re
import string
import os
import json
import streamlit.components.v1 as components
import io
from io import BytesIO
import math
from numpy import *
from pandas import DataFrame, Series
from numpy.random import randn
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
 

st.set_page_config(page_title='Market Monitor', page_icon="img/page_icon.png", layout='wide', initial_sidebar_state='expanded')

st.title("Market Monitor - Market Distribution, Change & Price Converter")
st.sidebar.image("https://lh6.googleusercontent.com/28Z-ruLPUFRdtMzGIOIgb0atJPNJgTtvhanzgho7cZDPrDQfyKHhL05yJXDGOd_Z9co=w2400", use_column_width=True)

st.sidebar.markdown(
            """
    ## Project Overview
    With Market Monitor, you can see and switch between trends in real-time forex market, get insights from these trends.
    Also, it can convert crypto coin price to a local currency price.
    
    Get started already!""")  

# Dropdown menus for instrument and Tframe
instrument = st.sidebar.selectbox("Select Instrument", ['BTC/USDT','BNB/USDT', 'ETH/USDT', "SOL/USDT", "DOT/USDT", "FIL/USDT",
                                                        "DOGE/USDT", "BNB/USDT", "USD/USDT", "XRP/USDT", "TRX/USDT", 
                                                        "XAU/USDT", "LTC/USDT", "SHIB/USDT", "MATIC/USDT"])

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

st.sidebar.markdown("## Conversion") # add a title to the sidebar container

to_conv = st.sidebar.selectbox(
            "Convert To",
            ("GBP (British Pound Sterling)", 
             "EUR (Euro)", "NZD (New Zealand Dollar)", "USD (United States Dollar)", "NPR (Nepalese Rupee)", "JPY (Japanese Yen)","BGN (Bulgarian Lev)","CZK (Czech Republic Koruna)","DKK (Danish Krone)","HUF (Hungarian Forint)","PLN (Polish Zloty)","RON (Romanian Leu)","SEK (Swedish Krona)", 
                                                  "CHF (Swiss Franc)","ISK (Icelandic Króna)","NOK (Norwegian Krone)","TRY (Turkish Lira)","AUD (Australian Dollar)","BRL (Brazilian Real)","CAD (Canadian Dollar)","CNY (Chinese Yuan)","HKD (Hong Kong Dollar)","IDR (Indonesian Rupiah)","ILS (Israeli New Sheqel)", "INR (Indian Rupee)","KRW (South Korean Won)","MXN (Mexican Peso)","MYR (Malaysian Ringgit)","PHP (Philippine Peso)","SGD (Singapore Dollar)", "THB (Thai Baht)", "ZAR (South African Rand)", "NGN (Nigerian Naira)"),)   

#Conversion

instrument = instrument[:instrument.index("USDT")] + '/' + instrument[instrument.index("USDT"):]

from pylivecoinwatch import LiveCoinWatchAPI

instrument_conv = instrument[:instrument.index("/")]
to_conv_2 = to_conv[:3]

res_2 = requests.get(
                "https://openexchangerates.org/api/latest.json",
                params = {
                    "app_id" : st.secrets["api_key"],
                    "symbols" : to_conv_2,
                    "show_alternatives": True
                        }
                )

rates_res_2 = res_2.json()["rates"]

lcw = LiveCoinWatchAPI()
lcw.set_api_key(st.secrets["api_key2"])

rate1 = lcw.coins_single(code=instrument_conv)["rate"]

conv_factor_1 = rate1
conv_factor_2 = rates_res_2[to_conv_2]

    
if st.sidebar.button("Show Viz!"):

  if instrument=="Select Forex Pair of interest" and Tframe=="Interval of interest":
    st.write("Kindly navigate to sidebar to see more options...")

  else:
    lim = 1000
    bybit = ccxt.bybit()
    instrument_conv = instrument[:instrument.index("/")]
    
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
  
# Converting close price to local currency here

    for i in range(0, len(df['close'])):
        df['close'][i]= float(df['close'][i]) * (conv_factor_2)
    
    for i in range(0, len(df['open'])):
        df['open'][i]= float(df['open'][i]) * (conv_factor_2)
        
    for i in range(0, len(df['high'])):
        df['high'][i]= float(df['high'][i]) * (conv_factor_2)
    
    for i in range(0, len(df['low'])):
        df['low'][i]= float(df['low'][i]) * (conv_factor_2)

# calculate RSI
    df['rsi'] = ta.rsi(df['close'])

# calculate Stochastics
    stoch_data = df.copy()

#df['stoch_k'], df['stoch_d'] = ta.stoch(df['high'], df['low'], df['close'])
#New calculation for Stochastic
    stoch_data['high'] = stoch_data['high'].rolling(14).max()
    stoch_data['low'] = stoch_data['low'].rolling(14).min()
    stoch_data['%k'] = (stoch_data["close"] - stoch_data['low'])*100/(stoch_data['high'] - stoch_data['low'])
    stoch_data['%d'] = stoch_data['%k'].rolling(3).mean()
    df['stoch_data'] = stoch_data['%d']


# Candlestick plot

    data = [go.Candlestick(x=df.index,
                       open=df.open,
                       high=df.high,
                       low=df.low,
                       close=df.close)]

    layout = go.Layout(title= f'{instrument} in {Tframe} Candlestick with Range Slider',
                   xaxis={'rangeslider':{'visible':True}})
    fig = go.Figure(data=data,layout=layout)
    plt.show()
    st.write(fig)

    
    import plotly.graph_objs as go

# create a line chart using the close data
    line = go.Scatter(
        x=df.index,
        y=df['close'],
        name='Close',
        line=dict(color='#17BECF')
)

# create the layout for the chart
    layout = go.Layout(
        title= f'{instrument} in {Tframe} Kline Data',
    xaxis=dict(
        title='Time',
        rangeslider=dict(visible=True)
    ),
    yaxis=dict(
        title='Price (USDT)'
    )
)

# create the figure and plot the chart
    fig = go.Figure(data=[line], layout=layout)
    plt.show()
    st.write(fig)

    import plotly.express as px

# create the line chart
    fig = px.line(df, x=df.index, y=df['rsi'], title=f'{instrument} in {Tframe} Kline Data')

# add the red and green lines
    fig.add_shape(
    type='line',
    x0=df.index[0],
    x1=df.index[-1],
    y0=75,
    y1=75,
    yref='y',
    line=dict(color='red', dash='dot')
)
        
    fig.add_shape(
    type='line',
    x0=df.index[0],
    x1=df.index[-1],
    y0=25,
    y1=25,
    yref='y',
    line=dict(color='green', dash='dot')
)

# set the y-axis range to include 0 and 100
    fig.update_layout(yaxis=dict(range=[0, 100]))

    plt.show()
    st.write(fig)

    st.write(df)
 

st.sidebar.markdown("## Quick Conversion") 
price = st.sidebar.number_input("Enter price to convert")
converted_price = float(price) * (conv_factor_1) * (conv_factor_2)

if st.sidebar.button("Convert"):
  st.sidebar.write("Converted Price = ", converted_price)
  




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
 
    [![Victor Ogunjobi](https://img.shields.io/badge/Author-@VictorOgunjobi-gray.svg?colorA=gray&colorB=dodgergreen&logo=github)](https://www.github.com/chemicopy)
    [![Victor Ogunjobi](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logoColor=white)](https://www.linkedin.com/in/victor-ogunjobi-a761561a5/)
    [![Victor Ogunjobi](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=gray)](https://twitter.com/chemicopy_)
    """)



   
