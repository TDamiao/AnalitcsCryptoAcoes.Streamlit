import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from binance.client import Client
import datetime

# Binance API keys (substitua pelas suas chaves se necessário)
BINANCE_API_KEY = 'sua_api_key_aqui'
BINANCE_API_SECRET = 'seu_api_secret_aqui'

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# Função para baixar dados de ações com yfinance
def get_stock_data(ticker):
    data = yf.download(ticker, period='1y', interval='1d')
    return data

# Função para baixar dados de criptomoedas da Binance
def get_crypto_data(symbol):
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 year ago UTC")
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                         'close_time', 'quote_asset_volume', 'number_of_trades', 
                                         'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['close'] = pd.to_numeric(data['close'])
    data['Close'] = data['close']
    data.index = pd.to_datetime(data['timestamp'], unit='ms')
    return data

# Função para calcular os indicadores usando pandas_ta
def calculate_indicators(data, indicator):
    if indicator == 'MACD':
        macd = data.ta.macd(fast=12, slow=26, signal=9)
        return macd['MACD_12_26_9'], macd['MACDs_12_26_9']
    elif indicator == 'RSI':
        rsi = data.ta.rsi(length=14)
        return rsi
    elif indicator == 'Bollinger Bands':
        bbands = data.ta.bbands(length=20)
        return bbands['BBL_20'], bbands['BBM_20'], bbands['BBU_20']

# Função para gerar recomendações
def generate_recommendation(data, indicator):
    if indicator == 'MACD':
        macd, signal = calculate_indicators(data, 'MACD')
        if macd.iloc[-1] > signal.iloc[-1]:
            return "Comprar"
        else:
            return "Vender"
    elif indicator == 'RSI':
        rsi = calculate_indicators(data, 'RSI')
        if rsi.iloc[-1] < 30:
            return "Comprar"
        elif rsi.iloc[-1] > 70:
            return "Vender"
        else:
            return "Manter"
    elif indicator == 'Bollinger Bands':
        lowerband, middleband, upperband = calculate_indicators(data, 'Bollinger Bands')
        if data['Close'].iloc[-1] < lowerband.iloc[-1]:
            return "Comprar"
        elif data['Close'].iloc[-1] > upperband.iloc[-1]:
            return "Vender"
        else:
            return "Manter"

# Interface com Streamlit
st.title("Análise de Ações e Criptomoedas com Indicadores Técnicos")

# Escolha entre ação ou criptomoeda
option = st.selectbox("Escolha o tipo de ativo", ['Ação', 'Criptomoeda'])

if option == 'Ação':
    ticker = st.text_input("Digite o ticker da ação", "AAPL")
    data = get_stock_data(ticker)
else:
    symbol = st.text_input("Digite o símbolo da criptomoeda", "BTCUSDT")
    data = get_crypto_data(symbol)

# Escolha o indicador
indicator = st.selectbox("Escolha o indicador", ['MACD', 'RSI', 'Bollinger Bands'])

if st.button("Analisar"):
    recommendation = generate_recommendation(data, indicator)
    st.write(f"Recomendação: {recommendation}")

    if indicator == 'MACD':
        macd, signal = calculate_indicators(data, 'MACD')
        st.line_chart(macd)
        st.line_chart(signal)

    elif indicator == 'RSI':
        rsi = calculate_indicators(data, 'RSI')
        st.line_chart(rsi)

    elif indicator == 'Bollinger Bands':
        lowerband, middleband, upperband = calculate_indicators(data, 'Bollinger Bands')
        st.line_chart(data['Close'])
        st.line_chart(upperband)
        st.line_chart(lowerband)