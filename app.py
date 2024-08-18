import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from binance.client import Client
import plotly.graph_objects as go
import datetime

# Binance API keys (substitua pelas suas chaves se necessário)
BINANCE_API_KEY = 'elKswgkiM7gXTeo0ge8BkMqJjfkeoU00Nds9outr3JkvzsUYHaXXPQAcNZYJxuNo'
BINANCE_API_SECRET = 'sSpVSdgRC1swiCmdQdYLBjdJviVrUgQB7Fy9m37tY7a56PcHgCQc7tCIKEGQbPMcY'

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
        return bbands['BBL_20_2.0'], bbands['BBM_20_2.0'], bbands['BBU_20_2.0']

# Função para gerar recomendações e marcadores de compra/venda
def generate_recommendation(data, indicator):
    buy_signals = []
    sell_signals = []

    if indicator == 'MACD':
        macd, signal = calculate_indicators(data, 'MACD')
        for i in range(1, len(macd)):
            if macd.iloc[i] > signal.iloc[i] and macd.iloc[i-1] < signal.iloc[i-1]:
                buy_signals.append((data.index[i], data['Close'].iloc[i]))
            elif macd.iloc[i] < signal.iloc[i] and macd.iloc[i-1] > signal.iloc[i-1]:
                sell_signals.append((data.index[i], data['Close'].iloc[i]))

    elif indicator == 'RSI':
        rsi = calculate_indicators(data, 'RSI')
        for i in range(len(rsi)):
            if rsi.iloc[i] < 30:
                buy_signals.append((data.index[i], data['Close'].iloc[i]))
            elif rsi.iloc[i] > 70:
                sell_signals.append((data.index[i], data['Close'].iloc[i]))

    elif indicator == 'Bollinger Bands':
        lowerband, middleband, upperband = calculate_indicators(data, 'Bollinger Bands')
        for i in range(len(data)):
            if data['Close'].iloc[i] < lowerband.iloc[i]:
                buy_signals.append((data.index[i], data['Close'].iloc[i]))
            elif data['Close'].iloc[i] > upperband.iloc[i]:
                sell_signals.append((data.index[i], data['Close'].iloc[i]))

    return buy_signals, sell_signals

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
    buy_signals, sell_signals = generate_recommendation(data, indicator)
    
    # Plotando os dados com marcadores de compra e venda
    fig = go.Figure()

    # Adiciona o gráfico de fechamento
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Preço de Fechamento'))

    # Adiciona os marcadores de compra
    if buy_signals:
        buy_dates, buy_prices = zip(*buy_signals)
        fig.add_trace(go.Scatter(x=buy_dates, y=buy_prices, mode='markers', name='Comprar', 
                                 marker=dict(color='green', size=10, symbol='circle')))

    # Adiciona os marcadores de venda
    if sell_signals:
        sell_dates, sell_prices = zip(*sell_signals)
        fig.add_trace(go.Scatter(x=sell_dates, y=sell_prices, mode='markers', name='Vender', 
                                 marker=dict(color='red', size=10, symbol='circle')))

    # Exibir o gráfico
    st.plotly_chart(fig)

    # Exibindo o preço da última análise de compra e venda
    if buy_signals:
        last_buy_date, last_buy_price = buy_signals[-1]
        st.write(f"Último preço de compra: {last_buy_price} na data {last_buy_date}")

    if sell_signals:
        last_sell_date, last_sell_price = sell_signals[-1]
        st.write(f"Último preço de venda: {last_sell_price} na data {last_sell_date}")