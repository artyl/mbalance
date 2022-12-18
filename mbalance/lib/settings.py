# -*- coding: utf8 -*-
''' Файл с общими установками, распространяется с дистрибутивом
Значения по умолчанию, здесь ничего не меняем, если хотим поменять меняем в mbplugin.ini
подробное описание см в readme.md
'''
import os, re, tempfile

UNIT = {'TB': 1073741824, 'ТБ': 1073741824, 'TByte': 1073741824, 'TBYTE': 1073741824,
        'GB': 1048576, 'ГБ': 1048576, 'GByte': 1048576, 'GBYTE': 1048576,
        'MB': 1024, 'МБ': 1024, 'MByte': 1024, 'MBYTE': 1024,
        'KB': 1, 'КБ': 1, 'KByte': 1, 'KBYTE': 1,
        'DAY': 30, 'DAYLY': 30, 'MONTH': 1,
        'day': 30, 'dayly': 30, 'month': 1,
        }


DEFAULTS = {
    # папка для логов
    'loggingfolder_': {'descr': 'папка для логов', 'type': 'text', 'validate': lambda i: os.path.isdir(i)},
    'loggingfolder': os.path.join(tempfile.gettempdir(), 'mblog'),
    # Папка для хранения сессий
    'storefolder_': {'descr': 'Папка для хранения сессий', 'type': 'text', 'validate': lambda i: os.path.isdir(i)},
    'storefolder': os.path.join(tempfile.gettempdir(), 'mbstore'),
    # Прокси сервер для работы хром плагинов http://user:pass@12.23.34.56:6789 для socks5 пишем socks5://...
    'browser_proxy_': {'descr': 'Прокси сервер для работы хром плагинов http://user:pass@12.23.34.56:6789 для socks5 пишем socks5://...', 'type': 'text'},
    'browser_proxy': '',
    # Прокси сервер для работы обычных плагинов http://user:pass@12.23.34.56:6789 для socks5 пишем socks5://...
    'requests_proxy_': {'descr': '''Прокси сервер для работы обычных плагинов либо пусто тогда пытается работать как есть, либо auto, тогда пытается подтянуть системные(срабатывает не всегда), либо в формате json {"http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080"}''', 'type': 'text'},
    'requests_proxy': '',
    # показывать окно chrome если на странице найдена капча
    'show_captcha_': {'descr': 'Показывать окно chrome если на странице найдена капча', 'type': 'checkbox'},
    'show_captcha': '0',
    # максимальное время ожидания ввода капчи в секундах
    'max_wait_captcha_': {'descr': 'Максимальное время ожидания ввода капчи в секундах', 'type': 'text', 'validate': lambda i: i.isdigit()},
    'max_wait_captcha': '180',
    # Показывать окна Chrome (при logginglevel=DEBUG всегда показывает), отключить можно только в windows, на линукс и mac всегда показывается
    # Этот режим был сделан из-за нестабильности работа headles chrome на puppeteer, кроме того он позволяет возвращать видимость браузера,
    # например для показа капчи.
    'show_chrome_': {'descr': 'Показывать окно chrome', 'type': 'checkbox'},
    'show_chrome': '0',
    # Пытаться спрятаться от скриптов определяющих что мы не человек, по умолчанию включено
    'playwright_stealth_': {'descr': 'Режим playwright stealth', 'type': 'checkbox'},
    'playwright_stealth': '1',
    # Режим Headless Прятать окна Chrome (при logginglevel=DEBUG всегда показывает)
    # Честный headless chrome режим, из этого режима вернуть окно в видимое нельзя
    'headless_chrome_': {'descr': 'Headless режим работы chrome', 'type': 'checkbox'},
    'headless_chrome': '1',
    # Честный headless chrome режим, из этого режима вернуть окно в видимое нельзя
    'feedback_': {'descr': 'Headless режим работы chrome', 'type': 'function'},
    'feedback': None,
    
    # Если в linux не установлен GUI или в докере чтобы запустить браузер не в headless может потребоваться включить xvfb
    # В докере он уже установлен из коробки
    'xvfb_': {'descr': 'Включить xvfb', 'type': 'checkbox'},
    'xvfb': '0',
    # NODE_TLS_REJECT_UNAUTHORIZED=0 отключить проверку сертификатов при загрузке движков
    'node_tls_reject_unauthorized_': {'descr': 'Отключение проверки сертификатов при загрузке браузерных движков, не меняйте этот параметр без крайней необходимости', 'type': 'text'},
    'node_tls_reject_unauthorized': '',
    # PLAYWRIGHT_BROWSERS_PATH
    'playwright_browsers_path_': {'descr': 'Путь по которому находится папка с движками браузеров, по умолчанию в LOCALAPPDATA\\ms-playwright, не меняйте этот путь без крайней необходимости', 'type': 'text'},
    'playwright_browsers_path': '',
    # Использовать браузер встроенный в движок playwright, если отключен, то движки не скачиваются
    'use_builtin_browser_': {'descr': 'Использовать браузер встроенный в движок playwright', 'type': 'checkbox'},
    'use_builtin_browser': '1',
    # Какой браузерный движок используется для запросов
    'browsertype_': {'descr': 'Какой браузерный движок используется для запросов', 'type': 'select', 'variants': 'chromium firefox'},
    'browsertype': 'chromium',
    # user-agent Какой user_agent использовать
    'user_agent_': {'descr': 'Какой user_agent использовать, если не указан использовать тот что есть', 'type': 'text', 'size': 200},
    'user_agent': '',
    # playwright_pause - остановить браузер после получения данных
    'playwright_pause_': {'descr': 'остановить браузер после получения данных и включить отладку. ВНИМАНИЕ!!!. Это отладочная опция, ее включение останавливает получение балансов', 'type': 'checkbox'},
    'playwright_pause': '0',
    # Путь к хрому - можно прописать явно в ini, иначе поищет из вариантов chrome_executable_path_alternate
    'chrome_executable_path_': {'descr': 'Путь к хрому', 'type': 'text', 'size': 100, 'validate': lambda i: (i == '' or os.path.exists(i))},
    'chrome_executable_path': '',
    # Для плагинов через хром сохранять в папке логов полученные responses и скриншоты
    'log_responses_': {'descr': 'Сохранять в папке логов полученные данные за последний запрос', 'type': 'checkbox'},
    'log_responses': '1',
    # Для плагинов через хром не загружать стили шрифты и картинки, включать с осторожностью
    'intercept_request_': {'descr': 'Не загружать стили, шрифты и картинки', 'type': 'checkbox'},
    'intercept_request': '1',
    # Для плагинов через хром не обрезать вычисляемое выражение в логе
    'log_full_eval_string_': {'descr': 'Для плагинов через хром не обрезать вычисляемое выражение в логе', 'type': 'checkbox'},
    'log_full_eval_string': '0',
    # В каких единицах идет выдача по интернету (варианты - см UNIT в начале файла settings.py)
    'interunit_': {'descr': 'В каких единицах идет выдача по интернету', 'type': 'select', 'variants': 'TB GB MB KB'},
    'interunit': 'GB',
    # спецвариант по просьбе Mr. Silver в котором возвращаются не остаток интернета, а использованный
    # 1 - показывать использованный трафик (usedByMe) по всем  или 0 - показывать оставшийся трафик (NonUsed) по всем
    # список тел, через запятую - показать использованный только для этого списка телефонов
    'mts_usedbyme_': {
        'descr': 'По МТС возвращать использованный трафик вместо оставшегося 1 - показывать использованный по всем, 0 - показывать оставшийся по всем, num1,num2,num3 - показывать использованный только по этим номерам',
        'type': 'text',
        'validate': lambda i: (i in ('0', '1') or re.match(r'^(\d\d\d+,)*\d\d\d+$', i))},
    'mts_usedbyme': '0',
    # спецвариант по просьбе dimon_s2020 при 0 берет данные по счетчику максимальные из всех
    # 1 - Переданные клиентом (ЛКК)
    # 2 - Снятые сотрудниками Мосэнергосбыт (АИИС КУЭ)
    # 3 - Поступившее через портал городских услуг (ПГУ)
    'mosenergosbyt_nm_indication_take_': {'descr': 'Мосэнергосбыт: Какие данные по электросчетчику брать, 0 - взять максимальный', 'type': 'text', 'validate': lambda i: i.isdigit()},
    'mosenergosbyt_nm_indication_take': '0',
    'mosenergosbyt_nm_indication_variants_': {'descr': 'Мосэнергосбыт: Для электросчетчика, какие варианты данных искать', 'type': 'text'},
    'mosenergosbyt_nm_indication_variants': '1:ЛКК,2:АИИС КУЭ,3:ПГУ',
    # Номер на который придет SMS при входе в ЛК теле2
    'tele2_sms_num_': {'descr': 'Номер на который придет SMS при логине в ЛК теле2 в формате 10 цифр, если не задан используется логин', 'type': 'text', 'validate': lambda i: (i.strip() == '' or i.isdigit() and len(i.strip()) == 10)},
    'tele2_sms_num': '',
    # Вести отдельный полный лог по стокам (stock.py)
    'stock_fulllog_': {'descr': 'Вести отдельный полный лог по стокам (stock.py)', 'type': 'checkbox'},
    'stock_fulllog': '0',
    # average_days - если нет в Options.ini Additional\AverageDays то возьмем отсюда
}


def get(key, kwargs):
    return kwargs.get(key.lower(), DEFAULTS.get(key.lower(), None))
