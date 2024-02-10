import enum


class GameState(enum.IntEnum):
    SERVICE = 1
    PLAY = 2
    NO_PLAY = 3


class ServiceType(enum.IntEnum):
    FLOAT_SERVE = 0
    HIGH_TOSS = 1
    LOW_TOSS = 2


class CourtZone(enum.IntEnum):
    BACK_LEFT_Z1 = 1
    FRONT_LEFT_Z2 = 2
    FRONT_MIDDLE_Z3 = 3
    FRONT_RIGHT_Z4 = 4
    BACK_RIGHT_Z5 = 5
    BACK_MIDDLE_Z6 = 6


class VolleyBallPositions(enum.IntEnum):
    SETTER = 1
    OPPOSITE_HITTER = 2
    MIDDLE_BLOCKER = 3
    OUTSIDE_HITTER = 4
    LIBERO = 5
