from enum import Enum

class SerializationStatus(Enum):
    ONGOING = "Ongoing"
    HIATUS = "Hiatus"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"