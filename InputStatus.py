from enum import Enum

class InputStatusEnum(Enum):
    NOTHING = 1
    SINGLE_PRESS = 2
    DOUBLE_PRESS = 3
    TRIPLE_PRESS = 4
    LONG_PRESS = 5
    ENCODER_INCREASE = 6
    ENCODER_DECREASE = 7
    NEXT_SP = 8
    PREVIOUS_SP = 9
    NEXT_DP = 10
    PREVIOUS_DP = 11
