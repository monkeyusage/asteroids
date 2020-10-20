import numpy as np
import pygame
from config import (
    WIDTH,
    HEIGHT,
    WHITE,
    YELLOW,
    RED,
    PLAYER_COORD,
    PLAYER_SPEED,
    FRICTION,
    STAR_SIZE,
    PARTICLE_SIZE,
    MISSILE_SPEED,
    MISSILES_PER_SEC,
    N_PARTICLES,
)
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
        self._update_angle(angle)
        center: np.ndarray = Sprite._get_center(
            self.coordinates
        )  # np.array([int, int])
        self.coordinates = Sprite._rotate_polygon(
            self.coordinates, center=center, degrees=angle
        )

    def _update_angle(self, angle: int):
        self.angle += angle
        if self.angle > 360:
            self.angle -= 360
        if self.angle < 0:
            self.angle += 360

    @staticmethod
    def _get_heading(angle: int) -> np.ndarray:
        rad = np.deg2rad(angle) - np.pi / 2
        return np.array([np.cos(rad), np.sin(rad)])

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
        self.inertia = np.array([0, 0], dtype=float)  # initial force
        self.angle = 0
        self.speed = PLAYER_SPEED
        self.cool_down = False
        self.last_shot_time = time()

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
                self.update_inertia()
            if user.get("fire"):
                self.shoot()
        self.accelerate()
        self.draw()
        self.missiles = None
        return self

    def accelerate(self):
        # apply friction
        self.inertia = np.multiply(self.inertia, FRICTION)
        self.coordinates = np.add(self.coordinates, self.inertia)

    def update_inertia(self):
        acceleration = np.multiply(Sprite._get_heading(self.angle), self.speed)
        for idx, value in enumerate(self.inertia):
            if value >= 1.5:
                self.inertia[idx] = 1.5
        self.inertia = np.add(self.inertia, acceleration)

    def shoot(self):
        head = self.coordinates[-1]
        if (time() - self.last_shot_time) > (1 / MISSILES_PER_SEC):
            self.cool_down = False
        if not self.cool_down:
            self.cool_down = True
            self.last_shot_time = time()
            return Missile(self.screen, self.angle, coordinates=head)


class Missile(Sprite):
    def __init__(self, screen, angle, coordinates=(0, 0), size=STAR_SIZE):
        super().__init__(screen, color=YELLOW, coordinates=(0, 0))
        self.angle = angle
        heading = Sprite._get_heading(self.angle)
        self.direction = np.multiply(heading, MISSILE_SPEED)
        self.coordinates = coordinates
        self.size = size

    def update(self, *args, **kwargs):
        self.coordinates = np.add(self.coordinates, self.direction).astype("int16")
        self.draw()
        return self

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
        if np.random.randint(0, 100):
            self.draw()
        return self

    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.coordinates, self.size)


class Particle(Sprite):
    def __init__(
        self, screen, coordinates=(0, 0), color=RED, particle_size=PARTICLE_SIZE
    ):
        super().__init__(screen, color=color, coordinates=coordinates)
        heading: np.ndarray = Sprite._get_heading(self.angle)
        self.direction = np.multiply(heading, 10)
        self.coordinates = coordinates
        self.color = color
        self.particle_size = particle_size

    def update(self, *args, **kwargs):
        self.coordinates = np.add(self.coordinates, self.direction).astype("int16")
        self.draw()
        return self

    def draw(self):
        pygame.draw.circle(
            self.screen, self.color, self.coordinates, self.particle_size
        )


class Explosion:
    def __init__(self, screen, coordinates):
        self.particles = [Particle(screen, coordinates) for _ in range(N_PARTICLES)]

    def explode(self):
        return self.particles
