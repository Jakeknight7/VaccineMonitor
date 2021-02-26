from enum import Enum

class Eligibility(Enum):
    HEALTHCARE_WORKER  = 0
    OLDER_THAN_65 = 1
    ESSENTIAL_WORKER = 2
    UNDERLYING_CONDITION = 3

class Dose(Enum):
    FIRST_AND_SECOND_DOSE = 0
    SECOND_DOSE = 1

class AppointmentTime(Enum):
    FIRST = 0
    LAST = -1