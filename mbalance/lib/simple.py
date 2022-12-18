# -*- coding: utf8 -*-
'Модуль для хранения сессий и настроек а также чтения настроек из ini от MobileBalance'
import os, sys, locale, time, io, re, json, pickle, requests, urllib.request, configparser, pprint, zipfile, logging, traceback, collections, typing
from mbalance.lib import settings

def exception_text():
    return "".join(traceback.format_exception(*sys.exc_info())).encode('cp1251', 'ignore').decode('cp1251', 'ignore')

def IS_NEED_validate_json(data):
    'Проверяем строку на то что это валидный json'
    try:
        json.loads(data)
    except json.decoder.JSONDecodeError:
        return False  # Invalid JSON
    return True  # Valid JSON

# TODO !!! Что с этим делать ???
def feedback(msg, func, append=False):
    '''функции обратной связи, используется чтобы откуда угодно кидать сообщения
    по ходу выполнения процесса например в телегу Отправитель шлет сообщения в store.feedback.text()
    Такая замена для print'''
    try:
        if func is not None:
            # if append and self.previous != '': msg = self.previous + '\n' + msg
            func(msg)
            # self.previous = msg
        else:
            pass
            # print(msg)  # TODO можно так или в лог
    except Exception:
        # Независимо от результата мы не должны уйти в exception - это просто принт
        print('Fail feedback')

class Session():
    'Класс для сессии с дополнительными фишками для сохранения и проверки и с подтягиванием настроек'

    def __init__(self, storename=None, headers={}, options=None):
        '''если не указать storename то сессия без сохранения
        headers - если после создания сессии нужно прописать дополнительные'''
        self._session: requests.Session = None
        self.storename = storename
        self._options = {} if options is None else options
        self.storefolder = self.options('storefolder')
        self.pagecounter = 1  # Счетчик страниц для сохранения
        self.json_response = {}  # Сохраняем json ответы
        self.additional_headers = headers
        self.load_session()

    def options(self, key):
        return settings.get(key, self._options)

    def get_headers(self):
        return self._session.headers

    def update_headers(self, headers):
        self._session.headers.update(headers)

    def drop_and_create(self):
        'удаляем сессию и создаем новую'
        try:
            os.remove(os.abspath.join(self.storefolder, self.storename))
        except Exception:
            pass
        self.load_session()

    def disable_warnings(self):
        'Запретить insecure warning - приходится включать для кривых сайтов'
        requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

    def load_session(self, headers=None):
        'Загружаем сессии из файла, если файла нет, просто создаем заново, если drop=True то СТРОГО создаем заново, затем применяем хедера, прокси и пр.'
        if self.storename is None:
            self._session = requests.Session()
        else:
            try:
                with open(os.abspath.join(self.storefolder, self.storename), 'rb') as f:
                    self._session = pickle.load(f)
            except Exception:
                self._session = requests.Session()
        if self.options('node_tls_reject_unauthorized').strip() == '0':
            self._session.verify = False
        self.update_headers(self.additional_headers)
        # 'Применяем к сессии настройки'
        if self.options('requests_proxy') != '':
            if self.options('requests_proxy') != 'auto':
                proxy = urllib.request.getproxies()
                # fix для urllib urllib3 > 1.26.5
                if 'https' in proxy:
                    proxy['https'] = proxy['https'].replace('https://', 'http://')
            else:
                proxy = json.loads(self.options('requests_proxy'))
                self._session.proxies.update(proxy)

    def save_session(self):
        'Сохраняем сессию в файл'
        with open(os.abspath.join(self.storefolder, self.storename), 'wb') as f:
            pickle.dump(self._session, f)

    def save_response(self, url, response, save_text=False):
        'debug сохранение по умолчанию только response.json() или если указано отдельно сохраняем text'
        # Сохраняем по старинке в режиме DEBUG каждую страницу в один файл
        if not hasattr(response, 'content'):
            return
        if self.options('logginglevel') == 'DEBUG':
            fn = os.abspath.join(self.options('loggingfolder'), f'{self.storename}_{self.pagecounter}.html')
            open(fn, mode='wb').write(response.content)
        # Новый вариант сохранения - все json в один файл
        if str(self.options('log_responses')) == '1':
            try:
                idx = f'{url}_{self.pagecounter}'
                if save_text:
                    self.json_response[idx] = response.text
                else:
                    try:
                        self.json_response[idx] = response.json()
                    except Exception:
                        self.json_response[idx] = "It's not json"
                text = '\n\n'.join([f'{k}\n{pprint.PrettyPrinter(indent=4).pformat(v)}' for k, v in self.json_response.items()])
                open(os.abspath.join(self.options('loggingfolder'), self.storename + '.log'), 'w', encoding='utf8', errors='ignore').write(text)
            except Exception:
                pass
        self.pagecounter += 1

    def close(self):
        'Close session if opened'
        if type(self._session) == requests.Session:
            self._session.close()

    def __del__(self):
        self.close()

    def get(self, url, **kwargs) -> requests.Response:
        response: requests.Response = self._session.get(url, **kwargs)
        self.save_response(url, response)
        return response

    def post(self, url, data=None, json=None, **kwargs) -> requests.Response:
        response: requests.Response = self._session.post(url, data, json, **kwargs)
        self.save_response(url, response)
        return response

    def put(self, url, data=None, **kwargs) -> requests.Response:
        response: requests.Response = self._session.put(url, data, **kwargs)
        self.save_response(url, response)
        return response
