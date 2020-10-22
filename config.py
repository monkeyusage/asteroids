# COLORS
BLACK = (0, 0, 0)  # Black
WHITE = (255, 255, 255)  # White
YELLOW = (255, 255, 0)  # Yellow
RED = (255, 0, 0)
# SCREEN
WIDTH, HEIGHT = (1000, 800)  # Screen dims
SCREEN_DIMS = (WIDTH, HEIGHT)
CENTER = (WIDTH // 2, HEIGHT // 2)
# GAME OPTIONS
FPS = 60
PLAYER_SPEED = 1.01
PLAYER_COORD = [
    (CENTER[0] - 10, CENTER[1]),  # base 1
    (CENTER[0] + 10, CENTER[1]),  # base 2
    (CENTER[0], CENTER[1] - 25),  # head
]
PLAYER_SENSITIVITY = 4
PLAYER_MAX_INERTIA = 3
MISSILE_SPEED = 10
MISSILES_PER_SEC = 10
ENEMY_SIZE = 100
FRICTION = 0.99
STAR_SIZE = 2
PARTICLE_SIZE = 2
N_STARS = 300
N_PARTICLES = 10
