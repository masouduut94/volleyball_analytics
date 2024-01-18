from enum import IntEnum


class VideoType(IntEnum):
    MAIN = 1
    RALLY = 2


class GameState(IntEnum):
    SERVICE = 1
    PLAY = 2
    NO_PLAY = 3
    WARMUP = 4


class ServiceType(IntEnum):
    FLOAT = 1
    HIGH_TOSS = 2


class CourtPosition(IntEnum):
    BACK_RIGHT = 1
    FRONT_RIGHT = 2
    FRONT_MID = 3
    FRONT_LEFT = 4
    BACK_LEFT = 5
    BACK_MIDDLE = 6
