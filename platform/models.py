from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import json


class DeviceType(Enum):
    """Типы устройств"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class TimeOfDay(Enum):
    """Время суток"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class UserAction(Enum):
    """Возможные действия пользователя"""
    PURCHASE = "purchase"
    CHURN = "churn"
    NAVIGATION = "navigation"


@dataclass
class GeoPoint:
    """Геоточка пользователя"""
    latitude: float
    longitude: float

    def to_dict(self) -> Dict:
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass
class UserContext:
    """Контекст пользователя"""
    user_id: int
    device_type: DeviceType
    screen_resolution: str
    operating_system: str
    geolocation: GeoPoint
    time_of_day: TimeOfDay
    view_history: List[str] = field(default_factory=list)
    click_data: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    is_new_user: bool = True

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "device_type": self.device_type.value,
            "screen_resolution": self.screen_resolution,
            "operating_system": self.operating_system,
            "geolocation": self.geolocation.to_dict(),
            "time_of_day": self.time_of_day.value,
            "view_history": self.view_history,
            "click_data": self.click_data,
            "user_preferences": self.user_preferences,
            "is_new_user": self.is_new_user
        }


@dataclass
class ComponentUI:
    """Компонент пользовательского интерфейса"""
    id: int
    name: str
    type_component: str  # button, widget, form, card, etc.
    description: str
    html_template: str
    css_styles: str
    js_script: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type_component,
            "description": self.description,
            "html": self.html_template,
            "css": self.css_styles,
            "js": self.js_script
        }


@dataclass
class AdaptationRule:
    """Правило адаптации интерфейса"""
    id: int
    name: str
    description: str
    conditions: Dict[str, Any]  # условия срабатывания
    actions: Dict[str, Any]  # действия при срабатывании
    priority: int
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conditions": self.conditions,
            "actions": self.actions,
            "priority": self.priority,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class UserBehavior:
    """История поведения пользователя"""
    user_id: int
    page_views: int
    clicks: int
    geolocation: GeoPoint
    effective_score: float
    interaction_time: float
    interaction_map: Dict[str, int] = field(default_factory=dict)
    predicted_action: Optional[UserAction] = None

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "page_views": self.page_views,
            "clicks": self.clicks,
            "geolocation": self.geolocation.to_dict(),
            "effective_score": self.effective_score,
            "interaction_time": self.interaction_time,
            "interaction_map": self.interaction_map,
            "predicted_action": self.predicted_action.value if self.predicted_action else None
        }


@dataclass
class Statistics:
    """Статистика и метрики"""
    total_rules: int
    active_rules: int
    total_users: int
    metrics: Dict[str, float] = field(default_factory=dict)
    date_recorded: datetime = field(default_factory=datetime.now)
    effective_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "total_rules": self.total_rules,
            "active_rules": self.active_rules,
            "total_users": self.total_users,
            "metrics": self.metrics,
            "date_recorded": self.date_recorded.isoformat(),
            "effective_data": self.effective_data
        }