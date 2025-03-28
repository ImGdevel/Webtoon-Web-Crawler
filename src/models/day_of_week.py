from enum import Enum

class DayOfWeek(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

    @staticmethod
    def from_korean(korean_day):
        mapping = {
            "월": DayOfWeek.MONDAY,
            "화": DayOfWeek.TUESDAY,
            "수": DayOfWeek.WEDNESDAY,
            "목": DayOfWeek.THURSDAY,
            "금": DayOfWeek.FRIDAY,
            "토": DayOfWeek.SATURDAY,
            "일": DayOfWeek.SUNDAY
        }
        return mapping.get(korean_day)