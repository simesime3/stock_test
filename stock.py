import streamlit as st  # フロントエンドを扱うstreamlitの機能をインポート
import pandas as pd  # データフレームを扱う機能をインポート
import yfinance as yf  # yahoo financeから株価情報を取得するための機能をインポート
import altair as alt  # チャート可視化機能をインポート

# 取得する銘柄の名前とキーを変換する一覧を設定
tickers = {
    'apple': 'AAPL',
    'facebook': 'META',
    'google': 'GOOGL',
    'microsoft': 'MSFT',
    'netflix': 'NFLX',
    'amazon': 'AMZN',
    'TOTO': '5332.T',
    'TOYOTA': '7203.T',
}

st.title('株価可視化アプリ')  # タイトル

st.sidebar.write("こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。")  # サイドバーに表示

st.sidebar.write("表示日数選択")  # サイドバーに表示

days = st.sidebar.slider('日数', 1, 3650, 30)  # 取得するための日数daysに代入

def get_period(days):
    if days <= 5:
        return '5d'
    elif days <= 30:
        return '1mo'
    elif days <= 90:
        return '3mo'
    elif days <= 180:
        return '6mo'
    elif days <= 365:
        return '1y'
    elif days <= 730:
        return '2y'
    elif days <= 1825:
        return '5y'
    elif days <= 3650:
        return '10y'
    else:
        return 'max'

# @st.cache_dataで読み込みが早くなるように処理を保持しておける
@st.cache_data
def get_data(period, tickers):
    df = pd.DataFrame()  # 株価を代入するための空箱を用意

    # 選択した株価の数だけ yf.Tickerでリクエストしてデータを取得する
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])  # 設定した銘柄一覧でリクエストの為の7203.Tなどに変換をして、それをyf.Tickerで株価リクエスト
        hist = tkr.history(period=period)  # スライドバーで指定した日数で取得した情報を絞る
        hist.index = pd.to_datetime(hist.index).strftime('%d %B %Y')  # indexを日付のフォーマットに変更
        hist = hist[['Close']]  # データを終値だけ抽出
        hist.columns = [company]  # データのカラムをyf.Tickerのリクエストした企業名に設定
        hist = hist.T  # 欲しい情報が逆なので、転置する
        hist.index.name = 'Name'  # indexの名前をNameにする
        df = pd.concat([df, hist])  # 用意した空のデータフレームに設定したhistのデータを結合する
    return df  # 返り値としてdfを返す

period = get_period(days)
df = get_data(period, tickers)

# チャートに表示する範囲をスライドで表示し、それぞれをymin, ymaxに代入
st.write("株価の範囲指定")  # サイドバーに表示
ymin, ymax = st.slider(
    '範囲を指定してください。',
    0.0, 5000.0, (0.0, 5000.0)
)  # サイドバーに表示

# 企業名の配列を生成し、companiesに代入
companies = st.multiselect(
    '会社名を選択してください。',
    list(df.index),
    ['google', 'apple', 'TOYOTA']
)

if not companies:
    st.error("少なくとも1つの会社を選択してください。")
else:
    data = df.loc[companies]  # 取得したデータから抽出するための配列で絞ってdataに代入
    data = data.T.reset_index()  # dataを抽出して転置

    # 企業ごとの別々のカラムにデータを表示する必要ないので企業を１つのカラムに統一
    data = pd.melt(data, id_vars=['Date']).rename(
        columns={'value': 'Stock Prices'}
    )

    # dataとスライドバーで設定した最大最小値を元にalt.Chartを使って株価チャートを作成
    chart = (
        alt.Chart(data)
        .mark_line(opacity=0.8, clip=True)
        .encode(
            x="Date:T",
            y=alt.Y("Stock Prices:Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
            color='Name:N'
        )
    )

    # 作成したチャートをstreamlitで表示
    st.altair_chart(chart, use_container_width=True)
