from typing import Dict, Any, Optional
from datetime import datetime
import random
from models import UserContext, DeviceType, TimeOfDay, GeoPoint, UserBehavior, UserAction


class ContextSensor:
    """Датчик для сбора информации о контексте"""

    @staticmethod
    def get_current_context(user_id: int) -> UserContext:
        """Получить текущий контекст пользователя"""

        device_types = list(DeviceType)
        time_values = list(TimeOfDay)

        return UserContext(
            user_id=user_id,
            device_type=random.choice(device_types),
            screen_resolution=ContextSensor._get_screen_resolution(),
            operating_system=ContextSensor._get_os(),
            geolocation=ContextSensor._get_geolocation(),
            time_of_day=random.choice(time_values),
            view_history=ContextSensor._generate_view_history(),
            click_data=ContextSensor._generate_click_data(),
            user_preferences={'theme': 'dark', 'language': 'ru'},
            is_new_user=random.random() > 0.7
        )

    @staticmethod
    def _get_screen_resolution() -> str:
        """Получить разрешение экрана"""
        resolutions = ['1920x1080', '1366x768', '1440x900', '768x1024', '375x667']
        return random.choice(resolutions)

    @staticmethod
    def _get_os() -> str:
        """Получить операционную систему"""
        os_list = ['Windows 10', 'macOS Monterey', 'Ubuntu 20.04', 'iOS 15', 'Android 12']
        return random.choice(os_list)

    @staticmethod
    def _get_geolocation() -> GeoPoint:
        """Получить геолокацию"""
        # Координаты основных городов(модель)
        cities = [
            GeoPoint(55.7558, 37.6173),
            GeoPoint(59.9311, 30.3609),
            GeoPoint(54.7034, 20.5109),
            GeoPoint(56.8389, 60.6057),
        ]
        return random.choice(cities)

    @staticmethod
    def _generate_view_history() -> list:
        """Генерировать историю просмотров"""
        pages = ['home', 'products', 'catalog', 'cart', 'checkout', 'profile']
        return random.sample(pages, random.randint(2, 4))

    @staticmethod
    def _generate_click_data() -> list:
        """Генерировать данные кликов"""
        buttons = ['button_1', 'button_2', 'link_3', 'card_4', 'form_5']
        return random.sample(buttons, random.randint(1, 3))


class DataCollector:
    """Сборщик данных о поведении пользователя"""

    def __init__(self, database_manager):
        self.db = database_manager
        self.context_sensor = ContextSensor()

    def collect_user_behavior(self, user_id: int) -> UserBehavior:
        """Собрать данные о поведении пользователя"""

        context = self.context_sensor.get_current_context(user_id)

        # Получить данные о взаимодействиях из БД(модель)
        interactions = self.db.execute_query(
            'SELECT * FROM user_interactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 100',
            (user_id,)
        )

        # Рассчитать метрики(модель)
        page_views = len(context.view_history)
        clicks = len(context.click_data)
        effective_score = random.uniform(0.3, 0.95)
        interaction_time = random.uniform(30, 3600)

        interaction_map = {
            'page_views': page_views,
            'clicks': clicks,
            'time_spent': int(interaction_time)
        }

        return UserBehavior(
            user_id=user_id,
            page_views=page_views,
            clicks=clicks,
            geolocation=context.geolocation,
            effective_score=effective_score,
            interaction_time=interaction_time,
            interaction_map=interaction_map
        )

    def track_user_action(self, user_id: int, action: str,
                         component_id: Optional[int] = None) -> None:
        """Отследить действие пользователя"""
        self.db.record_interaction(
            user_id=user_id,
            action=action,
            component_id=component_id,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'session_id': f'session_{user_id}_{datetime.now().timestamp()}'
            }
        )