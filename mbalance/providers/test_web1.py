# -*- coding: utf8 -*-
''' Автор ArtyLa '''
import os, sys, re, logging, random, time, json
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
from http import cookies
import time, logging, sys, traceback, threading, socket
from mbalance.lib import simple, settings, browser

PORT = 8083

pages = {
    '/login.html': '''<!DOCTYPE html>
        <html>
        <head>
            <title>Login form sample</title>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style></style>
        </head>
        <body>
            <script></script>
            <form class="login" action="/lk.html" method="POST">
                <label for="uname"><b>Username</b></label><input type="text" placeholder="Enter Username" name="uname" required><br>
                <label for="psw"><b>Password</b></label><input type="password" placeholder="Enter Password" name="psw" required><br>
                <input type="checkbox" checked="checked" name="remember"> Remember me<br>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>''',
    '/lk.html': '''<!DOCTYPE html>
        <html>
        <head>
            <title>Personal account</title>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style></style>
        </head>
        <body>
            <script>
                function loadJSON(callback) {
                    var xobj = new XMLHttpRequest();
                    xobj.overrideMimeType("application/json");
                    xobj.open('POST', 'data.json', true);
                    xobj.onreadystatechange = function () {
                        if (xobj.readyState == 4 && xobj.status == "200") {callback(xobj.responseText);}
                    };
                    xobj.send(null);
                }
                function after_load(text){
                    data = JSON.parse(text);
                    content = document.getElementById("content");
                    app = (el) => content.appendChild(el);
                    br = () => document.createElement("br");
                    tx = (el) => document.createTextNode(el);
                    if(Object.keys(data).length === 0){
                        app(tx("Unauthorized access"));
                        return
                    }
                    Object.entries(data.data.user).forEach(el=> {app(tx(el[0]));app(tx(" "));app(tx(el[1]));app(br())})
                }
                loadJSON(after_load)
            </script>
            <div id="content">
        </body>
        </html>''',
    '/data.json': {'data': {'user': {
        'Balance': 124.45 + random.randint(1, 5),  # double
        'Balance2': 22,  # double
        'Balance3': 33,  # double
        'LicSchet': 'Лицевой счет',
        'UserName': 'ФИО',
        'TarifPlan': 'Тарифный план',
        'BlockStatus': 'Статус блокировки',
        'AnyString': 'Любая строка',
        'SpendBalance': 12,  # double Потрачено средств
        'KreditLimit': 23,  # double Кредитный лимит
        'Currenc': 'Валюта',
        'Average': 5,  # double Средний расход в день
        'TurnOff': 20,  # дней до отключения
        'TurnOffStr': 'Ожидаемая дата отключения',
        'Recomend': 54,  # double Рекомендовано оплатить
        'SMS': 43,  # !!! integer Кол-во оставшихся/потраченных СМС
        'Min': 222,  # !!! integer Кол-во оставшихся минут
        'SpendMin': 32,  # double Кол-во потраченных минут (с секундами)
        # BalExpired->BeeExpired, Expired->BeeExpired
        'Expired': 'Дата истечения баланса/платежа',
        'ObPlat': 14,  # double Сумма обещанного платежа
        'Internet': 1234.45,  # double Кол-во оставшегося/потраченного трафика
        # 'ErrorMsg':	'Сообщение об ошибке', # Если оно есть в Response то это ошибка
        'UslugiOn': '2/8',
        # Это будет показано в hover, если включено
        'UslugiList': 'Услуга1\t10р\nУслуга2\t20р\nУслуга3\t30р\nУслуга4\t40р'
    }}}
}

class dummywebserver():
    # A relatively simple WSGI application. It's going to print out the
    # environment dictionary after being updated by setup_testing_defaults
    def __init__(self, host='', port=PORT):
        self.host, self.port = host, port

    def simple_app(self, environ, start_response):
        setup_testing_defaults(environ)
        logging.info(f"{environ['PATH_INFO']}")
        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        pg = environ['PATH_INFO']
        if pg == '/favicon.ico':
            headers = [('Content-type', 'image/x-icon')]
            res = [b'\x00\x00\x01\x00\x01\x00\x01\x02\x00\x00\x01\x00\x18\x008\x00\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00']
        elif pg in pages:
            if type(pages[pg]) is dict:
                cs = cookies.SimpleCookie(environ['HTTP_COOKIE'])
                headers = [('Content-type', 'application/json')]
                if 'TOKEN' in cs and cs.get('TOKEN').value == '123456':
                    res = [json.dumps(pages[pg], ensure_ascii=False).encode('utf8')]
                else:
                    res = ['{}']
            else:
                headers = [('Content-type', 'text/html')]
                res = [pages[pg].encode('utf8')]
        else:
            res = [f'hello {time.asctime()}']
        if pg == '/lk.html':
            if environ['REQUEST_METHOD'] == 'POST':
                headers.append(('Set-Cookie', "TOKEN=123456; SameSite=Strict"))
            else:
                headers.append(('Set-Cookie', "TOKEN=; SameSite=Strict; expires=0"))
        start_response(status, headers)
        return [line.encode('utf8') if type(line) == str else line for line in res]

    def run_server(self):
        with socket.socket() as sock:
            sock.settimeout(0.2)  # this prevents a 2 second lag when starting the server
            if sock.connect_ex((self.host, self.port)) == 0:
                logging.error(f"Port {self.host}:{self.port} already in use.")
                return
        with make_server(self.host, self.port, self.simple_app) as self.httpd:
            # httpd = make_server(self.host, self.port, self.simple_app)
            logging.info(f'Serving on port {self.host}:{self.port}...')
            self.httpd.serve_forever()

    def thread_run_server(self):
        self.webserver_thread = threading.Thread(target=self.run_server)
        self.webserver_thread.daemon = True
        self.webserver_thread.start()
        time.sleep(0.1)

    def stop_server(self):
        logging.info(f"httpd.shutdown")
        self.httpd.shutdown()


login_url = 'http://localhost:8083/login.html'
user_selectors = {'chk_lk_page_js': "document.querySelector('form input[type=password]') == null",
                  'chk_login_page_js': "document.querySelector('form input[type=password]') !== null",
                  'login_clear_js': "document.querySelector('form input[type=text]').value=''",
                  'login_selector': 'form input[type=text]', }


class browserengine(browser.BrowserController):
    def data_collector(self):
        self.do_logon(url=login_url, user_selectors=user_selectors)
        # Здесь мы берем данные непосредственно с отрендеренной страницы, поэтому url_tag не указан
        self.wait_params(params=[
            {'name': 'Balance', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Balance"},
            {'name': 'Balance2', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Balance2"},
            {'name': 'Balance3', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Balance3"},
            {'name': 'LicSchet', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.LicSchet"},
            {'name': 'UserName', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.UserName"},
            {'name': 'TarifPlan', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.TarifPlan"},
            {'name': 'BlockStatus', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.BlockStatus"},
            {'name': 'AnyString', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.AnyString"},
            {'name': 'SpendBalance', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.SpendBalance"},
            {'name': 'KreditLimit', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.KreditLimit"},
            {'name': 'Currenc', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Currenc"},
            {'name': 'Average', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Average"},
            {'name': 'TurnOff', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.TurnOff"},
            {'name': 'TurnOffStr', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.TurnOffStr"},
            {'name': 'Recomend', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Recomend"},
            {'name': 'SMS', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.SMS"},
            {'name': 'Min', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Min"},
            {'name': 'SpendMin', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.SpendMin"},
            {'name': 'Expired', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Expired"},
            {'name': 'ObPlat', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.ObPlat"},
            {'name': 'Internet', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.Internet"},
            {'name': 'UslugiOn', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.UslugiOn"},
            {'name': 'UslugiList', 'url_tag': ['/data.json$'], 'jsformula': "data.data.user.UslugiList"},
        ])


def get_balance(login, password, storename=None, **kwargs):
    ''' На вход логин и пароль, на выходе словарь с результатами '''
    return browser.browserengine(login, password, storename, plugin_name=__name__).main()

def get_balance(login, password, storename=None, **kwargs):
    ''' На вход логин и пароль, на выходе словарь с результатами '''
    web = dummywebserver(host='', port=PORT)
    web.thread_run_server()  # run thread web
    result = browserengine(login, password, storename, options=kwargs, plugin_name=__name__).main()
    web.stop_server()
    logging.info('End')
    return result


if __name__ == '__main__':
    print('This is module test_web')
