import yaml
import json

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

OWM_TOKEN = config['weather_api_key']
TELEGRAM_TOKEN = config['telegram_token']
PROXY_URL = config['proxy_url']
REQUEST_KWARGS = {'proxy_url': PROXY_URL}

OWM_URL = 'http://api.openweathermap.org/data/2.5/weather?appid={}&units=metric'.format(OWM_TOKEN)

RESPONCE_FORMAT = """* Температура - <b>{0} градусов по Цельсию</b> \n* Давление - <b>{1} мм рт. ст</b> \n* Скорость ветра - <b>{2} м/с</b> \n* Влажность - <b>{3}%</b> \n* Как стоит одется? - <b>{4}</b>"""

with open('clothes_recommendations.json', 'r') as f:
    RECOMMENDATION_DICT = json.load(f)


