# Парсер BetsAPI Football Scraper

- __Назначение__: скрипт берет с BetsAPI актуальную информацию (total/avg market value, foreigners, natioanal_team_players, avg_age) по каждой футбольной команде в БД и при необходимости обновляет нужные поля в таблице `teams` 
- __Источник данных__: BetsAPI
- __Периодичность запуска__: Разовая (выполняется один цикл)
- __Зависимости__: `loguru, PyMySQL, python-dotenv, Requests, tqdm`
- __Ответственный__: Нарек Бабахани
- __Примечания__: 

    - Сначала запрашивает ближайшие upcoming match, если данных нет - берет ближайший ended матч. Затем по ID вытаскивает tm_stats
    - Считает в памяти список изменённых команд и раз в batch_size записывает их в БД, уменьшая кол-во запросов

  


## Как запустить на сервере:

1. Клонируем репозиторий
    ```
   
    git clone https://github.com/StatusSSS/betsapi_football.git
   
    cd betsapi_football
   ```

2. Cоздаем virtualenv внутри проекта
    ```
    python3 -m venv venv
    
    source venv/bin/activate
   ```

3. Устанавливаем зависимости
    ```
    pip install --upgrade pip
    
    pip install -r betsapi_football_scraper/deploy/requirements.txt
   ```

4. В каталоге deploy лежит .env файл, перенесите его в корень проекта и заполните его

    ```
    DB_HOST=
    DB_PORT=
    DB_USER=
    DB_PASS=
    DB_NAME=
    DB_SSL_CA=
    
   BETSAPI_TOKEN=
   ```

5. Проверяем, что скрипт запускается вручную
    ```
    python -m betsapi_football_scraper.runner
   ```

## Systemd‑служба

#### Сохраните файл betsapi_football_scraper.service у себя в systemd/system, заранее заменив поля <...>:

```angular2html
[Unit]
Description=BetsAPI Football Scraper
After=network.target

[Service]
User=<SYSTEM_USER>
Group=<SYSTEM_GROUP>

WorkingDirectory=<ABSOLUTE_PATH_TO>/betsapi_football
EnvironmentFile=<ABSOLUTE_PATH_TO>/betsapi_football/.env
ExecStart=<ABSOLUTE_PATH_TO>/betsapi_football/venv/bin/python -m betsapi_football_scraper.runner

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

- User/Group — системный пользователь, под которым будет крутиться сервис
- <ABSOLUTE_PATH_TO> — абсолютный путь к проекту

## Активация systemd
    
```
# Перечитываем конфигурацию systemd
sudo systemctl daemon-reload

# Включаем автозапуск при загрузке
sudo systemctl enable --now betsapi_football_scraper.service

# Проверяем статус
sudo systemctl status betsapi_football_scraper.service
```