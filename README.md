# Backend-сервис для интерфейса и алгоритма прогноза спроса на 14 дней для товаров собственного производства.

#### Проект backend-сервиса системы для управления поступающими запросами и обеспечивания взаимодействия между другими компонентами.

[![Run linter](https://github.com/Lentyan/backend/actions/workflows/run_linter.yml/badge.svg)](https://github.com/Lentyan/backend/actions/workflows/run_linter.yml)
[![Tests](https://github.com/Lentyan/backend/actions/workflows/run_tests.yml/badge.svg)](https://github.com/Lentyan/backend/actions/workflows/run_tests.yml)

# Содержание

1. [БРИФ](#brif)

   1.1 [ER - диаграмма сущностей](#db_er_blueprint)

2. [Подготовка к запуску](#start)

   2.1. [Правила работы с git](#git)

   2.2. [Poetry](#poetry)

   2.3. [Pre-commit](#pre-commit)

   2.4. [Настройка переменных окружения](#env)

3. [Запуск сервиса](#run-service)

   3.1. [Запуск сервиса для локальной разработки](#run-local)

# 1. [БРИФ](docs/brif.md) <a id="brif"></a>
   ## 1.1. [ER - диаграмма сущностей](docs/db_er_blueprint.pdf)<a id="db_er_blueprint"></a>

# 2. Подготовка к запуску <a id="start"></a>

Примечание: использование Poetry и pre-commit при работе над проектом
обязательно.

## 2.1. Правила работы с git <a id="git"></a>:

1. Две основные ветки: `master` и `develop`
2. Ветка `develop` — “предрелизная”, т.е. здесь должен быть рабочий и
   выверенный код
3. Создавая новую ветку, наследуйтесь от ветки `develop`
4. В `master` находится только production-ready код (CI/CD)
5. Правила именования веток
    - весь новый функционал — `feature/название-функционала`
    - исправление ошибок — `bugfix/название-багфикса`
    - работа с инфраструктурой - `build/название-инфраструктуры`
6. Пушим свою ветку в репозиторий и открываем Pull Request

## 2.2. Poetry <a id="poetry"></a>:

Poetry - это инструмент для управления зависимостями и виртуальными
окружениями, также может использоваться для сборки пакетов. В этом проекте
Poetry необходим для дальнейшей разработки приложения, его установка <b>
обязательна</b>.<br>

<details>
 <summary>
 Как скачать и установить?
 </summary>

### Установка:

Установите poetry
следуя [инструкции с официального сайта](https://python-poetry.org/docs/#installation).
<details>
 <summary>
 Команды для установки:
 </summary>
Для UNIX-систем и Bash on Windows вводим в консоль следующую команду:

> *curl -sSL https://install.python-poetry.org | python -*

Для WINDOWS PowerShell:

> *(Invoke-WebRequest -Uri https://install.python-poetry.org
-UseBasicParsing).Content | python -*
</details>
<br>
После установки перезапустите оболочку и введите команду

> poetry --version

Если установка прошла успешно, вы получите ответ в формате

> Poetry (version 1.2.0)

Для дальнейшей работы введите команду:

> poetry config virtualenvs.in-project true

Выполнение данной команды необходимо для создания виртуального окружения в
папке проекта.

После предыдущей команды создадим виртуальное окружение нашего проекта с
помощью команды:

> poetry install

Результатом выполнения команды станет создание в корне проекта папки .venv.
Зависимости для создания окружения берутся из файлов poetry.lock (
приоритетнее)
и pyproject.toml

Для добавления новой зависимости в окружение необходимо выполнить команду

> poetry add <package_name>

_Пример использования:_

> poetry add starlette

Также poetry позволяет разделять зависимости необходимые для разработки, от
основных.
Для добавления зависимости необходимой для разработки и тестирования
необходимо
добавить флаг ***--dev***

> poetry add <package_name> --dev

_Пример использования:_

> poetry add pytest --dev

</details>

<details>
 <summary>
 Порядок работы после настройки
 </summary>

<br>

Чтобы активировать виртуальное окружение, введите команду:

> poetry shell

Существует возможность запуска скриптов и команд с помощью команды без
активации окружения:

> poetry run <script_name>.py

_Примеры:_

> poetry run python script_name>.py
>
> poetry run pytest
>
> poetry run black

Порядок работы в оболочке не меняется. Пример команды для Win:

> python src\run_bot.py

Доступен стандартный метод работы с активацией окружения в терминале с
помощью команд:

Для WINDOWS:

> source .venv/Scripts/activate

Для UNIX:

> source .venv/bin/activate

</details>

В этом разделе представлены наиболее часто используемые команды.
Подробнее: https://python-poetry.org/docs/cli/

#### Активировать виртуальное окружение

```shell
poetry shell
```

#### Добавить зависимость

```shell
poetry add <package_name>
```

#### Обновить зависимости

```shell
poetry update
```

## 2.3. Pre-commit <a id="pre-commit"></a>:

<details>
 <summary>
 Настройка pre-commit
 </summary>
<br>

1. Убедиться, что pre-commit установлен:

   ```shell
   pre-commit --version
   ```

2. Настроить git hook скрипт:

   ```shell
   pre-commit install
   ```

Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому
стилю.
</details>

## 2.4. Настройка переменных окружения <a id="env"></a>

Перед запуском проекта необходимо создать копию файла
```.env-example```, назвав его ```.env``` и установить свои значения.

# 3. Запуск сервиса <a id="run-service"></a>

## 3.1. Запуск сервиса для локальной разработки <a id="run-local"></a>

Запуск сервиса в локальной среде рекомендуется выполнять с помощью команд:

* запуск сервиса с контейнером PostgreSQL:

```shell
make run-local
```

