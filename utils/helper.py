import random
from pathlib import Path

project_base_path = Path(__file__).parents[1]
devGuildID = 829265067073339403
COLORS = [int(i, 16) for i in ["011C26", "025159", "08A696", "26FFDF", "F26A1B", "FF2C10"]]


def get_random_color() -> int:
    """
    Give a random color from the bf2042 color palate
    :return: int
    """
    return random.choice(COLORS)
