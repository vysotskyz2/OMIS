import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import os


class DatabaseManager:
    """Менеджер для управления базой данных SQLite"""

    def __init__(self, db_path: str = "adaptive_ui.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица правил адаптации
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

        # Таблица компонентов
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

        # Таблица истории взаимодействия
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                component_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Таблица статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_rules INTEGER,
                active_rules INTEGER,
                total_users INTEGER,
                metrics JSON,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Выполнить SELECT запрос"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Выполнить INSERT/UPDATE/DELETE запрос"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def add_rule(self, name: str, description: str, conditions: Dict,
                 actions: Dict, priority: int) -> int:
        """Добавить правило адаптации"""
        query = '''
            INSERT INTO adaptation_rules 
            (name, description, conditions, actions, priority)
            VALUES (?, ?, ?, ?, ?)
        '''
        conditions_json = json.dumps(conditions)
        actions_json = json.dumps(actions)
        return self.execute_update(query, (name, description, conditions_json, actions_json, priority))

    def get_rules(self, enabled_only: bool = False) -> List[Dict]:
        """Получить все правила"""
        query = 'SELECT * FROM adaptation_rules'
        if enabled_only:
            query += ' WHERE enabled = 1'
        query += ' ORDER BY priority DESC'
        return self.execute_query(query)

    def get_rule_by_id(self, rule_id: int) -> Optional[Dict]:
        """Получить правило по ID"""
        query = 'SELECT * FROM adaptation_rules WHERE id = ?'
        results = self.execute_query(query, (rule_id,))
        return results[0] if results else None

    def add_component(self, name: str, comp_type: str, description: str,
                     html_template: str, css_styles: str, js_script: str = "") -> int:
        """Добавить компонент"""
        query = '''
            INSERT INTO components 
            (name, type, description, html_template, css_styles, js_script)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute_update(query, (name, comp_type, description,
                                          html_template, css_styles, js_script))

    def get_components(self) -> List[Dict]:
        """Получить все компоненты"""
        query = 'SELECT * FROM components ORDER BY created_at DESC'
        return self.execute_query(query)

    def record_interaction(self, user_id: int, action: str,
                          component_id: Optional[int] = None,
                          metadata: Optional[Dict] = None) -> int:
        """Записать взаимодействие пользователя"""
        query = '''
            INSERT INTO user_interactions 
            (user_id, action, component_id, metadata)
            VALUES (?, ?, ?, ?)
        '''
        metadata_json = json.dumps(metadata or {})
        return self.execute_update(query, (user_id, action, component_id, metadata_json))

    def get_statistics(self) -> Dict:
        """Получить общую статистику"""
        rules_count = self.execute_query('SELECT COUNT(*) as count FROM adaptation_rules')
        active_rules = self.execute_query('SELECT COUNT(*) as count FROM adaptation_rules WHERE enabled = 1')
        users_count = self.execute_query('SELECT COUNT(DISTINCT user_id) as count FROM user_interactions')

        return {
            'total_rules': rules_count[0]['count'],
            'active_rules': active_rules[0]['count'],
            'total_users': users_count[0]['count']
        }