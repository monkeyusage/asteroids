import numpy as np
import pygame
from config import WIDTH, HEIGHT, WHITE, YELLOW, PLAYER_COORD, PLAYER_SPEED, FRICTION, STAR_SIZE
from typing import Dict, Union
from time import time


class Sprite:
    def __init__(self, screen, color, coordinates):
        self.screen = screen
        self.color = color
        self.coordinates = coordinates
        self.angle = np.random.randint(0, 360)
        self.display = True

    def draw(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def rotate(self, angle: int):
        center: np.ndarray = Sprite._get_center(
            self.coordinates
        )  # np.array([int, int])
        self.coordinates = Sprite._rotate_polygon(
            self.coordinates, center=center, degrees=angle
        )
        self._update_angle(angle)

    def _update_angle(self, angle: int):
        self.angle += angle
        if self.angle > 360:
            self.angle -= 360
        if self.angle < 0:
            self.angle += 360

    @staticmethod
    def _get_center(coordinates: np.ndarray) -> np.ndarray:
        return coordinates.mean(axis=0).astype("int16")

    @staticmethod
    def _rotate_polygon(points, center=(0, 0), degrees=0) -> np.ndarray:
        angle = np.deg2rad(degrees)
        return np.array(
            [Sprite._rotate_point(point, center, angle) for point in points]
        )

    @staticmethod
    def _rotate_point(point, center=(0, 0), angle=0):
        return np.array(
            [
                center[0]
                + (point[0] - center[0]) * np.cos(angle)
                - (point[1] - center[1]) * np.sin(angle),
                center[1]
                + (point[0] - center[0]) * np.sin(angle)
                + (point[1] - center[1]) * np.cos(angle),
            ]
        )


class Ship(Sprite):
    def __init__(self, screen, color=WHITE, coordinates=np.array(PLAYER_COORD)):
        super().__init__(screen, color, coordinates)
        self.velocity = np.array([0, 0], dtype=float)  # initial force
        self.angle = 0
        self.force = PLAYER_SPEED

    def draw(self):
        pygame.draw.polygon(self.screen, self.color, self.coordinates, 1)

    def update(self, user: Dict[str, Union[bool, int]] = {}):
        """Update information based on environment and user input

        Args:
            user (Dict[str, Union[bool, int]], optional): User input. Defaults to {}.

        Returns:
            Ship: applies changes on screen and returns self object for reuse in next iteration
        """
        if user:
            if user.get("rotate"):
                angle = user["rotate"]
                self.rotate(angle)
            if user.get("push"):
                self.update_velocity()
            if user.get("fire"):
                self.shoot()
        self.accelerate()
        self.draw()
        self.missiles = None
        return self

    def accelerate(self):
        # apply friction
        self.velocity = np.multiply(self.velocity, FRICTION)
        self.coordinates = np.add(self.coordinates, self.velocity)

    def update_velocity(self):
        rad = np.deg2rad(self.angle) - np.pi / 2
        acceleration = np.array([np.cos(rad) * self.force, np.sin(rad) * self.force])
        for idx, value in enumerate(self.velocity):
            if value >= 1.5:
                self.velocity[idx] = 1.5
        self.velocity = np.add(self.velocity, acceleration)

    def shoot(self):
        pass


class Missile(Sprite):
    def __init__(self, screen, velocity, coordinates=(0,0), size=STAR_SIZE):
        super().__init__(screen, color=YELLOW, coordinates=(0, 0))
        self.coordinates = coordinates
        self.size = size
        self.velocity = velocity
        self.speed = 4
    
    def update(self):
        self.coordinates = np.add(self.coordinates, self.velocity)

    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.coordinates, self.size)

        
class Star(Sprite):
    def __init__(self, screen, coordinates=(0, 0), size=STAR_SIZE):
        super().__init__(screen, color=WHITE, coordinates=(0, 0))
        self.set_coord()
        self.size = size

    def set_coord(self):
        pos_x = np.random.randint(0, WIDTH)
        pos_y = np.random.randint(0, HEIGHT)
        coordinates = [pos_x, pos_y]
        self.coordinates = coordinates

    def update(self, *args, **kwargs):
        if np.random.randint(0, 10):
            self.draw()
        return self

    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.coordinates, self.size)
