import pygame
import numpy as np
from time import sleep, time
from config import *
from typing import Dict, Union
from utils import sleep_fps
from sprites import Ship, Sprite, Star, Explosion, Spawner
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", default=False)
args = parser.parse_args()
DEBUG = args.debug

screen = pygame.display.set_mode(SCREEN_DIMS)  # Setting Screen
pygame.display.set_caption("Asteroids")  # Window Name
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("sounds/tetris.mp3")
pygame.mixer.music.play(-1, 0.0)
screen.fill(BLACK)

stars = [Star(screen) for _ in range(N_STARS)]
ship = Ship(screen)
enemies = Spawner(screen).spawn()
sprites = [ship, *enemies] + stars
solid_sprites = [ship, *enemies]

assert all(
    [isinstance(obj, Sprite) for obj in sprites]
), "Inserted non sprite object into sprite list"

pygame.key.set_repeat(2, 2)
while True:
    t0 = time()
    user = {}
    # catch user events
    events = pygame.event.get()  # collect key presses
    if any(event.type == pygame.QUIT for event in events):
        pygame.quit()
        break
    for event in events:
        if event.type == pygame.KEYDOWN:  # collect actions
            if event.key == pygame.K_RIGHT:
                user["rotate"] = PLAYER_SENSITIVITY
            if event.key == pygame.K_LEFT:
                user["rotate"] = -PLAYER_SENSITIVITY
            if event.key == pygame.K_UP:
                user["push"] = True
            if event.key == pygame.K_SPACE:
                missile = ship.shoot()
                if missile:
                    sprites.append(missile)
    # update screen according to changes
    screen.fill(BLACK)
    sprites = [
        sprite.update(user) for sprite in sprites
    ]  # apply update() to all sprites
    if not ship.display:
        ship = Ship(screen)
        sprites.append(ship)
        solid_sprites.append(ship)
    
    updated_solids = []
    for sprite in solid_sprites:
        if sprite.dead:
            coordinates = Sprite._get_center(sprite.coordinates)
            particles = Explosion(screen, coordinates).explode()
            sprites += particles
        else:
            updated_solids.append(sprite)
    solid_sprites = updated_solids
    sprites = [sprite for sprite in sprites if sprite.display]
    sleep_fps(t0)  # control FPS
    pygame.display.update()
