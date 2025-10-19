
# Бот-помощник для общежития №5 СПбПУ

Данный бот предназначен для автоматизации взаимодействия с жителями общежития.  
Ниже приведена инструкция по установке, настройке и запуску бота на Raspberry Pi Zero.

---

## Подключение к Raspberry Pi

1. Убедитесь, что Raspberry Pi подключен к Wi-Fi сети.
2. Найдите IP-адрес устройства в настройках роутера.
3. Подключитесь по SSH с помощью команды:

```bash
ssh <username>@<id_address>
```


Пример успешного подключения:

```bash
~$ ssh user@192.168.3.243
user@192.168.3.243`s password:
Linux raspberrypi 6.1.21+ #1642 Non Apr  3 17:19:14 BST 2023 army61

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Jun  6 17:42:12 2024 from 192.168.3.176
user@raspberrypi:~ $
```

---

## Настройка окружения

1. Клонируйте репозиторий с ботом:

```bash
git clone git@github.com:samb1232/dorm_bot.git
```

2. Перейдите в папку проекта:

```bash
cd dorm_bot
```

3. Создайте файл `.env` в директории проекта, заполните его корректными данными (или скопируйте корректный файл `.env` на устройство). Структура файла `.env` находится в файле `.env.example`.

> **Важно:** Для получения актуальных токенов обратитесь к техническому ответственному за бота или к создателю (@samb1232 в Telegram).

4. Установите зависимости Python:

```bash
pip install -r requirements.txt
```

---

## Запуск бота

Запустите бота в фоновом режиме:

```bash
python main.py &
```

Пример вывода:

```bash
user@raspberrypi:~/dorm_bot $ python main.py &
[1] 1507
```

Если вы видите сообщение `Бот запущен`, бот успешно запущен.

---

## Управление процессом

### Проверка работы бота

```bash
ps aux | grep python
```

Пример вывода:

```bash
user    1507  9.1 12.3  80716 54072 pts/1    S1   11:21   0:24 python main.py
user    1515  0.0  0.4   7432  1832 pts/1    S+   11:25   0:00 grep --color=auto python
```

### Завершение работы

Вариант 1 (через fg и Ctrl+C):

```bash
fg
python main.py
^C
```

Вариант 2 (через kill):

```bash
kill <process_id>
```


## Примечания

- Бот использует Google Drive и Google Sheets API для работы с файлами.
- Все конфиденциальные данные хранятся в `.env`.
- Все текстовые данные хранятся в `string.py`.

