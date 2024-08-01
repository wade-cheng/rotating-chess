from enum import Enum

# gray on black
# BACKGROUND_COLOR = (150, 150, 150)
# BOARD_COLOR = (0, 0, 0)

# beige on brown
BACKGROUND_COLOR = (240, 217, 181)
BOARD_COLOR = (181, 136, 99)

SELECTED_PIECE_COLOR = (255, 255, 153)  # yellowish
MOVE_POINT_COLOR = (173, 255, 244)  # cyanish
CAPTURE_POINT_COLOR = (255, 0, 0)  # red
HITCIRCLE_COLOR = (0, 255, 127)  # springgreen

HITCIRCLE_RADIUS: int = 17

# THESE ARE SKIN OPTIONS. DO NOT EDIT
class PieceSkin(Enum):
    a = ""
    b = "1"
    c = "2"
    d = "3"


# EDIT SKIN HERE
SKIN = PieceSkin.b

# whether a player may select and rotate multiple pieces at once
CAN_SELECT_MULTIPLE = False
