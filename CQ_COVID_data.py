import re
import time
import requests
from bs4 import BeautifulSoup
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


def deal(s):
    pattern = re.compile(r'<[^>]*>')
    remove = re.findall(pattern, s)
    for i in remove:
        s = s.replace(i, '')
    return s


if __name__ == '__main__':
    url = 'https://www.cq.gov.cn/zt/yqfk/yqtb/index.html'
    for i in range(1000):
        if i == 0:
            url = 'https://www.cq.gov.cn/zt/yqfk/yqtb/index.html'
        else:
            url = 'https://www.cq.gov.cn/zt/yqfk/yqtb/index_' + str(i) + '.html'
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', {'class': 'common-list'})
        print(div)
        break