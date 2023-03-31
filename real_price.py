from sklearn.linear_model import LinearRegression
import pandas as pd


def get_x_y():
    btcusdt = pd.read_csv('BTCUSDT_1m_0103_3003.csv')
    ethusdt = pd.read_csv('ETHUSDT_1m_0103_3003.csv')

    btcusdt_opens = btcusdt['<OPEN>']
    ethusdt_opens = ethusdt['<OPEN>']

    x = pd.DataFrame(btcusdt_opens)
    y = pd.DataFrame(ethusdt_opens)

    return x, y


def get_coefs(x, y):
    model = LinearRegression()
    model.fit(x, y)

    regression_coef = model.coef_
    r_squared = model.score(x, y)

    return regression_coef, r_squared


x, y = get_x_y()
regression_coef, r_squared = get_coefs(x, y)

print(f'coefficient of regression: {regression_coef[0][0]:.2f}')
print(f'R-squared (determination coefficient): {r_squared:.2f}\n')

def get_real_changing_of_ethusdt(price):
    return price * (1 - r_squared)