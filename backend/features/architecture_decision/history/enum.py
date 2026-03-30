from backend.features.project.enum import Enum


class HistoryEventType(str, Enum):
    CREATED = "CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    FIELD_CHANGED = "FIELD_CHANGED"