
import random


TICKET_REGEX = "[A-Z0-9]+"
TICKET_VALUES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

DEFAULT_LEN = 8    # 2.8 trillion entries


def get(length=DEFAULT_LEN):
    """Randomly generate and return a ticket."""
    # TODO: better generation technique.
    return "".join((random.choice(TICKET_VALUES) for value in range(length)))
