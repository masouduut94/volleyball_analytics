import enum


class GameState(enum.IntEnum):
    SERVICE = 1
    PLAY = 2
    NO_PLAY = 3


class ServiceType(enum.IntEnum):
    FLOAT_SERVE = 0
    HIGH_TOSS = 1
    LOW_TOSS = 2
