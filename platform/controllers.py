from typing import List, Dict, Any, Optional
from models import AdaptationRule, ComponentUI, UserContext, Statistics
from database import DatabaseManager
from ml_engine import MLEngine
from data_collector import DataCollector
import json
from datetime import datetime


class AdminPanelController:
    """Контроллер панели администратора"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_rule(self, name: str, description: str,
                   conditions: Dict, actions: Dict, priority: int) -> int:
        """Создать правило адаптации"""
        rule_id = self.db.add_rule(name, description, conditions, actions, priority)
        print(f"[AdminPanelController] Правило '{name}' создано с ID: {rule_id}")
        return rule_id

    def get_analytics_report(self) -> Dict[str, Any]:
        """Получить аналитический отчет"""
        stats = self.db.get_statistics()
        rules = self.db.get_rules()

        report = {
            'summary': stats,
            'rules': rules,
            'timestamp': datetime.now().isoformat()
        }

        return report

    def get_all_rules(self) -> List[Dict]:
        """Получить все правила"""
        return self.db.get_rules()


class AdaptationController:
    """Контроллер адаптации интерфейса"""

    def __init__(self, db: DatabaseManager, ml_engine: MLEngine):
        self.db = db
        self.ml_engine = ml_engine
        self.data_collector = DataCollector(db)

    def handle_user_login(self, user_id: int) -> Dict[str, Any]:
        """Обработать вход пользователя"""
        # Собрать контекст пользователя
        behavior = self.data_collector.collect_user_behavior(user_id)

        # Предсказать действие
        predicted_action = self.ml_engine.predict_next_action(behavior)

        # Получить рекомендации адаптации
        rules = self.db.get_rules(enabled_only=True)
        recommendations = self.ml_engine.generate_recommendations(behavior, rules)

        # Применить правила
        layout = self.generate_layout(recommendations, rules)

        self.data_collector.track_user_action(user_id, 'login')

        return {
            'user_id': user_id,
            'predicted_action': predicted_action.value,
            'recommendations': recommendations,
            'layout': layout,
            'context': behavior.to_dict()
        }

    def generate_layout(self, recommendations: List[Dict],
                       rules: List[Dict]) -> Dict[str, Any]:
        """Сгенерировать макет интерфейса"""
        layout = {
            'header': self._create_header(),
            'main_content': self._create_main_content(recommendations),
            'sidebar': self._create_sidebar(),
            'footer': self._create_footer()
        }
        return layout

    def _create_header(self) -> Dict[str, str]:
        """Создать заголовок"""
        return {
            'title': 'Adaptive UI Platform',
            'user_menu': 'Profile | Settings | Logout'
        }

    def _create_main_content(self, recommendations: List[Dict]) -> List[Dict]:
        """Создать основной контент"""
        return recommendations

    def _create_sidebar(self) -> Dict[str, Any]:
        """Создать боковую панель"""
        return {
            'menu': ['Dashboard', 'Rules', 'Components', 'Analytics'],
            'widgets': []
        }

    def _create_footer(self) -> Dict[str, str]:
        """Создать подвал"""
        return {
            'copyright': '© 2024 Adaptive UI Platform',
            'links': ['About', 'Privacy', 'Terms']
        }


class DataCollectionService:
    """Сервис сбора данных"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.data_collector = DataCollector(db)

    def collect_context(self, user_id: int) -> Dict[str, Any]:
        """Собрать контекст пользователя"""
        behavior = self.data_collector.collect_user_behavior(user_id)
        return behavior.to_dict()

    def track_behavior(self, user_id: int, action: str,
                      component_id: Optional[int] = None) -> None:
        """Отследить поведение"""
        self.data_collector.track_user_action(user_id, action, component_id)


class TestingManager:
    """Менеджер тестирования"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def compare_variants(self, rule_id_a: int, rule_id_b: int) -> Dict[str, Any]:
        """Сравнить варианты адаптации"""
        rule_a = self.db.get_rule_by_id(rule_id_a)
        rule_b = self.db.get_rule_by_id(rule_id_b)

        return {
            'variant_a': rule_a,
            'variant_b': rule_b,
            'comparison': 'Results available after sufficient data collection'
        }