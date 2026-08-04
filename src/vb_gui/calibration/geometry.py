from collections import OrderedDict

POINTS = OrderedDict([
    ("net_top_left", "Net Top Left"),
    ("net_top_right", "Net Top Right"),
    ("net_bottom_left", "Net Bottom Left"),
    ("net_bottom_right", "Net Bottom Right"),
    ("far_end_line_left", "Far End Line Left"),
    ("far_end_line_right", "Far End Line Right"),
    ("far_attack_line_left", "Far Attack Line Left"),
    ("far_attack_line_right", "Far Attack Line Right"),
    ("near_end_line_left", "Near End Line Left"),
    ("near_end_line_right", "Near End Line Right"),
    ("near_attack_line_left", "Near Attack Line Left"),
    ("near_attack_line_right", "Near Attack Line Right"),
    ("middle_line_left", "Middle Line Left"),
    ("middle_line_right", "Middle Line Right"),
])

LINES = [
    ("far_end_line_left", "far_end_line_right"),
    ("far_attack_line_left", "far_attack_line_right"),
    ("middle_line_left", "middle_line_right"),
    ("near_attack_line_left", "near_attack_line_right"),
    ("near_end_line_left", "near_end_line_right"),
    ("net_top_left", "net_top_right"),
    ("net_bottom_left", "net_bottom_right"),
]


def build_polygons(points):
    return {
        "far_attack_zone": [
            points["far_end_line_left"],
            points["far_end_line_right"],
            points["far_attack_line_right"],
            points["far_attack_line_left"],
        ],
        "near_attack_zone": [
            points["middle_line_left"],
            points["middle_line_right"],
            points["near_attack_line_right"],
            points["near_attack_line_left"],
        ],
        "far_back_zone": [
            points["far_attack_line_left"],
            points["far_attack_line_right"],
            points["middle_line_right"],
            points["middle_line_left"],
        ],
        "near_back_zone": [
            points["near_attack_line_left"],
            points["near_attack_line_right"],
            points["near_end_line_right"],
            points["near_end_line_left"],
        ],
        "net": [
            points["net_top_left"],
            points["net_top_right"],
            points["net_bottom_right"],
            points["net_bottom_left"],
        ],
    }
