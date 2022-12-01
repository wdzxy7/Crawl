import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests.exceptions import RequestException


def get_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def main():
    res_dict = {'day': [], 'high': [], 'low': [], 'weather': [], 'wind': []}
    for month in range(1, 12):
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        url = 'https://lishi.tianqi.com/chongqing/2022' + month + '.html'
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        uls = soup.find_all('ul', {'class': 'thrui'})
        soup = BeautifulSoup(str(uls).replace('\n', ''), 'html.parser')
        lis = soup.find_all('li')
        for i in lis:
            day = i.contents[0].string
            high = i.contents[1].string
            low = i.contents[2].string
            weather = i.contents[3].string
            wind = i.contents[4].string
            res_dict['day'].append(day)
            res_dict['high'].append(high)
            res_dict['low'].append(low)
            res_dict['weather'].append(weather)
            res_dict['wind'].append(wind)
    df = DataFrame(res_dict)
    df.to_csv('CQ_Weather.csv', index=False)


if __name__ == '__main__':
    main()