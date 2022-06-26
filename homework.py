import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict, List, Union

import requests

import telegram

from dotenv import load_dotenv

from exceptions import (
    APIStatusCodeError, TelegramError
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message: str) -> None:
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.info('Отправляем сообщение в телеграм')
        bot.send_message(TELEGRAM_CHAT_ID, message)

    except Exception as exc:
        logging.error('Ошибка при отправке сообщения в телеграм')
        raise TelegramError(
            f'Ошибка отправки сообщения в телеграм: {exc}'
        ) from exc

    else:
        logging.info('Сообщение в телеграм успешно отправлено')


def get_api_answer(
    current_timestamp: int
) -> Dict[str, Union[List[Dict[str, Union[int, str]]], int]]:
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if response.status_code != HTTPStatus.OK:
            raise APIStatusCodeError(
                'Неверный ответ сервера'
            )
        return response.json()

    except Exception as exc:
        logging.error(f'Ошибка при запросе к API: {exc}')
        raise APIStatusCodeError(
            'Неверный ответ сервера'
        )


def check_response(
    response: Dict[str, Union[List[Dict[str, Union[int, str]]], int]]
) -> List[Dict[str, Union[int, str]]]:
    """Проверяет ответ API на корректность."""
    logging.info('Проверка ответа от API начата')

    if not isinstance(response, dict) or response is None:
        raise TypeError(
            f'Ответ от API не является словарём: response = {response}'
        )

    elif any([response.get('homeworks') is None,
              response.get('current_date') is None]):
        raise KeyError(
            'Словарь ответа API не содержит ключей homeworks и/или '
            'current_date'
        )

    elif not isinstance(response.get('homeworks'), list):
        raise TypeError(
            'Ключ homeworks в ответе API не содержит списка'
        )

    else:
        return response['homeworks']


def parse_status(
    homework: List[Dict[str, Union[int, str]]]
) -> str:
    """Извлекает из информации о конкретной домашней работе.
    статус этой работы
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'

    except KeyError:
        logging.error('Недокументированный статус домашней работы')
        raise KeyError('Недокументированный статус домашней работы')


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    return all((
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = (
            'Отсутствуют обязательные переменные окружения: '
            'TELEGRAM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID. '
            'Программа принудительно остановлена'
        )
        logging.critical(error_message)
        sys.exit(error_message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    prev_message = ''
    prev_error = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            homework = homework[0]
            message = parse_status(homework)

            if prev_message != message:
                send_message(bot, message)
                prev_message = message

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as exc:
            message = f'Сбой в работе программы: {exc}'
            logging.error(message)

            if prev_error != message:
                send_message(bot, message)
                prev_error = message

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    log_format = (
        '%(asctime)s [%(levelname)s] %(message)s'
    )
    log_file = os.path.join(BASE_DIR, 'output.log')
    log_stream = sys.stdout
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding="UTF-8"),
            logging.StreamHandler(log_stream)
        ]
    )
    main()
