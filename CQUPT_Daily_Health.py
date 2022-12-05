import os
import pickle
import time
import requests
from lxml import etree


proxies={
'http': 'http://127.0.0.1:7890',
'https': 'http://127.0.0.1:7890'  # https -> http
}


class CasService:
    def __init__(self, svr_session, user_name, password):
        self.svr_session = svr_session
        self.data = {
            "username": user_name,
            "password": password,
            'cas_url': 'https://ids.cqupt.edu.cn/authserver/login?service=http%3A%2F%2Fehall.cqupt.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.cqupt.edu.cn%2Fnew%2Findex.html',
            # 'cas_url': 'https://ids.cqupt.edu.cn/authserver/login?service=https%3A%2F%2Fresource.cqupt.edu.cn%2Frump_frontend%2FloginFromCas%2F'
        }
        self.session = requests.session()

    def login(self):
        service_url = "http://ehall.cqupt.edu.cn/publicapp/sys/cyxsjkdkmobile/*default/index.html"
        response = self.svr_session.get(url=service_url, allow_redirects=False, proxies=proxies)
        if response.status_code == 200:
            self.send_daka_post()
            return True
        response = self.session.get(self.data['cas_url'], allow_redirects=False, proxies=proxies)
        if response.status_code == 200:
            user_form = self.get_execution(response)
            response = self.session.post(self.data['cas_url'], data=user_form, allow_redirects=False, proxies=proxies)
            if response.status_code == 302:
                url_with_ticket = response.headers["location"]
                confirm_response = self.svr_session.get(url=url_with_ticket, allow_redirects=True)
                if confirm_response.status_code == 200:
                    print("logon on success")
                    self.write_cascookies_to_file()
                    self.send_daka_post()
                    return True
                else:
                    print("logon on failed")
            else:
                print('auth failed')
                return False
        else:
            print("cas cookies still valid")
            url_with_ticket = response.headers["location"]
            confirm_response = self.svr_session.get(url=url_with_ticket, allow_redirects = True)
            if confirm_response.status_code == 200:
                print("nopassword login success")
                self.send_daka_post()

                return True
            else:
                print("cas url_with_ticket error")
                os.remove("cas_cookies.dat")
                return False

    def get_execution(self, response):
        user_form = {
            'username': self.data['username'],
            'password': self.data['password'],
            'lt': '',
            'execution': '',
            'dllt': 'generalLogin',
            'cllt': 'userNameLogin',
            '_eventId': 'submit',
        }
        login_html = etree.HTML(response.text)
        execution_value = login_html.xpath("//form[@id='qrLoginForm']/input[@name='execution']/@value")
        user_form['execution'] = execution_value[0]
        lt_value = login_html.xpath("//form[@id='qrLoginForm']/input[@name='lt']/@value")
        user_form['lt'] = lt_value[0]
        return user_form

    def load_cascookies_from_file(self):
        if os.path.exists("cas_cookies.dat"):
            with open("cas_cookies.dat", 'rb') as f:
                self.session.cookies.update(pickle.load(f))

    def write_cascookies_to_file(self):
        with open("cas_cookies.dat",'wb') as f:
            pickle.dump(self.session.cookies,f)

    def send_daka_post(self):
        url = 'http://ehall.cqupt.edu.cn/publicapp/sys/cyxsjkdk/modules/yddjk/T_XSJKDK_XSTBXX_SAVE.do'
        data = {
            'XH': '',
            'XM': '',
            'MQJZD': '重庆市,重庆市,',
            'JZDXXDZ': '',
            'SFXN': '是',
            'JZDYQFXDJ': '其他',
            'SFYZGFXDQLJS': '无',
            'SFJCZGFXDQLJSRY': '无',
            'SZDJSSFYYQFS': '否',
            'JZDSFFXQHLSGKQY': '否',
            'TWSFZC': '是',
            'SFYGRZZ': '无',
            'TZRYSFYC': '否',
            'YKMYS': '绿色',
            'QTSM': '',
            'DKSJ': '',
            'LONGITUDE': '',
            'LATITUDE': '',
            'RQ': '',
            'SFYC': '否',
            'LOCATIONBIG': '',
            'LOCATIONSMALL': '',
            'SFTS': '',
            'SFTQX': '',
            'SFDK': '是',
            'WID': '',

        }
        self.svr_session.get("http://ehall.cqupt.edu.cn/publicapp/sys/funauthapp/api/getAppConfig/cyxsjkdkmobile-6578524306216816.do?GNFW=MOBILE")
        data['WID'] = 'EEF20FBE9248D7D9E053B02BCACA4E6A'
        data['RQ'] = time.strftime("%Y-%m-%d", time.localtime())
        data['DKSJ'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        daka_response = self.svr_session.post(url, data=data, proxies=proxies)
        if daka_response.status_code == 200:
            print(daka_response.text)
            print("打卡post已发出")
        check_body = {
            "SFDK": "是",
            "pageNumber": 1,
            "pageSize": 7,
            "TYRZM": ,
            "*order": "-DKSJ"
        }
        datas = self.svr_session.post(
            "http://ehall.cqupt.edu.cn/publicapp/sys/cyxsjkdk/modules/yddjk/T_XSJKDK_XSTBXX_QUERY.do",
            data=check_body).json()
        rows = datas['datas']['T_XSJKDK_XSTBXX_QUERY']['rows']
        print("检查")
        print("------------------------")
        for row in rows:
            print(row['RQ'], row['SFDK'])


user = ''
password = ''

auth_session = requests.session()
testCas = CasService(auth_session, user, password)
testCas.login()