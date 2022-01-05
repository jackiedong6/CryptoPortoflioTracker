from flask import Blueprint, render_template, request, flash, jsonify, Markup
from flask_login import login_required, current_user
from .models import Asset, User
from . import db
import json
import pandas as pd
import requests
import plotnine 
from plotnine import ggplot, aes, geom_line, geom_point, labs, scale_x_date,theme, element_text, ggtitle
from plotly.tools import mpl_to_plotly as ggplotly
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.offline as pyo
import datetime
import plotly.graph_objects as go


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    symbol = "LRC/USD"
    plot = fetch_daily_data(symbol)
    return render_template("index.html", user = current_user, chart = plot)


@views.route('/transactions', methods = ['GET', 'POST'])
@login_required
def transactions():

    # new_transaction = Asset(ticker = ticker, asset_type = asset_type, quantity = quantity, date_purchased = date_purchased, user_id=current_user.id)
    # db.session.add(new_transaction)
    # db.session.commit()
    
    users = User.query
    return render_template('transactions.html', title='Basic Table', users=users, user = current_user)
    



def fetch_daily_data(symbol):
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
        print(data['date']) 
        # print(data[data['date'] > '2021-12-20'])
        if data is None:
            print("Did not return any data from Coinbase for this symbol")
        else:
            # [data['date'] > '2021-11-20']
            data = go.Scatter(x=data['date'], y=data['close'])
            plot = go.Figure(data = data)
            plot.update_layout(
                font_family="Courier New",
                font_color="blue",
                # title_font_family="Times New Roman",
                title_font_color="blue",
                title_text = f"Price History for {symbol}",
                title_x=0.5,
                title_y = 0.9,
                title_yanchor= 'top',
                xaxis_title="Time",
                yaxis_title="Price History",
            )
            chart_div_string = pyo.offline.plot(plot, include_plotlyjs=True, output_type='div')
            chart_div_for_use_in_jinja_template = Markup(chart_div_string)
            return chart_div_for_use_in_jinja_template
    else:
        print("Did not receieve OK response from Coinbase API")
        return None 

