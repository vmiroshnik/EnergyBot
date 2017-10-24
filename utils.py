import datetime as dt
import csv
import re
import time

import matplotlib.pyplot as plt
import pandas as pd
import requests as rq
import bs4 as bs

import settings


def get_data_tb(today, proxies=None):
    day_index = 0 if today else 1
    base_url = r'http://data.gov.ua'
    url = base_url + r'/passport/31199018-e15e-4e87-bf5e-2a4293151f5c'
    i = 0
    while i < 3:
        res_base = rq.get(url, proxies=proxies)
        soup = bs.BeautifulSoup(res_base.text, "html.parser")
        data_tag = soup.find_all('a', href=re.compile('/file/'))[day_index]
        data_url = base_url + data_tag.get('href')
        res = rq.get(data_url, proxies=proxies)
        if res.ok:
            break
        time.sleep(5)
        i += 1
    res_str = list(csv.reader(res.content.decode('utf-8').splitlines()))
    data_tb = pd.DataFrame(res_str[1:], columns=res_str[0], dtype=int)
    return data_tb


def make_graph(total_tb, date, save=True, show=False):
    gen_tb = total_tb.loc[:, 'АЕС': 'ГАЕС(генерація)']
    cons_tb = total_tb.loc[:, 'Споживання':]

    colors = ['#662E1C',
              '#DE7A22',
              '#F9DC24',
              '#DDBC95',
              '#556DAC',
              '#43C0F6']

    fig = gen_tb.plot(kind='bar',
                      width=0.9,
                      figsize=(10, 7),
                      stacked=True,
                      align='center',
                      xlim=(-1, len(gen_tb)+2),
                      color=colors,
                      title=f"Споживання та генерація за {date}",
                      legend=False)
    cons_tb['Споживання'].plot(color='#F25C00', lw=2)

    plt.text(0, -2900, "Примітка: Споживання не включає обсяги закачки ГАЕС та міждержавні перетоки" 
             "\nДжерело даних: http://data.gov.ua/passport/31199018-e15e-4e87-bf5e-2a4293151f5c"    
             "\nАвтор: EnergyBot (@UAEnergyBot)",
             # "\nАвтор: Мірошник Володимир (miroshnyk.volodymyr@gmail.com)",
             fontsize=9)
    fig.spines['top'].set_visible(False)
    fig.spines['right'].set_visible(False)
    fig.spines['bottom'].set_visible(False)
    fig.spines['left'].set_visible(False)
    fig.yaxis.grid(lw=0.7, linestyle='--', color='black', alpha=0.5)
    fig.set_xticklabels(range(1, gen_tb.shape[0] + 1))
    plt.tick_params(axis='both', which='both', bottom='off', left='off')
    plt.legend(facecolor=None)
    plt.ylabel('Мвт')
    # Сдвиг осей что бы все столбци помещались на картинке
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - 1, x1 + 1, y0, y1))
    plt.subplots_adjust(left=0.10, right=0.95, top=0.95, bottom=0.13)
    if save:
        plt.savefig(r'gen.png', bbos_inches='tight')
    if show:
        plt.show()
    return plt


if __name__ == '__main__':
    date = dt.datetime.today()
    today = False
    proxies = settings.proxy
    date_for_graph = date.strftime('%d.%m.%Y') if today else (date - dt.timedelta(1)).strftime('%d.%m.%Y')

    data_tb = get_data_tb(today, proxies=proxies)

    make_graph(data_tb, date_for_graph, show=True)

    # data_tb = pd.read_csv(r'C:\Users\VM\Downloads\dg_10.csv')
    gen_tb = data_tb.loc[:, 'АЕС': 'ГАЕС(генерація)']
    cons_tb = data_tb.loc[:, 'Споживання':]

    gen_sum = gen_tb.sum(axis=1)

    cons_min_idx = cons_tb['Споживання'].idxmin() + 1
    cons_min = cons_tb['Споживання'].min()
    cons_max_idx = cons_tb['Споживання'].idxmax() + 1
    cons_max = cons_tb['Споживання'].max()




