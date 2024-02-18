# Проект для автоматического создания конкурсов для телеграм каналов
:octocat:

Этот проект предназначен для автоматического создания конкурсов для телеграм каналов по шаблону и подведения их итогов, а также добавления нескольких каналов для одного пользователя и планирования каждого конкурса с помощью асинхронного apScheduler.

## Основные файлы

Основные файлы проекта находятся в папке `src`:

- `main.py`: Основной файл, содержащий основную логику и взаимодействие с Telegram ботом.
- `functions_helpers.py`: Вспомогательные функции.
- `constants_and_helpers.py`: Константы и классы с состояниями.
- `buttons.py`: Описание кнопок и клавиатур.

## Файлы в папке `src/databases`

В папке `src/databases` находятся файлы, связанные с базой данных:

- `models_db.py`: Описание моделей БД.
- `databases.py`: Функции для работы с БД.

## Установка и настройка

Чтобы установить и настроить проект, выполните следующие шаги:

1. Установите все зависимости с помощью команды:

   ```shell
   pip3 install -r requirements.txt
   ```

2. Установите все необходимые переменные в файле `.env`.

3. Запустите файл `main.py`.

4. Если у вас возникли вопросы или требуется дополнительная помощь, обратитесь к разработчику:

- Telegram: @elpasotoro
