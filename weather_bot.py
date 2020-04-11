from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import requests
import config as weather_constant
from requests.exceptions import RequestException
import re
import logging
import sys
import signal

logger = logging.getLogger("CTO_WeatherBot")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_recommendation(temp):
    answer = None
    for key in list(weather_constant.RECOMMENDATION_DICT.keys())[:-1]:
        if temp < int(key):
            answer = weather_constant.RECOMMENDATION_DICT[key]
            break

    if answer is None:
        answer = weather_constant.RECOMMENDATION_DICT['top_temp']

    return answer


def check_string(text):
    clean_string = False
    if re.match("^[а-яА-Яa-zA-Z, ]*$", text):
        clean_string = True
    return clean_string


def get_weather(url):
    weather_dict = None
    try:
        weather_dict = requests.get(url, timeout=3).json()
    except RequestException as e:
        logging.error(e)
        logging.error("Could not reach OWM API!")
    return weather_dict


def get_update_message(update):
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    return message


def handle_text_request(bot, update):
    message = get_update_message(update)
    string_check = check_string(message.text)
    if string_check:
        url = weather_constant.OWM_URL + "&q={0}".format(message.text)
        logger.debug("Requesting weather for request: ", message.text)
        weather_dict = get_weather(url)
        if weather_dict is not None:
            try:
                answer = weather_constant.RESPONCE_FORMAT.format(weather_dict['main']["temp"],
                                                                 weather_dict["main"]["pressure"],
                                                                 weather_dict["wind"]['speed'],
                                                                 weather_dict['main']['humidity'],
                                                                 get_recommendation(float(weather_dict['main']['feels_like'])))
            except KeyError:
                answer = "Не могу найти такую локацию!"
        else:
            answer = 'Сервис погоды не работает, попробуйте позже!'
    else:
        answer = "Не могу понять, что Вы имели ввиду, посмотрите /help!"

    bot.send_message(chat_id=update.message.chat_id, text=answer, parse_mode=telegram.ParseMode.HTML)


def handle_location_request(bot, update):
    message = get_update_message(update)
    latitude, longitude = message.location.latitude, message.location.longitude
    url = weather_constant.OWM_URL + "&lat={0}&lon={1}&cnt=1".format(latitude, longitude)
    logger.debug("Requesting weather for request: ", message.text)
    weather_dict = get_weather(url)
    if weather_dict is not None:
        try:
            answer = weather_constant.RESPONCE_FORMAT.format(weather_dict['main']["temp"],
                                                             weather_dict["main"]["pressure"],
                                                             weather_dict["wind"]['speed'],
                                                             weather_dict['main']['humidity'],
                                                             get_recommendation(float(weather_dict['main']['feels_like'])))
        except:
            answer = "Не могу найти такую локацию!"
    else:
        answer = 'Сервис погоды не работает, попробуйте позже!'
    bot.send_message(chat_id=update.message.chat_id, text=answer, parse_mode=telegram.ParseMode.HTML)



def help_service(bot, update):
    help_message = "Я могу давать информацию о погоде на сегодня и давать рекоммендации по тому что стоит одеть. \n" \
                   "Отправь мне свою телеграм локацию или просто напиши город в котором хочешь узнать погоду. \n" \
                   "Я разбираю следующие форматы сообщений: \n" \
                   "* <b> город </b>\n" \
                   "* <b> город,страна </b> \n" \
                   "* <b> телеграм локация </b>"
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=help_message, parse_mode=telegram.ParseMode.HTML)

def sig_handler(signal, frame):
    logger.info("Weather bot terminating...")
    sys.exit(0)

def main():
    logger.info("Weather bot is starting...")
    signal.signal(signal.SIGINT, sig_handler)

    updater = Updater(token=weather_constant.TELEGRAM_TOKEN, request_kwargs=weather_constant.REQUEST_KWARGS)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('help', help_service))
    dispatcher.add_handler(CommandHandler('start', help_service))

    dispatcher.add_handler(MessageHandler(Filters.text, handle_text_request))
    dispatcher.add_handler(MessageHandler(Filters.location, handle_location_request))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
