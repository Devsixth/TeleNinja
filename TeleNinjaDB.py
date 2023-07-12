import requests
import datetime
from sqlalchemy import update
import pandas as pd
from PIL import Image
import streamlit as st
from DBEngine import NinjaCalls, NinjaManager

today = datetime.date.today()
from datetime import datetime
import telepot

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
date = today.strftime("%d-%m-%Y")

st.sidebar.title('Navigation')
side = st.sidebar.radio('Selct:',
                        ['Home', 'Cash', 'Future', "Others", "Message"])
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["CallReco", "Alert", "TGT",
                                                    "SL", "Exit", "Text", "Image"])

stock = pd.read_csv("StockProfile.csv")
sp = [row for row in stock['Symbol']]
sp.insert(0, '<select>')


def load_image(imgf):
    img = Image.open(imgf)
    return img


def to_group(cl):
    callg = {'chat_id': chat_id_g, 'text': cl}
    requests.post(url, data=callg).json()


def to_channel(cl):
    callc = {'chat_id': chat_id_c, 'text': cl}
    requests.post(url, data=callc).json()


def updatedb(sym, newval):
    nim = NinjaManager()
    nim.get_session().execute(update(NinjaCalls).where((NinjaCalls.Symbol == sym) and
                                                       (NinjaCalls.Date == today)).values(dict(SL=newval)))
    nim.get_session().commit()
    nim.get_session().close()


def closuredb(sym, closure, exitrate):
    nim = NinjaManager()
    nim.get_session().rollback()
    if (closure == 'TGT') or (closure == 'SL'):
        nm.get_session().execute(update(NinjaCalls).where((NinjaCalls.Symbol == sym) and
                                                          (NinjaCalls.Date == today)).
                                 values(dict(Closure=closure, ExitAt=current_time)))
    else:
        nm.get_session().execute(update(NinjaCalls).where((NinjaCalls.Symbol == stk) and
                                                          (NinjaCalls.Date == today)).
                                 values(dict(Closure=closure, ExitAt=current_time, ExitRate=exitrate)))

    nm.get_session().commit()
    nm.get_session().close()


def todb(sym, mont, sigl, lp, stopl, tgt, quty, sgmnt):
    nim = NinjaManager()
    nim.get_session().rollback()

    if sgmnt == "Cash":
        sgmnt = "NSECM"
        new_txn = NinjaCalls(Symbol=sym, Segment=sgmnt, Signal=sigl,
                             Rate=lp, SL=stopl, TGT=tgt, QTY=quty,
                             Date=today, EntryAt=datetime.now().strftime("%H:%M:%S"))
        nm.get_session().add(new_txn)

    elif sgmnt == "Future":
        sgmnt = "NSEFO"
        new_txn = NinjaCalls(Symbol=sym, Segment=sgmnt, Signal=sigl,
                             Rate=lp, SL=stopl, TGT=tgt, QTY=quty, Mon=mont,
                             Date=today, EntryAt=datetime.now().strftime("%H:%M:%S"))
        nm.get_session().add(new_txn)
    elif sgmnt == "Index":
        sgmnt = "INDEX"
        new_txn = NinjaCalls(Symbol=sym, Segment=sgmnt, Signal=sigl,
                             Rate=lp, SL=stopl, TGT=tgt, QTY=quty, Mon=mont,
                             Date=today, EntryAt=datetime.now().strftime("%H:%M:%S"))
        nm.get_session().add(new_txn)
    else:
        sgmnt = "COMMODITY"
        new_txn = NinjaCalls(Symbol=sym, Segment=sgmnt, Signal=sigl,
                             Rate=lp, SL=stopl, TGT=tgt, QTY=quty, Mon=mont,
                             Date=today, EntryAt=datetime.now().strftime("%H:%M:%S"))
        nm.get_session().add(new_txn)

    nm.get_session().commit()
    nm.get_session().close()


with tab6:
    st.header("NEWS")
    news = st.text_input("Enter the News", )
    st.write(news)
    if st.button("SendNews"):
        to_channel(news)
        to_group(news)

with tab1:
    if (side == "Home") or (side == "Message"):
        st.title("Ninja - Sending Calls/News/Image to Telegram")

    if side == "Cash":
        st.header("Cash Call Recommendation")
        col1, col2 = st.columns(2)
        with col1:
            segment = "Cash"
            stk = st.selectbox("Select the StockName", sp)
            signal = st.selectbox("OrderType", ['<select>', "BUY", "SELL"], 0)
        with col2:
            lp1 = st.number_input("LimitPrice")
            sp1 = st.number_input("StopPrice")
            tgt1 = st.number_input("Target", )
            if lp1:
                qty1 = (round(100000 / lp1), 0)
                qty = qty1[0]
                call = f"{stk} \n {signal} around - {lp1}, TGT - {tgt1}, SL - {sp1}, Qty - {qty} (1 Lakh)"
                st.write(call)
        if st.button("SendCall"):
            to_group(call)
            todb(stk, 'nil', signal, lp1, sp1, tgt1, qty, segment)
            to_channel(call)
            st.write("MessageSent")

    elif side == "Future":
        st.header("Fut/Idx Call Recommendation")
        col1, col2 = st.columns(2)
        with col1:
            segment = st.selectbox("Segment", ['<select>', "Future", "Index"], 0)
            stk = st.selectbox("Enter the StockName", sp)
            mon = st.selectbox("Month", ['<select>', "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 0)
            signal = st.selectbox("OrderType", ['<select>', "BUY", "SELL"], 0)
        with col2:
            lp1 = st.number_input("Rate")
            sp1 = st.number_input("StopPrice")
            tgt1 = st.number_input("Target", )
            if stk != "<select>":
                q = stock[stock['Symbol'] == stk]['Lot'].tolist()
                lot = q[0]
                st.write("Lot - ", lot)
                call = f"{stk} \n {signal} around - {lp1}, TGT - {tgt1}, SL - {sp1}, Lot - {lot} ({mon})"
                st.write(call)
        if st.button("SendCall"):
            todb(stk, mon, signal, lp1, sp1, tgt1, lot, segment)
            to_channel(call)
            st.write("MessageSent")

    elif side == "Others":
        st.header("Commodity Call Recommendation")
        col1, col2 = st.columns(2)
        with col1:
            segment = "COMMODITY"
            stk = st.selectbox("Select the StockName", sp)
            mon = st.selectbox("Month", ['<select>', "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 0)
            signal = st.selectbox("OrderType", ['<select>', "BUY", "SELL"], 0)
        with col2:
            lp1 = st.number_input("Rate")
            sp1 = st.number_input("StopPrice")
            tgt1 = st.number_input("Target", )
            if stk != "<select>":
                q = stock[stock['Symbol'] == stk]['Lot'].tolist()
                lot = q[0]
                st.write("Lot - ", lot)
                call = f"{stk} \n {signal} around - {lp1}, TGT - {tgt1}, SL - {sp1}, Lot - {lot} "
                st.write(call)
        if st.button("SendCall"):
            todb(stk, mon, signal, lp1, sp1, tgt1, lot, segment)
            to_channel(call)
            to_group(call)
            st.write("MessageSent")

with tab2:
    nm = NinjaManager()
    q0 = nm.get_session().query(NinjaCalls)
    q = q0.where(NinjaCalls.Date == today)
    filtered = pd.read_sql(q.statement, nm.get_session().bind)
    sp = [row for row in filtered['Symbol']]
    sp.insert(0, '<select>')
    nm.get_session().close()

    if (side == "Home") or (side == "Message"):
        st.title("Ninja - Sending Calls/News/Image to Telegram")

    elif (side == "Cash") or (side == "Future") or (side == "Others"):
        st.header("Call Alert")
        col1, col2 = st.columns(2)
        with col1:
            stk = st.selectbox("ChooseStock", sp)
            if stk != '<select>':
                val = filtered.loc[filtered['Symbol'] == stk]
                t = val['TGT'].iloc[0]
                rate = val['Rate'].iloc[0]
                sig = val['Signal'].iloc[0]
                if sig == "BUY":
                    alert = round((rate + (t - rate) * 0.5), 1)
                    newsl = round((rate * (1 + 0.0027)), 1)
                else:
                    alert = round((rate - (rate - t) * 0.5), 1)
                    newsl = round((rate * (1 - 0.0027)), 1)
                call = f"ALERT {stk} is at {alert}. Move SL to {newsl}"
                st.write(call)
        if st.button("SendAlert"):
            if side == "Cash":
                updatedb(stk, newsl)
                to_channel(news)
                to_group(news)
            elif side == "Future":
                updatedb(stk, newsl)
                to_channel(news)
            else:
                updatedb(stk, newsl)
                to_channel(news)
                to_group(news)
            st.write("Message Sent")

with tab3:
    nm = NinjaManager()
    q0 = nm.get_session().query(NinjaCalls)
    q = q0.where(NinjaCalls.Date == today)
    filtered = pd.read_sql(q.statement, nm.get_session().bind)
    sp = [row for row in filtered['Symbol']]
    sp.insert(0, '<select>')
    nm.get_session().close()

    if (side == "Home") or (side == "Message"):
        st.title("Ninja - Sending Calls/News/Image to Telegram")

    elif (side == "Cash") or (side == "Future") or (side == "Others"):
        st.header("TGT Closure")
        stk = st.selectbox("Choose Stock", sp)
        if stk != '<select>':
            val = filtered.loc[filtered['Symbol'] == stk]
            t = val['TGT'].iloc[0]
            rate = val['Rate'].iloc[0]
            sig = val['Signal'].iloc[0]
            q = val['QTY'].iloc[0]
            if sig == "BUY":
                pl = round((t - rate) * q, 1)
            else:
                pl = round((rate - t) * q)
            call = f"{stk} \n TGT Achvd. Book Profits {pl}"
            st.write(call)
        if st.button("SendTGTClosure"):
            if side == "Cash":
                closuredb(stk, 'TGT', 'nil')
                to_channel(news)
                to_group(news)
            elif side == "Future":
                closuredb(stk, 'TGT', 'nil')
                to_channel(news)
            else:
                closuredb(stk, 'TGT', 'nil')
                to_channel(news)
                to_group(news)
            st.write("Message Sent")

with tab4:
    nm = NinjaManager()
    q0 = nm.get_session().query(NinjaCalls)
    q = q0.where(NinjaCalls.Date == today)
    filtered = pd.read_sql(q.statement, nm.get_session().bind)
    sp = [row for row in filtered['Symbol']]
    sp.insert(0, '<select>')
    nm.get_session().close()

    if (side == "Home") or (side == "Message"):
        st.title("Ninja - Sending Calls/News/Image to Telegram")

    elif (side == "Cash") or (side == "Future") or (side == "Others"):
        st.header("SL Closure")
        stk = st.selectbox("Stock", sp)
        if stk != '<select>':
            val = filtered.loc[filtered['Symbol'] == stk]
            s = val['SL'].iloc[0]
            rate = val['Rate'].iloc[0]
            sig = val['Signal'].iloc[0]
            q = val['QTY'].iloc[0]
            if sig == "BUY":
                pl = round((s - rate) * q, 1)
            else:
                pl = round((rate - s) * q)
            call = f"{stk} \n SL Hit. Book P/L {pl}"
            st.write(call)
        if st.button("SendSLClosure"):
            if side == "Cash":
                closuredb(stk, 'SL', 'nil')
                to_channel(news)
                to_group(news)
            elif side == "Future":
                closuredb(stk, 'SL', 'nil')
                to_channel(news)
            else:
                closuredb(stk, 'SL', 'nil')
                to_channel(news)
                to_group(news)
            st.write("Message Sent")

with tab5:
    nm = NinjaManager()
    q0 = nm.get_session().query(NinjaCalls)
    q = q0.where(NinjaCalls.Date == today)
    filtered = pd.read_sql(q.statement, nm.get_session().bind)
    sp = [row for row in filtered['Symbol']]
    sp.insert(0, '<select>')
    nm.get_session().close()

    if (side == "Home") or (side == "Message"):
        st.title("Ninja - Sending Calls/News/Image to Telegram")

    elif (side == "Cash") or (side == "Future") or (side == "Others"):
        st.header("Exit Closure")
        col1, col2 = st.columns(2)
        with col1:
            stk = st.selectbox("StockName", sp)
        with col2:
            exitval = st.number_input("EnterExitRate")
            if stk != '<select>':
                val = filtered.loc[filtered['Symbol'] == stk]
                rate = val['Rate'].iloc[0]
                sig = val['Signal'].iloc[0]
                q = val['QTY'].iloc[0]
                call = f"{stk} \n Exit at {exitval}"
                st.write(call)

        if st.button("SendExit"):
            if side == "Cash":
                closuredb(stk, 'EXIT', exitval)
                to_channel(news)
                to_group(news)
            elif side == "Future":
                closuredb(stk, 'EXIT', exitval)
                to_channel(news)
            else:
                closuredb(stk, 'EXIT', exitval)
                to_channel(news)
                to_group(news)
            st.write("Message Sent")

with tab7:
    chat_id_g = '-1001750224466'  # to the group
    chat_id_c = '-1001542839898'  # to the channel
    token = '5378660401:AAG6VvrbQY4c5Ph3dtIlRdy7E4mmcew67O8'
    st.subheader("Image")
    image_file = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"])
    if image_file is not None:
        st.image(load_image(image_file), width=250)
        path = image_file.name
        bot = telepot.Bot(token=token)
        bot.sendPhoto(chat_id=chat_id_g, photo=open(path, 'rb'))
        bot.sendPhoto(chat_id=chat_id_c, photo=open(path, 'rb'))
        st.write("Image Sent")

if __name__ == "__main__":
    url = "https://api.telegram.org/bot5378660401:AAG6VvrbQY4c5Ph3dtIlRdy7E4mmcew67O8/sendmessage"
