from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

from database import DatabaseManager
from ml_engine import MLEngine
from controllers import AdminPanelController, AdaptationController, DataCollectionService, TestingManager
from infrastructure import ApplicationBootstrapper

app = Flask(__name__)
app.secret_key = 'secret'

db = DatabaseManager('adaptive_ui.db')
ml_engine = MLEngine()
bootstrapper = ApplicationBootstrapper()

admin_controller = AdminPanelController(db)
adaptation_controller = AdaptationController(db, ml_engine)
data_collection_service = DataCollectionService(db)
testing_manager = TestingManager(db)


# Декоратор для проверки аутентификации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Главная страница"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверка учетных данных (для демо)
        if username and password:
            session['user_id'] = 1
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Дашборд (панель администратора)"""
    stats = db.get_statistics()
    rules = admin_controller.get_all_rules()

    context = {
        'stats': stats,
        'rules': rules,
        'username': session.get('username')
    }

    return render_template('dashboard.html', **context)


@app.route('/rules')
@login_required
def rules():
    """Управление правилами"""
    rules_list = admin_controller.get_all_rules()

    return render_template('rules.html', rules=rules_list)


@app.route('/rules/create', methods=['GET', 'POST'])
@login_required
def create_rule():
    """Создать новое правило"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        priority = int(request.form.get('priority', 1))

        conditions = {
            'device_type': request.form.get('device_type'),
            'time_of_day': request.form.get('time_of_day'),
            'user_type': request.form.get('user_type')
        }

        actions = {
            'show_components': request.form.getlist('components'),
            'theme': request.form.get('theme'),
            'layout': request.form.get('layout')
        }

        rule_id = admin_controller.create_rule(
            name, description, conditions, actions, priority
        )

        return redirect(url_for('rules'))

    return render_template('rules.html', create_mode=True)


@app.route('/components')
@login_required
def components():
    """Библиотека компонентов"""
    components_list = db.get_components()

    return render_template('components.html', components=components_list)


@app.route('/analytics')
@login_required
def analytics():
    """Аналитика и отчеты"""
    report = admin_controller.get_analytics_report()

    return render_template('analytics.html', report=report)


@app.route('/api/user/context/<int:user_id>', methods=['GET'])
def get_user_context(user_id):
    """API: Получить контекст пользователя"""
    context = data_collection_service.collect_context(user_id)
    return jsonify(context)


@app.route('/api/user/adapt', methods=['POST'])
def adapt_interface():
    """API: Адаптировать интерфейс"""
    user_id = request.json.get('user_id')

    result = adaptation_controller.handle_user_login(user_id)
    return jsonify(result)


@app.route('/api/rules', methods=['GET'])
def get_rules_api():
    """API: Получить все правила"""
    rules = admin_controller.get_all_rules()
    return jsonify(rules)


@app.route('/api/rules', methods=['POST'])
def create_rule_api():
    """API: Создать правило"""
    data = request.json

    rule_id = admin_controller.create_rule(
        data.get('name'),
        data.get('description'),
        data.get('conditions'),
        data.get('actions'),
        data.get('priority', 1)
    )

    return jsonify({'rule_id': rule_id, 'status': 'created'})


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """API: Получить аналитику"""
    report = admin_controller.get_analytics_report()
    return jsonify(report)


@app.route('/api/test/compare', methods=['POST'])
def test_compare_variants():
    """API: Сравнить варианты"""
    data = request.json

    result = testing_manager.compare_variants(
        data.get('rule_a_id'),
        data.get('rule_b_id')
    )

    return jsonify(result)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Обработка ошибки 404"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка ошибки 500"""
    return jsonify({'error': 'Internal server error'}), 500


# ==================== ИНИЦИАЛИЗАЦИЯ ====================

if __name__ == '__main__':
    # Инициализация системы
    bootstrapper.main()
    bootstrapper.init_services()

    # Создание тестовых данных
    def seed_database():
        """Создание тестовых данных"""
        # Проверить, не пусто ли БД
        rules = db.get_rules()
        if len(rules) == 0:
            print("[SEED] Добавление тестовых данных...")

            # Добавить тестовые правила
            db.add_rule(
                "Mobile Morning Rule",
                "Show quick tasks for mobile users in the morning",
                {"device_type": "mobile", "time_of_day": "morning"},
                {"show_components": ["quick_tasks"], "layout": "compact"},
                priority=10
            )

            db.add_rule(
                "Evening Dark Theme",
                "Apply dark theme in the evening",
                {"time_of_day": "evening"},
                {"theme": "dark", "layout": "relaxed"},
                priority=5
            )

            # Добавить тестовые компоненты
            db.add_component(
                "Quick Tasks Widget",
                "widget",
                "Быстрый доступ к задачам",
                "<div class='quick-tasks'>{{ tasks }}</div>",
                ".quick-tasks { background: #f0f0f0; padding: 10px; }"
            )

            db.add_component(
                "CTA Button",
                "button",
                "Call-to-action кнопка",
                "<button class='cta'>{{ text }}</button>",
                ".cta { background: #007bff; color: white; padding: 10px 20px; }"
            )

            print("[SEED] Тестовые данные добавлены")

    seed_database()

    print("[APP] Запуск Flask приложения...")
    print("[APP] Доступно на http://localhost:5000")
    print("[APP] Вход: admin / password")

    app.run(debug=True, port=5000)