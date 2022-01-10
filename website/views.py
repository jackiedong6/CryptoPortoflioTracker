from flask import Blueprint, render_template, request, flash, jsonify, Markup,redirect, url_for
from flask_login import login_required, current_user
from .models import Asset, User
import numpy as np
from . import db
import json
import pandas as pd
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objects as go
from datetime import datetime
import string 
from sqlalchemy.sql import func

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # symbol = "LRC/USD"
    portfolio_data = pd.DataFrame(columns = ['unix', 'low', 'high', 'open', 'close', 'volume', 'date', 'vol_fiat', "Total"])
    portfolio_pie = pd.DataFrame(columns = ["Ticker", "Quantity", "Total Value"])
    # Data for overall portfolio performance
    transactions = Asset.query.filter_by(user_id=current_user.id)
    Ticker_List = db.session.query(Asset.ticker).distinct()
    Ticker_List = [value for value, in Ticker_List]
    Ticker_Dict = {}
    for transaction in transactions:
        ticker_symbol = transaction.ticker
        ticker_symbol += "/USD"
        ticker_time = transaction.date_purchased
        ticker_quantity = transaction.quantity 
        data = fetch_daily_data(ticker_symbol, ticker_time, ticker_quantity)
        # print(data)
        data1 = np.array(data.iloc[-1]['close'])
        total_spent = ticker_quantity * data1 
        db.session.query(Asset).filter(Asset.id==transaction.id).update({'total_spent':total_spent},synchronize_session=False)
        db.session.commit()
        ticker_symbol = ticker_symbol.replace("/USD","")
        data2 = np.array(data.iloc[0]['close'])
        data2 = data2.tolist()
        Ticker_Dict[ticker_symbol] = [data2]
        portfolio_data = portfolio_data.set_index('date').add(data.set_index('date'), fill_value=0).reset_index()
    Data = go.Scatter(x = portfolio_data['date'], y = portfolio_data['Total'])
    plot = go.Figure(data = Data)
    plot.update_layout(
        font_family="Courier New",
        font_color="blue",
        title_font_color="blue",
        title_text = "Portfolio History",
        title_x=0.5,
        title_y = 0.9,
        title_yanchor= 'top',
        xaxis_title="Date",
        yaxis_title="Price",
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
    )
    chart_div_string = pyo.offline.plot(plot, include_plotlyjs=True, output_type='div')
    chart = Markup(chart_div_string)
    # Pie Chart
    if len(Ticker_List) > 0: 
        for ticker in Ticker_List:
            quantity_query = db.session.query(func.sum(Asset.quantity)).filter(Asset.ticker==ticker)
            quantity_query = [value for value, in quantity_query]
            Ticker_Dict[ticker].append(quantity_query[0])
            totalSpent_query = db.session.query(func.sum(Asset.total_spent)).filter(Asset.ticker==ticker)
            totalSpent_query = [value for value, in totalSpent_query]
            Ticker_Dict[ticker].append(totalSpent_query[0])
        Ticker_df = pd.DataFrame(Ticker_Dict)
        Ticker_df = Ticker_df.T
        Ticker_df["totalValue"] = Ticker_df[0] * Ticker_df[1]
        Ticker_df.columns = ['priceToday', 'totalQuantity', 'totalSpent','totalValue']
        Ticker_df["totalProfit"] = Ticker_df["totalValue"] - Ticker_df["totalSpent"]
        Ticker_df["Color"] = np.where(Ticker_df["totalProfit"]<0, '#ff2800', '#0FFF50')
        pie_fig = go.Figure(data=[go.Pie(labels=Ticker_df.index, values=Ticker_df['totalValue'], textinfo='label+percent',
                            insidetextorientation='radial'
                            )])
        pie_fig.update_layout(
            font_family="Courier New",
            font_color="blue",
            title_font_color="blue",
            title_text = "Asset Breakdown",
            title_x=0.5,
            title_y = 0.9,
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            width=400, 
            height=400,
            modebar_remove = ['toImage', 'hoverClosestPie'],
        )
        piechart_div_string = pyo.offline.plot(pie_fig, include_plotlyjs=True, output_type='div')
        pie_chart = Markup(piechart_div_string)
        bar_fig = go.Figure(go.Bar(x = Ticker_df.index, y = Ticker_df['totalProfit'], marker_color = Ticker_df['Color']))
        bar_fig.update_layout(
            font_family="Courier New",
            font_color="blue",
            title_font_color="blue",
            title_text = "Profit/Loss",
            title_x=0.5,
            title_y = 0.9,
            yaxis_range=[-1000,1000],
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            xaxis_title="Asset",
            yaxis_title="Profit/Loss",
        )
        bargraph_div_string = pyo.offline.plot(bar_fig, include_plotlyjs=True, output_type='div')
        bargraph = Markup(bargraph_div_string)
        bool_data = True
        return render_template("index.html", bool = bool_data, user = current_user, tickers = Ticker_List, chart = chart, piechart = pie_chart, bargraph = bargraph)
    bool_data = False 
    return render_template("index.html", bool = bool_data, user = current_user, tickers = Ticker_List)


@views.route('/transactions', methods = ['GET', 'POST'])
@login_required
def transactions():
    uri = 'https://api.pro.coinbase.com/currencies'
    ticker = {}
    response = requests.get(uri).json()
    for i in range(len(response)):
        if response[i]['details']['type'] == 'crypto':
            ticker[(response[i]['id'])] = response[i]['name']
    sorted_ticker =  dict(sorted(ticker.items()))
    max_time = datetime.today().strftime('%Y-%m-%d')
    if (request.method == "POST"):
        transaction_type = request.form.get('btnradio')
        quantity = request.form.get('quantity')
        ticker = request.form.get('ticker')
        date_purchased = request.form.get('time')
        date_purchased = datetime.strptime(date_purchased, "%Y-%m-%d")
        quantity = float(quantity)
        if transaction_type == "BUY":
            new_transaction = Asset(ticker = ticker, quantity = quantity, 
                                    date_purchased = date_purchased, user_id=current_user.id, transaction_type = transaction_type, total_spent = None)
            db.session.add(new_transaction)
            db.session.commit()
            return redirect(url_for('views.transactions'))
        if transaction_type == "SELL":
            quantity_query = db.session.query(func.sum(Asset.quantity)).filter(Asset.ticker==ticker)
            quantity_query = [value for value, in quantity_query]
            if quantity <= (float)(quantity_query[0]):
                quantity = quantity * -1 
                new_transaction = Asset(ticker = ticker, quantity = quantity, 
                                        date_purchased = date_purchased, user_id=current_user.id, transaction_type = transaction_type, total_spent = None)
                db.session.add(new_transaction)
                db.session.commit()
                return redirect(url_for('views.transactions'))
            else:      
                 flash(f'You do not have enough {ticker}', category='error')
                 return redirect(url_for('views.transactions'))
    else:
        transactions = Asset.query.filter_by(user_id=current_user.id)
        return render_template('transactions.html', title='Basic Table', 
                                user = current_user, ticker = sorted_ticker, transactions = transactions, max_time = max_time)
    



def fetch_daily_data(symbol, start_date, quantity):
    pair_split = symbol.split('/')  # symbol must be in format XXX/XXX ie. BTC/EUR
    symbol = pair_split[0] + '-' + pair_split[1]
    url = f'https://api.pro.coinbase.com/products/{symbol}/candles?granularity=86400'
    response = requests.get(url)
    if response.status_code == 200:  # check to make sure the response from server is good
        data = pd.DataFrame(json.loads(response.text), columns=['unix', 'low', 'high', 'open', 'close', 'volume'])
        data['date'] = pd.to_datetime(data['unix'], unit='s')  # convert to a readable date
        data['vol_fiat'] = data['volume'] * data['close']  # multiply the BTC volume by closing price to approximate fiat volume
        # data['date'] = pd.to_datetime(data['date'],format = "%Y-%m-%d")                    
        data['date'] = pd.to_datetime(data['date'], format='%Y%m%d%H%M%S')
        data = data[data['date'] >= start_date]
        if data is None:
            print("Did not return any data from Coinbase for this symbol")
        else:
            for i in data['close']:
                i = float(i)
            data['Total'] = data['close'] * (float)(quantity)
            return data

    else:
        print("Did not receieve OK response from Coinbase API")
        return None 

