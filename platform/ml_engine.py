from typing import Dict, Any, List
import random
from models import UserBehavior, UserAction, GeoPoint


class MLEngine:
    """модель движка"""

    def __init__(self):
        self.model_accuracy = 0.85  # целевая точность 85%

    def predict_next_action(self, behavior: UserBehavior) -> UserAction:
        """
        Прогнозирование следующего действия пользователя
        (Purchase, Churn, Navigation)
        """

        # Вычисление вероятностей на основе поведения
        purchase_score = self._calculate_purchase_probability(behavior)
        churn_score = self._calculate_churn_probability(behavior)
        navigation_score = 1.0 - purchase_score - churn_score

        # Выбор действия с наибольшей вероятностью
        scores = {
            UserAction.PURCHASE: purchase_score,
            UserAction.CHURN: churn_score,
            UserAction.NAVIGATION: navigation_score
        }

        predicted_action = max(scores, key=scores.get)
        behavior.predicted_action = predicted_action

        return predicted_action

    def _calculate_purchase_probability(self, behavior: UserBehavior) -> float:
        """Вычислить вероятность покупки"""
        # Модель
        base_score = behavior.effective_score * 0.5
        interaction_bonus = min(0.3, behavior.clicks * 0.05)
        time_bonus = min(0.2, behavior.interaction_time * 0.01)

        return base_score + interaction_bonus + time_bonus

    def _calculate_churn_probability(self, behavior: UserBehavior) -> float:
        """Вычислить вероятность отсева (churn)"""
        # Модель
        if behavior.clicks == 0:
            return 0.6

        if behavior.interaction_time < 60:
            return 0.3

        return 0.1

    def generate_recommendations(self, behavior: UserBehavior,
                                 available_rules: List[Dict]) -> List[Dict]:
        """Генерировать рекомендации адаптации"""
        predicted_action = self.predict_next_action(behavior)

        recommendations = []

        if predicted_action == UserAction.PURCHASE:
            # Рекомендовать CTA-виджеты для покупки
            recommendations.append({
                'type': 'cta_widget',
                'content': 'Добавить в корзину',
                'priority': 1,
                'conversion_potential': 0.05
            })

        elif predicted_action == UserAction.CHURN:
            # Рекомендовать удерживающие элементы
            recommendations.append({
                'type': 'retention_widget',
                'content': 'Специальное предложение',
                'priority': 1,
                'retention_potential': 0.3
            })

        else:  # NAVIGATION
            # Рекомендовать навигационные элементы
            recommendations.append({
                'type': 'navigation_widget',
                'content': 'Рекомендуемые разделы',
                'priority': 2
            })

        return recommendations

    def get_model_accuracy(self) -> float:
        """Получить точность модели"""
        return self.model_accuracy