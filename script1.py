from kiteconnect import KiteConnect
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from kiteconnect import KiteConnect


# Initialise
def get_kite():
    kiteObj = KiteConnect(api_key='API_KEY')
    kiteObj.set_access_token('ACCESS_TOKEN')
    return kiteObj


kite = get_kite()
instrumentsList = None


def getCMP(tradingSymbol):
    quote = kite.quote(tradingSymbol)
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0


def get_symbols(expiry, name, strike, ins_type):
    global instrumentsList

    if instrumentsList is None:
        instrumentsList = kite.instruments('NFO')

    lst_b = [
        num for num in instrumentsList
        if num['expiry'] == expiry and num['strike'] == strike
        and num['instrument_type'] == ins_type and num['name'] == name
    ]
    return lst_b[0]['tradingsymbol']


def place_order(tradingSymbol, price, qty, direction, exchangeType, product,
                orderType):
    try:
        orderId = kite.place_order(variety=kite.VARIETY_REGULAR,
                                   exchange=exchangeType,
                                   tradingsymbol=tradingSymbol,
                                   transaction_type=direction,
                                   quantity=qty,
                                   price=price,
                                   product=product,
                                   order_type=orderType)
    except:
        print("Order placement failed")



def main_function():
    # target_price = input("Enter target price to buy again")
    atm_strike = round(getCMP('NSE:NIFTY 50'), -1)  # current priced rouned to 10
    stop_loss = atm_strike * 1.2  # stop loss 20% more of the current price
    next_thursday_expiry = datetime.today() + relativedelta(weekday=TH(1))  # gives the next expiry date

    symbol_ce = get_symbols(next_thursday_expiry.date(), 'NIFTY', atm_strike, 'CE')  # call
    symbol_pe = get_symbols(next_thursday_expiry.date(), 'NIFTY', atm_strike, 'PE')  # put

    place_order(symbol_ce, 0, 75, kite.TRANSACTION_TYPE_SELL,
                KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                KiteConnect.ORDER_TYPE_MARKET)

    place_order(symbol_pe, 0, 75, kite.TRANSACTION_TYPE_SELL,
                KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                KiteConnect.ORDER_TYPE_MARKET)

    while True:
        try:
            new_price = round(getCMP('NSE:NIFTY 50'), -1) # round off to nearest 10
        except:
            continue

        print("Combined Permium = ", new_price)

        if (new_price >= stop_loss):
            try:
                place_order(symbol_ce, 0, 75, kite.TRANSACTION_TYPE_BUY,
                            KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                            KiteConnect.ORDER_TYPE_MARKET)

                place_order(symbol_pe, 0, 75, kite.TRANSACTION_TYPE_BUY,
                            KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                            KiteConnect.ORDER_TYPE_MARKET)
            except:
                continue

            break

        # if a target price is also given
        # if(new_price <= target_price):
        #     try:
        #         place_order(symbol_ce, 0, 75, kite.TRANSACTION_TYPE_BUY,
        #                     KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
        #                     KiteConnect.ORDER_TYPE_MARKET)

        #         place_order(symbol_pe, 0, 75, kite.TRANSACTION_TYPE_BUY,
        #                     KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
        #                     KiteConnect.ORDER_TYPE_MARKET)
        #     except:
        #         continue

        #     break

        time.sleep(5)
