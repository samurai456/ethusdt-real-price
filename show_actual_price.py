import websocket
websocket.enableTrace(False)
import json
import datetime
from real_price import get_real_changing_of_ethusdt


class ShowActualPrice:
    def __init__(self, callback):
        def on_error(ws, error): print(error)
        def on_close(ws): print('### closed ###')
        def on_open(ws): ws.send('{"type":"subscribe","symbol":"BINANCE:ETHUSDT"}')

        self.callback = callback
        self.ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=c3k8j9qad3i8d96ruceg",
                              on_message = self.message_recv,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)

        self.last60lows = []
        self.lowest_in_last60lows = None
        self.last60highs = []
        self.highest_in_last60highs = None
        self.current_minute = 0

        self.previous_price = None
        self.current_real_price = None
        

    def message_recv(self, ws, message):
        response = json.loads(message)
        data = response.get('data')
        if not data: return
        self.main(data)


    def main(self, data):
        last_price = data[-1]['p']
        last_time = data[-1]['t']

        if not self.previous_price:
            self.previous_price = last_price
            self.current_real_price = last_price

        distinction = last_price - self.previous_price
        real_changing = self.callback(distinction)
        self.current_real_price += real_changing

        self.previous_price = last_price
        self.print_real_price_and_changing(real_changing, last_time, last_price, distinction)
        self.warn_if_price_changed_by_1percent(last_time)
    

    def print_real_price_and_changing(self, real_changing, last_time, last_price, distinction):
        time_ = datetime.datetime.fromtimestamp(last_time // 1000)
        sign = '' if real_changing < 0 else '+'
        signX = '' if distinction < 0 else '+'
        print(f'\r[{time_}] {self.current_real_price:0.2f} [{sign}{real_changing:.4f}]\t\tmarket price: {last_price} [{signX}{distinction:.4f}]\t', end = '')


    def warn_if_price_changed_by_1percent(self, last_time):
        last_minute = last_time // 1000 // 60
        self.edit_last60(last_minute)
        self.check_if_price_grew_fell_1percent()


    def edit_last60(self, last_minute):
        price = self.current_real_price

        if not self.lowest_in_last60lows and self.lowest_in_last60lows != 0:
            self.lowest_in_last60lows = price
            self.highest_in_last60highs = price

        if self.current_minute < last_minute:
            self.current_minute = last_minute
            self.last60lows.append(price)
            self.last60highs.append(price)

        if price < self.last60lows[-1]: self.last60lows[-1] = price
        if price > self.last60highs[-1]: self.last60highs[-1] = price

        if len(self.last60lows) > 60: 
            self.last60lows.pop(0)
            self.last60highs.pop(0)
            self.reset_highest_and_lowest_of_last60()       #ocures only if self.highest_in_last60highs or self.lowest_in_last60lows was poped

        if self.last60lows[-1] < self.lowest_in_last60lows:
            self.lowest_in_last60lows = self.last60lows[-1]

        if self.last60highs[-1] > self.highest_in_last60highs:
            self.highest_in_last60highs = self.last60highs[-1]


    def reset_highest_and_lowest_of_last60(self):

        if not self.highest_in_last60highs in self.last60highs:
            self.highest_in_last60highs = self.last60highs[-1]
            for x in self.last60highs:
                if x > self.highest_in_last60highs: self.highest_in_last60highs = x

        if not self.lowest_in_last60lows in self.last60lows:
            self.lowest_in_last60lows = self.last60lows[-1]
            for x in self.last60lows:
                if x < self.lowest_in_last60lows: self.lowest_in_last60lows = x


    def check_if_price_grew_fell_1percent(self):
        if self.current_real_price >= self.lowest_in_last60lows * 1.01:
            print('#### price has GROWN by 1% within 60 minutes ####')

        if self.current_real_price <= self.highest_in_last60highs * 0.99:
            print('#### price has FALLEN by 1% within 60 minutes ####')

        
    def run(self):
        self.ws.run_forever()


show_price = ShowActualPrice(get_real_changing_of_ethusdt)
show_price.run()


