# i18n-service
tiny i18n-service with Django Framework

## environment infomations
- Python: 3.6.5 
- Django: 2.2.4
- Database: SQLite

## How-To
1. Install (or Update) Python >= 3.6.5
2. Clone repository (https://github.com/roharoha/i18n-service.git)
3. Set-up virtual environment in project root directory

    ```
    $ path/did/you/clone/i18n-service python3 -m venv .venv
    $ path/did/you/clone/i18n-service . .venv/bin/activate
    $ (.venv) path/did/you/clone/i18n-service # <- check it!
    ```
4. install all depedancies (Using requirements.txt)
    ```
    $ (.venv) path/did/you/clone/i18n-service pip install -r requirements.txt
    ```

5. Migrate All models in Django project

    db.sqlite3 file will be created in project root directory.
    ```
   $ (.venv) path/did/you/clone/i18n-service ./manage.py migrate
   ```
   
6. (Optional) Test all cases if you need to check all endpoint works...

    if there is no error & all test are ok, running server is ready.
    ```
   $ (.venv) path/did/you/clone/i18n-service ./manage.py test
    ``` 
7. run server

    ```
   $ (.venv) path/did/you/clone/i18n-service ./manage.py runserver
   ```
    after command, all endpoint can be here: https://127.0.0.1:8000/