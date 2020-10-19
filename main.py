import pygame
import numpy as np
from time import sleep, time
from config import BACKGROUD_COLOR, PLAYER_COLOR, WIDTH, HEIGHT, SCREEN_DIMS, FPS
from typing import Dict, Union

screen = pygame.display.set_mode(SCREEN_DIMS)  # Setting Screen
pygame.display.set_caption("Asteroids")  # Window Name
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("sounds/tetris.mp3")
pygame.mixer.music.play(-1, 0.0)
screen.fill(BACKGROUD_COLOR)


class Sprite:
    def __init__(self):
        pass

    def update(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def _rotate_polygon(points, center=(0, 0), degrees=0) -> np.ndarray:
        angle = np.deg2rad(degrees)
        return np.array([Sprite._rotate_point(point, center, angle) for point in points])

    @staticmethod
    def _rotate_point(point, center=(0,0), angle=0):
        return np.array([
            center[0] + (point[0] - center[0])*np.cos(angle) - (point[1] - center[1])*np.sin(angle),
            center[1] + (point[0] - center[0])*np.sin(angle) + (point[1] - center[1])*np.cos(angle),
        ])

    @staticmethod
    def _get_center(coordinates: np.ndarray) -> np.ndarray:
        return coordinates.mean(axis=0).astype("int16")


class Ship(Sprite):
    def __init__(self):
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.color = PLAYER_COLOR
        self.coordinates = np.array(
            [
                (self.center[0] - 10, self.center[1]),  # base 1
                (self.center[0] + 10, self.center[1]),  # base 2
                (self.center[0], self.center[1] - 25),  # head
            ]
        )
        self.velocity = np.array([0, 0])  # initial force
        self.display = False

    def draw(self):
        pygame.draw.polygon(screen, self.color, self.coordinates, 1)

    def update(self, user:Dict[str, Union[bool, int]]={}):
        """Update information based on environment and user input

        Args:
            user (Dict[str, Union[bool, int]], optional): User input. Defaults to {}.

        Returns:
            Ship: applies changes on screen and returns self object for reuse in next iteration
        """
        if user:
            if angle:= user.get("rotate"):
                self.rotate(angle)
            if user.get("push"):
                self.move()
        self.draw()
        return self
    
    def move(self):
        pass
    
    def rotate(self, angle:int):
        center : np.ndarray = Ship._get_center(self.coordinates) # np.array([int, int])
        self.coordinates = Ship._rotate_polygon(
            self.coordinates, center=center, degrees=angle
        )

def sleep_fps(orig_time: float, frame_time: float = 1 / FPS) -> None:
    final_time = time()
    elapsed_time = final_time - orig_time
    if elapsed_time < frame_time:
        sleep(frame_time - elapsed_time)


ship = Ship()
sprites = [ship]
assert all([isinstance(obj, Sprite) for obj in sprites]), "Inserted non sprite object into sprite list"

pygame.key.set_repeat(10,10)
while True:
    t0 = time()
    user = {}
    # catch user events
    events = pygame.event.get()
    if any(event.type == pygame.QUIT for event in events):
            pygame.quit()
            break
    for event in events:
        if event.type == pygame.KEYDOWN:  # collect key presses and actions
            if event.key == pygame.K_RIGHT:
                user["rotate"] = 5
            if event.key == pygame.K_LEFT:
                user["rotate"] = -5
            if event.key == pygame.K_UP:
                user["push"] = True
    # update screen according to changes
    screen.fill(BACKGROUD_COLOR)
    sprites = [sprite.update(user) for sprite in sprites]  # apply update to all sprites
    sleep_fps(t0)  # control FPS
    pygame.display.update()