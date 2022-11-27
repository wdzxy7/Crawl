import re
import requests
from pandas import DataFrame
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
    remove = re.findall(pattern, str(s))
    for i in remove:
        s = s.replace(i, '')
    return s


def get_url(html):
    global detail_urls
    soup = BeautifulSoup(str(html), 'html.parser')
    urls = soup.find_all('a', {'target': '_blank'})
    for i in urls:
        if re.match(r'^2022年\d{1,2}月\d{1,2}日重庆市新冠肺炎疫情情况', i['title']):
            detail_urls.append(i['href'].replace('./', '/'))


def get_day(data):
    date = data.split('/')[2]
    date = date.split('_')[0].replace('t', '')
    return date


def add_rest(district, sign):
    global infection, asymptomatic, heal
    rest = set(keys) - set(district)
    if sign == 1:
        for i in rest:
            infection[i].append(0)
    elif sign == 2:
        for i in rest:
            asymptomatic[i].append(0)
    else:
        for i in rest:
            heal[i].append(0)


def get_data(data):
    global infection, asymptomatic, heal
    district = []
    for region in data[0]:
        try:
            loc = re.search(r'(区|县)', region).span()
        except:
            continue
        reg = region[0: loc[1]]
        number = region[loc[1]:]
        if reg in district:
            continue
        district.append(reg)
        try:
            infection[reg].append(number)
        except:
            infection[reg] = [number]
    add_rest(district, 1)

    district.clear()
    for region in data[1]:
        try:
            loc = re.search(r'(区|县)', region).span()
        except:
            continue
        reg = region[0: loc[1]]
        number = region[loc[1]:]
        if reg in district:
            continue
        district.append(reg)
        try:
            asymptomatic[reg].append(number)
        except:
            asymptomatic[reg] = [number]
    add_rest(district, 2)

    district.clear()
    for region in data[2]:
        try:
            loc = re.search(r'(区|县)', region).span()
        except:
            continue
        reg = region[0: loc[1]]
        number = region[loc[1]:]
        if reg in district:
            continue
        district.append(reg)
        try:
            heal[reg].append(number)
        except:
            heal[reg] = [number]
    add_rest(district, 3)


def main():
    global days, infection, asymptomatic, heal
    for page in range(1000):
        if page == 0:
            url = 'https://www.cq.gov.cn/zt/yqfk/yqtb/index.html'
        else:
            url = 'https://www.cq.gov.cn/zt/yqfk/yqtb/index_' + str(page) + '.html'
        print(url)
        html = get_html(url)
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except:
            break
        div = soup.find('div', {'class': 'common-list'})
        get_url(div)
        page += 1
    for back in detail_urls:
        day = get_day(back)
        days.append(day)
        url = 'https://www.cq.gov.cn/zt/yqfk/yqtb' + back
        print(url)
        infection['url'].append(url)
        asymptomatic['url'].append(url)
        heal['url'].append(url)
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', {'class': 'view TRS_UEDITOR trs_paper_default trs_web'})
        soup = BeautifulSoup(str(div), 'html.parser')
        ps = soup.find_all('p')[0: 3]
        details = []
        for p in ps:
            try:
                if '外输入确' in ps[2].contents:
                    raise Exception
                detail = re.findall(r'（(.*?)），', str(p.contents))
                detail = detail[0].replace('例', '')
                detail = detail.split('、')
                details.append(detail)
            except Exception as e:
                print(e)
                details.clear()
                details = [[], [], []]
                mess = ps[0].contents
                mess = str(mess).replace('其中，', '').replace('，', '')
                mess = mess.split('。')
                try:
                    inf_data = mess[0]
                    inf_data = re.findall(r'（(.*?)）', inf_data)[0].replace('例', '')
                    details[0] = inf_data.split('、')
                except:
                    try:
                        inf_data = mess[0]
                        print(inf_data)
                        inf_data = re.findall(r'^新增本土确诊病例\d{1,2}例(.*?)(；|现)+', inf_data)[0]
                    except:
                        inf_data = ''
                    details[0] = inf_data.split('、')

                try:
                    asy_data = mess[1]
                    asy_data = re.findall(r'（(.*?)）', asy_data)[0].replace('例', '')
                    details[1] = asy_data.split('、')
                except:
                    try:
                        asy_data = mess[1]
                        print(asy_data)
                        asy_data = re.findall(r'新增本土无症状感染者\d{1,2}例(.*?)；', asy_data)[0]
                    except:
                        asy_data = ''
                    details[1] = asy_data.split('、')

                try:
                    heal_data = mess[2]
                    heal_data = re.findall(r'（(.*?)）', heal_data)[0].replace('例', '')
                    details[2] = heal_data.split('、')
                except:
                    try:
                        heal_data = mess[2]
                        print(heal_data)
                        heal_data = re.findall(r'(解除本土无症状感染者医学观察|治愈出院本土确诊病例)\d{1,2}例(.*?)；', heal_data)[0]
                    except:
                        heal_data = ''
                    details[1] = heal_data.split('、')
                break
        get_data(details)


if __name__ == '__main__':
    keys = ['万州区', '渝北区', '黔江区', '城口县', '沙坪坝区', '渝中区', '开州区', '垫江县', '南岸区', '万盛经开区', '江北区',
            '九龙坡区', '永川区', '綦江区', '云阳县', '涪陵区', '璧山区', '武隆区', '巫山县', '巴南区', '合川区', '梁平区', '奉节县',
            '彭水县', '北碚区', '长寿区', '江津区', '潼南区', '荣昌区', '秀山县', '铜梁区', '忠县', '巫溪县', '大渡口区', '丰都县',
            '南川区', '酉阳县', '石柱县', '大足区']
    l1 = len(keys)
    infection = {'url': []}
    asymptomatic = {'url': []}
    heal = {'url': []}
    for key in keys:
        infection[key] = []
        asymptomatic[key] = []
        heal[key] = []
    days = []
    detail_urls = []
    main()
    infection_df = DataFrame(infection, index=days)
    asymptomatic_df = DataFrame(asymptomatic, index=days)
    heal_df = DataFrame(heal, index=days)
    infection_df.to_csv('infection.csv', encoding='gbk')
    asymptomatic_df.to_csv('asymptomatic.csv', encoding='gbk')
    heal_df.to_csv('heal.csv', encoding='gbk')