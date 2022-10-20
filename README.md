# homework-bot

## Описание

homework_bot - это телеграмм-бот, информирующий студента об изменении статуса его домашней работы.

Информация об статусе изменения домашней работы поступают при условии:

- Существует изменение статуса
- Прошло минимум 10 минут от кранего сообщения

Если что то пошло не по плану, то будут поступать в телеграм сообщения о БАГАХ.

## Стек технологий

Python 3.7.9
python-telegram-bot 13.7

## Запуск проекта 

1. Cклонируйте репозиторий:

`git clone git@github.com:FanisGi/yatube.git`

2. Cоздайте и активируйте виртуальное окружение:

`python3 -m venv venv`

`source env/bin/activate`

3. Установите зависимости из файла **requirements.txt**:

`python3 -m pip install --upgrade pip`

`pip install -r requirements.txt`

4. Создайте в папке проекта файл **.env**. Сохраните в ней:

- **PRACTICUM_TOKEN** - личный токен от ЯндексюПрактикуме;

- **TELEGRAM_TOKEN** - токен вашего телеграм-бота. Если у Вас ещё нет такого помощника, то его можно создать в приложении телеграм через **@BotFather** командой `/start`. Далее появится полноценная инструкция;

- **TELEGRAM_CHAT_ID** - личный id, получите его в приложении телеграм через **@userinfobot** командой `/start`.

5. Запускайте и радуйтесь.
