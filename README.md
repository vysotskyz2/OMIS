# Платформа для создания адаптивных пользовательских интерфейсов
## Описание

Модель системы для создания, управления и тестирования адаптивных правил пользовательского интерфейса. Система позволяет автоматически адаптировать UI на основе устройства пользователя, времени суток, типа пользователя и других параметров.

## Возможности
- Создание и управление правилами адаптации
- Библиотека UI компонентов
- Редактирование и удаление компонентов и правил
- Веб-интерфейс для управления
- Система отчетности (аналитика)

## Технологический стек

**Backend:**
- Python 3.7+
- Flask
- SQLite3
- Jinja2 Template Engine

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript

**Database:**
- SQLite3

## Быстрый старт

```bash
# Клонировать или скопировать проект
cd platform
# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///adaptive_ui.db')
DATABASE_PATH = 'adaptive_ui.db'
SECRET_KEY = os.getenv('SECRET_KEY', 'secret')

# Запустить приложение
python app.py

# Открыть в браузере
http://localhost:5000
```

## Структура проекта

```
adaptive_ui_platform/
├── templates/                 # HTML шаблоны
│   ├── base.html             # Базовый шаблон
│   ├── login.html            # Форма входа
│   ├── dashboard.html        # Дашборд
│   ├── rules.html            # Список правил
│   ├── create_rule.html      # Форма создания правила
│   ├── edit_rule.html        # Форма редактирования правила
│   ├── components.html       # Список компонентов
│   ├── create_component.html # Форма создания компонента
│   ├── edit_component.html   # Форма редактирования компонента
│   ├── view_component.html   # Просмотр компонента
│   ├── analytics.html        # Аналитика
│   └── dashboard.html        # Другие страницы
├── app.py                    #приложение Flask
├── adaptive_ui.db            # База данных (создается автоматически)
├── requirements.txt          # Python зависимости
└── README.md                 # Этот файл
```

## Архитектура системы

### Соответствие диаграмме классов

#### View Layer (Интерфейс Администратора)
- Веб-интерфейс для управления...
- Отображение статистики...
- CRUD операции...

#### Controllers (Контроллеры)
- Admin Panel Controller - полная реализация...
- Adaptation Controller - базовая логика...
- Data Collection Service - сбор данных...

#### Infrastructure (Инфраструктура) 
- Repository pattern для всех сущностей...
- Database Manager для управления...
- SQLite3 как хранилище...

#### Models (Модели Данных)
- Adaptation Rules - правила адаптации
- Components - UI компоненты
- User Context - минимальный контекст

#### Entry Point (Точка входа)
- Инициализация приложения
- Запуск сервера Flask
- Инициализация БД

## API Endpoints

- `POST /api/token` - Аутентификация
- `GET /api/status` - Статус системы
- `GET /api/rules` - Список правил
- `POST /api/rules` - Создать правило
- `GET /api/rules/{id}` - Получить правило
- `PUT /api/rules/{id}` - Обновить правило
- `DELETE /api/rules/{id}` - Удалить правило
- `GET /api/components` - Список компонентов
- `POST /api/components` - Создать компонент
- `GET /api/components/{id}` - Получить компонент
- `PUT /api/components/{id}` - Обновить компонент
- `DELETE /api/components/{id}` - Удалить компонент
- `GET /api/dashboard` - Данные дашборда
- `GET /api/analytics` - Аналитика

## Примечания

- В продакшн среде измените SECRET_KEY и пароли БД
- Система использует SQLite3 для хранения данных

## Лицензия
ЛР №6 ОМИС
