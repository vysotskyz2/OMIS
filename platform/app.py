from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

DB_PATH = 'adaptive_ui.db'


def init_db():
    """Инициализация базы данных"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                conditions JSON NOT NULL,
                actions JSON NOT NULL,
                priority INTEGER NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                html_template TEXT,
                css_styles TEXT,
                js_script TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Добавляем тестовые данные
        cursor.execute('''
            INSERT INTO components (name, type, description, html_template, css_styles)
            VALUES ('Quick Tasks Widget', 'widget', 'Быстрый доступ к задачам',
                    '<div class="quick-tasks"><h3>Мои задачи</h3><ul><li>Задача 1</li></ul></div>',
                    '.quick-tasks { background: #f0f0f0; padding: 10px; border-radius: 5px; }')
        ''')

        cursor.execute('''
            INSERT INTO components (name, type, description, html_template, css_styles)
            VALUES ('CTA Button', 'button', 'Call-to-action кнопка',
                    '<button class="cta-btn">Купить сейчас</button>',
                    '.cta-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }')
        ''')

        cursor.execute('''
            INSERT INTO components (name, type, description, html_template, css_styles)
            VALUES ('User Card', 'card', 'Карточка пользователя',
                    '<div class="user-card"><img src="avatar.jpg"><h4>Имя</h4><p>Описание</p></div>',
                    '.user-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; text-align: center; }')
        ''')

        conn.commit()
        conn.close()
        print("[INIT] База данных инициализирована")


def get_db_connection():
    """Получить соединение с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_rules():
    """Получить все правила"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM adaptation_rules ORDER BY priority DESC')
    rules = cursor.fetchall()
    conn.close()
    return [dict(rule) for rule in rules]


def get_rule_by_id(rule_id):
    """Получить правило по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM adaptation_rules WHERE id=?', (rule_id,))
    rule = cursor.fetchone()
    conn.close()
    return dict(rule) if rule else None


def create_rule(name, description, conditions, actions, priority):
    """Создать правило"""
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions_json = json.dumps(conditions)
    actions_json = json.dumps(actions)
    cursor.execute('''
        INSERT INTO adaptation_rules (name, description, conditions, actions, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, conditions_json, actions_json, priority))
    conn.commit()
    rule_id = cursor.lastrowid
    conn.close()
    return rule_id


def update_rule(rule_id, name, description, conditions, actions, priority, enabled):
    """Обновить правило"""
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions_json = json.dumps(conditions)
    actions_json = json.dumps(actions)
    cursor.execute('''
        UPDATE adaptation_rules 
        SET name=?, description=?, conditions=?, actions=?, priority=?, enabled=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    ''', (name, description, conditions_json, actions_json, priority, enabled, rule_id))
    conn.commit()
    conn.close()
    return True


def delete_rule(rule_id):
    """Удалить правило"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM adaptation_rules WHERE id=?', (rule_id,))
    conn.commit()
    conn.close()
    return True


def toggle_rule(rule_id):
    """Включить/выключить правило"""
    rule = get_rule_by_id(rule_id)
    if not rule:
        return False

    new_status = not rule['enabled']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE adaptation_rules SET enabled=? WHERE id=?', (new_status, rule_id))
    conn.commit()
    conn.close()
    return True


def get_all_components():
    """Получить все компоненты"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM components ORDER BY created_at DESC')
    components = cursor.fetchall()
    conn.close()
    return [dict(comp) for comp in components]


def get_component_by_id(component_id):
    """Получить компонент по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM components WHERE id=?', (component_id,))
    component = cursor.fetchone()
    conn.close()
    return dict(component) if component else None


def create_component(name, comp_type, description, html_template, css_styles, js_script=""):
    """Создать компонент"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO components (name, type, description, html_template, css_styles, js_script)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, comp_type, description, html_template, css_styles, js_script))
    conn.commit()
    component_id = cursor.lastrowid
    conn.close()
    return component_id


def update_component(component_id, name, comp_type, description, html_template, css_styles, js_script=""):
    """Обновить компонент"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE components 
        SET name=?, type=?, description=?, html_template=?, css_styles=?, js_script=?
        WHERE id=?
    ''', (name, comp_type, description, html_template, css_styles, js_script, component_id))
    conn.commit()
    conn.close()
    return True


def delete_component(component_id):
    """Удалить компонент"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM components WHERE id=?', (component_id,))
    conn.commit()
    conn.close()
    return True


def get_statistics():
    """Получить статистику"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM adaptation_rules')
    total_rules = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM adaptation_rules WHERE enabled = 1')
    active_rules = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM components')
    total_components = cursor.fetchone()['count']

    conn.close()

    return {
        'total_rules': total_rules,
        'active_rules': active_rules,
        'total_components': total_components
    }



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
    """Дашборд"""
    stats = get_statistics()
    rules = get_all_rules()

    for rule in rules:
        if isinstance(rule.get('conditions'), str):
            rule['conditions'] = json.loads(rule['conditions'])
        if isinstance(rule.get('actions'), str):
            rule['actions'] = json.loads(rule['actions'])

    return render_template('dashboard.html',
                           stats=stats,
                           rules=rules,
                           username=session.get('username'))


@app.route('/rules')
@login_required
def rules():
    """Управление правилами"""
    rules_list = get_all_rules()

    for rule in rules_list:
        if isinstance(rule.get('conditions'), str):
            rule['conditions'] = json.loads(rule['conditions'])
        if isinstance(rule.get('actions'), str):
            rule['actions'] = json.loads(rule['actions'])

    return render_template('rules.html', rules=rules_list)


@app.route('/rules/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    """Редактировать правило"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        priority = int(request.form.get('priority', 1))
        enabled = request.form.get('enabled') == 'on'

        conditions = {
            'device_type': request.form.get('device_type'),
            'time_of_day': request.form.get('time_of_day'),
            'user_type': request.form.get('user_type')
        }

        actions = {
            'theme': request.form.get('theme'),
            'layout': request.form.get('layout')
        }

        update_rule(rule_id, name, description, conditions, actions, priority, enabled)
        return redirect(url_for('rules'))

    rule = get_rule_by_id(rule_id)
    if not rule:
        return redirect(url_for('rules'))

    if isinstance(rule.get('conditions'), str):
        rule['conditions'] = json.loads(rule['conditions'])
    if isinstance(rule.get('actions'), str):
        rule['actions'] = json.loads(rule['actions'])

    return render_template('edit_rule.html', rule=rule)


@app.route('/rules/<int:rule_id>/delete', methods=['POST'])
@login_required
def delete_rule_route(rule_id):
    """Удалить правило"""
    delete_rule(rule_id)
    return redirect(url_for('rules'))


@app.route('/rules/<int:rule_id>/toggle', methods=['POST'])
@login_required
def toggle_rule_route(rule_id):
    """Включить/выключить правило"""
    toggle_rule(rule_id)
    return redirect(url_for('rules'))


@app.route('/rules/create', methods=['GET', 'POST'])
@login_required
def create_rule_page():
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
            'theme': request.form.get('theme'),
            'layout': request.form.get('layout')
        }

        create_rule(name, description, conditions, actions, priority)
        return redirect(url_for('rules'))

    return render_template('create_rule.html')


@app.route('/components')
@login_required
def components():
    """Библиотека компонентов"""
    components_list = get_all_components()
    return render_template('components.html', components=components_list)


@app.route('/components/create', methods=['GET', 'POST'])
def create_component_page():
    """Создание нового компонента"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO components (name, type, description, html_template, css_styles, js_script)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.form.get('name'),
                request.form.get('type'),
                request.form.get('description'),
                request.form.get('html_template'),
                request.form.get('css_styles'),
                request.form.get('js_script', '')
            ))
            conn.commit()
            conn.close()
            return redirect(url_for('components'))
        except Exception as e:
            print(f"Error creating component: {e}")
            return redirect(url_for('components'))

    return render_template('create_component.html')

@app.route('/components/<int:component_id>/view', methods=['GET'])
@login_required
def view_component(component_id):
    """Просмотреть компонент"""
    component = get_component_by_id(component_id)
    if not component:
        return redirect(url_for('components'))

    return render_template('view_component.html', component=component)


@app.route('/components/<int:component_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_component(component_id):
    """Редактировать компонент"""
    if request.method == 'POST':
        name = request.form.get('name')
        comp_type = request.form.get('type')
        description = request.form.get('description')
        html_template = request.form.get('html_template')
        css_styles = request.form.get('css_styles')
        js_script = request.form.get('js_script', '')

        update_component(component_id, name, comp_type, description,
                         html_template, css_styles, js_script)
        return redirect(url_for('components'))

    component = get_component_by_id(component_id)
    if not component:
        return redirect(url_for('components'))

    return render_template('edit_component.html', component=component)


@app.route('/components/<int:component_id>/delete', methods=['POST'])
@login_required
def delete_component_route(component_id):
    """Удалить компонент"""
    delete_component(component_id)
    return redirect(url_for('components'))


@app.route('/analytics')
@login_required
def analytics():
    """Аналитика и отчеты"""
    stats = get_statistics()
    rules = get_all_rules()

    report = {
        'summary': stats,
        'rules': rules,
        'timestamp': datetime.now().isoformat()
    }

    return render_template('analytics.html', report=report)


# ==================== API ENDPOINTS ====================

@app.route('/api/rules', methods=['GET'])
def api_get_rules():
    """API: Получить все правила"""
    rules = get_all_rules()
    for rule in rules:
        if isinstance(rule.get('conditions'), str):
            rule['conditions'] = json.loads(rule['conditions'])
        if isinstance(rule.get('actions'), str):
            rule['actions'] = json.loads(rule['actions'])
    return jsonify(rules)


@app.route('/api/rules', methods=['POST'])
def api_create_rule():
    """API: Создать правило"""
    data = request.json
    rule_id = create_rule(
        data.get('name'),
        data.get('description'),
        data.get('conditions'),
        data.get('actions'),
        data.get('priority', 1)
    )
    return jsonify({'rule_id': rule_id, 'status': 'created'})


@app.route('/api/components', methods=['GET'])
def api_get_components():
    """API: Получить все компоненты"""
    components = get_all_components()
    return jsonify(components)


@app.route('/api/statistics', methods=['GET'])
def api_get_statistics():
    """API: Получить статистику"""
    stats = get_statistics()
    return jsonify(stats)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Обработка ошибки 404"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка ошибки 500"""
    return jsonify({'error': 'Internal server error'}), 500


# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    init_db()
    print("[APP] Доступно на http://localhost:5000")

    app.run(debug=True, port=5000)