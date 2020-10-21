import numpy as np
import pygame
from config import *
from typing import Dict, Union, List
from random import choices, choice
from time import time
from utils import is_point
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Sprite:
    def __init__(self, screen, coordinates, color):
        self.screen = screen
        self.color = color
        self.coordinates = coordinates
        self.angle = np.random.randint(0, 360)
        self.display = True
        self.size = 1

    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.coordinates, self.size)

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

    def _polygon_collision(self) -> bool:
        if any(Sprite._is_out(point) for point in self.coordinates):
            self.display = False
            return True
        return False

    @staticmethod
    def _is_out(point: np.ndarray) -> bool:
        if (0 < point[0] < SCREEN_DIMS[0]) and (0 < point[1] < SCREEN_DIMS[1]):
            return False
        return True

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


class Missile(Sprite):
    def __init__(self, screen, angle, coordinates, size=STAR_SIZE):
        super().__init__(screen, coordinates, color=YELLOW)
        self.angle = angle
        heading = Sprite._get_heading(self.angle)
        self.direction = np.multiply(heading, MISSILE_SPEED)
        self.coordinates = coordinates
        self.size = size

    def update(self, *args, **kwargs):
        if Missile._is_out(self.coordinates):
            self.display = False
        if self.display:
            self.coordinates = np.add(self.coordinates, self.direction).astype("int16")
            self.draw()
        return self


class Star(Sprite):
    def __init__(self, screen, coordinates=np.array([0, 0]), size=STAR_SIZE):
        super().__init__(screen, coordinates, color=WHITE)
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


class Particle(Sprite):
    def __init__(
        self, screen, coordinates=np.array([0, 0]), color=RED, size=PARTICLE_SIZE
    ):
        super().__init__(screen, coordinates=coordinates, color=color)
        heading: np.ndarray = Sprite._get_heading(self.angle)
        self.direction = np.multiply(heading, 10)
        self.coordinates = coordinates
        self.color = color
        self.size = size

    def update(self, *args, **kwargs):
        if Particle._is_out(self.coordinates):
            self.display = False
        if self.display:
            self.coordinates = np.add(self.coordinates, self.direction).astype("int16")
            self.draw()
        return self


class Explosion:
    def __init__(self, screen, coordinates):
        self.particles = [Particle(screen, coordinates) for _ in range(N_PARTICLES)]

    def explode(self):
        return self.particles


class SolidSprite(Sprite):
    def __init__(self, screen, coordinates, color):
        super().__init__(screen, coordinates=coordinates, color=color)
        self.inertia = np.array([0, 0], dtype=float)
        self.angle = 0
        self.dead = False
        self.dangerous = []

    def accelerate(self) -> None:
        if (self.inertia == 0).all():
            return
        self.coordinates = np.add(self.coordinates, self.inertia)

    def check_collision(self, sprites:Sprite):
        dangerous_objects = [sprite for sprite in sprites if type(sprite) in self.dangerous]
        polygon = Polygon(self.coordinates)
        for obj in dangerous_objects:
            coords = obj.coordinates
            if is_point(coords): # if coordinates is a single point than do not iterate
                self.check_point(coords, polygon)
                continue
            for point in coords:
                self.check_point(point, polygon)
            if self.dead:
                return

    def check_point(self, point, polygon):
        p = Point(point)
        if polygon.contains(p):
            self.dead = True

    def draw(self):
        pygame.draw.polygon(self.screen, self.color, self.coordinates, 1)


class Enemy(SolidSprite):
    def __init__(self, screen, coordinates=np.array([0, 0]), color=WHITE, size=ENEMY_SIZE):
        super().__init__(screen, coordinates=coordinates, color=color)
        self.size = size
        self.radius = self.size // 2
        self.coordinates = self.init_polygon(center=coordinates)
        self.inertia = np.random.randint(low=-2, high=2, size=(2), dtype="int16")
        self.dangerous = [Missile]

    def init_polygon(self, center):
        n_points = choice([4, 5, 6, 10])
        points = []
        angle = 0
        radians = np.deg2rad(angle)
        for _ in range(n_points):
            xpos = center[0] + self.radius * np.cos(radians)
            ypos = center[1] + self.radius * np.sin(radians)
            point = [int(xpos), int(ypos)]
            points.append(point)
            angle += (360 // n_points) - 1
            radians = np.deg2rad(angle)
        return np.array(points)

    def update(self, *args, **kwargs):
        self._polygon_collision()
        self.check_collision(kwargs["sprites"])
        if self.display:
            self.accelerate()
            self.draw()
        else:
            self.dead = True
        return self


class Spawner():
    def __init__(self, screen, n_enemies:int=10):
        self.screen = screen
        self.size = ENEMY_SIZE
        self.n_enemies = n_enemies
        self.game_map = self.create_map()
        if len(self.game_map) <= self.n_enemies:
            raise ValueError("Too many enemies for their given size\nEither reduce size or number of enemies")
        
    def create_map(self):
        game_map : List[List[int, int]] = [] # store enemy positions here
        # compute all possible x and y coordinates and create points from them
        xs = np.linspace(self.size, WIDTH - self.size, WIDTH // self.size - 1, dtype="int16")
        ys = np.linspace(self.size, HEIGHT - self.size, HEIGHT // self.size - 1, dtype="int16")
        # compute collision square values
        min_x, min_y = np.subtract(CENTER, self.size)
        max_x, max_y = np.add(CENTER, self.size)
        for xpos in xs:
            for ypos in ys:
                # filter out possible positions that could collide with player spawn
                if ((xpos < min_x) or (xpos > max_x)) or ((ypos < min_y) or (ypos > max_y)):
                    game_map.append([xpos, ypos])
        return game_map

    def spawn(self):
        spawns = choices(self.game_map, k=self.n_enemies)
        return [Enemy(self.screen, spawn) for spawn in spawns]


class Ship(SolidSprite):
    def __init__(self, screen, coordinates=np.array(PLAYER_COORD), color=WHITE):
        super().__init__(screen, coordinates=coordinates, color=color)
        self.inertia = np.array([0, 0], dtype=float)  # initial force
        self.angle = 0
        self.speed = PLAYER_SPEED
        self.max_inertia = PLAYER_MAX_INERTIA
        self.cool_down = False
        self.last_shot_time = time()
        self.dangerous = [Enemy]

    def update(self, user: Dict[str, Union[bool, int]] = {}, *args, **kwargs):
        """Update information based on environment and user input

        Args:
            user (Dict[str, Union[bool, int]], optional): User input. Defaults to {}.

        Returns:
            Ship: applies changes on screen and returns self object for reuse in next iteration
        """
        self._polygon_collision()
        self.check_collision(kwargs["sprites"])
        if self.display:
            if user:
                if user.get("rotate"):
                    angle = user["rotate"]
                    self.rotate(angle)
                if user.get("push"):
                    self.update_inertia()
                if user.get("fire"):
                    self.shoot()
            self.inertia = np.multiply(self.inertia, FRICTION)
            self.accelerate()
            self.draw()
        else:
            self.dead = True
        return self

    def update_inertia(self) -> None:
        acceleration = np.multiply(Sprite._get_heading(self.angle), self.speed)
        self.inertia = np.add(self.inertia, acceleration)
        for idx, value in enumerate(self.inertia):
            if self.max_inertia <= value:
                self.inertia[idx] = self.max_inertia
            if value <= -self.max_inertia:
                self.inertia[idx] = -self.max_inertia

    def shoot(self) -> Sprite:
        head = self.coordinates[-1]
        if (time() - self.last_shot_time) > (1 / MISSILES_PER_SEC):
            self.cool_down = False
        if not self.cool_down:
            self.cool_down = True
            self.last_shot_time = time()
            return Missile(self.screen, self.angle, coordinates=head)