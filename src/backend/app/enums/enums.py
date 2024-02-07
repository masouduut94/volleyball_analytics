import enum


class GameState(enum.IntEnum):
    SERVICE = 0
    PLAY = 1
    NO_PLAY = 2


class ServiceType(enum.IntEnum):
    FLOAT_SERVE = 0
    HIGH_TOSS = 1
    LOW_TOSS = 2
