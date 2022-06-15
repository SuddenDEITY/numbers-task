# Numbers-Task

## Установка
1. Клонируем репозиторий:
```
git clone https://github.com/SuddenDEITY/numbers-task <directory_you_want>
```
2. В файле backend/config/settings.py добавить ваш telegram id в поле TG_CHAT_ID (в самом низу файла);

Обращу внимание, что telegram id и ник в телеграме это совсем разные вещи.

3. Чтобы получить telegram id вы можете нажать кнопку "Start" в чате с ботом @NumbersTestTaskBot;
4. Перейти по ссылке https://api.telegram.org/bot5503940773:AAGeakD300QX38gP1-FRlMlMbCmTtYAP5CQ/getUpdates найдите там свой ник и слева от него увидите ваш telegram id;
5. Билдим контейнеры:
```
docker-compose up --build
```
6. После того, как контейнеры полностью запустились, по ссылке http://127.0.0.1:3000 можете увидеть web-сервер React.

Ссылка на Google Sheets https://docs.google.com/spreadsheets/d/1B2uR_2BNK0SHB3878rUThFQCRjU5umpc7AvOfMOrPBQ/edit#gid=0
