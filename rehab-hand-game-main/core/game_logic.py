from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import random
import math


@dataclass
class Item:
    # Store subpixel precision for smooth movement
    x: float
    y: float
    radius: int
    speed_x: float = 0.0
    speed_y: float = 0.0


def generate_item(screen_width: int, screen_height: int, radius: int = 20, level: int = 1) -> Item:
    """Generate a new red-circle item fully inside the screen bounds.

    If level > 1, the item moves with speed proportional to level.
    """
    x = random.randint(radius, max(radius, screen_width - radius))
    y = random.randint(radius, max(radius, screen_height - radius))

    if level <= 1:
        speed_x = 0.0
        speed_y = 0.0
    else:
        # Random direction unit vector multiplied by speed per frame
        angle = random.uniform(0.0, 2.0 * math.pi)
        speed = level * 0.5
        speed_x = math.cos(angle) * speed
        speed_y = math.sin(angle) * speed

    return Item(x=float(x), y=float(y), radius=radius, speed_x=speed_x, speed_y=speed_y)


def check_collision(finger_x: int, finger_y: int, item: Item) -> bool:
    """Return True if the fingertip touches the circular item."""
    dx = finger_x - item.x
    dy = finger_y - item.y
    distance = math.hypot(dx, dy)
    return distance <= item.radius


def update_item_position(item: Item, screen_width: int, screen_height: int) -> None:
    """Move the item according to its velocity and bounce off screen edges.

    The item position is kept within [radius, width-radius] and
    [radius, height-radius]. If it touches an edge, the velocity axis is
    inverted to create a bounce effect.
    """
    # Update position
    item.x += item.speed_x
    item.y += item.speed_y

    # Bounce horizontally
    if item.x - item.radius < 0:
        item.x = item.radius
        item.speed_x *= -1
    elif item.x + item.radius > screen_width:
        item.x = screen_width - item.radius
        item.speed_x *= -1

    # Bounce vertically
    if item.y - item.radius < 0:
        item.y = item.radius
        item.speed_y *= -1
    elif item.y + item.radius > screen_height:
        item.y = screen_height - item.radius
        item.speed_y *= -1
