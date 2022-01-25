import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH = 576
SCREEN_HEIGHT = 800
IMAGE_SRC = "Assets/sprites"
GRAVITY = 0.20

score = 0
hi_score = 0

with open("high_score.txt", "r") as F:
    hi_score = int(F.readline())

game_state = True
bird_movement = 0

game_font = pygame.font.Font('Assets/04B_19__.ttf', 30)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird ~ Mo (Github: @1Hanif1")

icon = pygame.image.load("Assets/favicon.ico")
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

bg_image = pygame.image.load(f"{IMAGE_SRC}/background-day.png").convert()
bg_image = pygame.transform.scale(bg_image, size=(SCREEN_WIDTH, SCREEN_HEIGHT))

floor_image = pygame.image.load(f"{IMAGE_SRC}/base.png").convert()
floor_image = pygame.transform.scale(floor_image, size=(
    SCREEN_WIDTH, 100))
floor_x = 0

bird_up = pygame.image.load(
    f"{IMAGE_SRC}/bluebird-upflap.png").convert_alpha()
bird_mid = pygame.image.load(
    f"{IMAGE_SRC}/bluebird-midflap.png").convert_alpha()
bird_down = pygame.image.load(
    f"{IMAGE_SRC}/bluebird-downflap.png").convert_alpha()

bird_frames = [bird_up, bird_mid, bird_down]
bird_index = 0

bird_image = bird_frames[bird_index]
bird_image = pygame.transform.scale(bird_image, (50, 40))
bird_rect = bird_image.get_rect(center=(100, 400))

pipe_image = pygame.image.load(f"{IMAGE_SRC}/pipe-green.png")
pipe_image = pygame.transform.scale2x(pipe_image)
pipe_list = []
pipe_height = [500, 600, 700]

game_main_screen = pygame.image.load(
    f"{IMAGE_SRC}/message.png").convert_alpha()
game_main_screen = pygame.transform.scale(game_main_screen, (400, 500))
game_main_screen_rect = game_main_screen.get_rect(center=(288, 400))

# Sounds
AUDIO_SRC = "Assets/audio"
flap = pygame.mixer.Sound(f"{AUDIO_SRC}/wing.wav")
die = pygame.mixer.Sound(f"{AUDIO_SRC}/die.wav")
hit = pygame.mixer.Sound(f"{AUDIO_SRC}/hit.wav")
point = pygame.mixer.Sound(f"{AUDIO_SRC}/point.wav")


SPAWNPIPE_EVENT = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE_EVENT, 2000)

BIRDFLAP_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP_EVENT, 100)

UPDATE_SCORE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(UPDATE_SCORE_EVENT, 2000)


def score_display(state):
    if state:
        score_board = game_font.render(f"{score}", True, (255, 255, 255))
        score_rect = score_board.get_rect(center=(288, 100))
        screen.blit(score_board, score_rect)
    else:
        score_board = game_font.render(f"{score}", True, (255, 255, 255))
        score_rect = score_board.get_rect(center=(288, 100))
        screen.blit(score_board, score_rect)

        high_score = game_font.render(
            f"High Score: {hi_score}", True, (255, 255, 255))
        score_rect = high_score.get_rect(center=(288, 685))
        screen.blit(high_score, score_rect)

        global UPDATE_SCORE_EVENT
        UPDATE_SCORE_EVENT = None


def draw_floor():
    screen.blit(floor_image, (floor_x, (SCREEN_HEIGHT - 100)))
    screen.blit(floor_image, (floor_x + 576, (SCREEN_HEIGHT - 100)))


def create_pipe():
    pipe_position = random.choice(pipe_height)

    lower_pipe = pipe_image.get_rect(
        midtop=(SCREEN_WIDTH + 100, pipe_position))

    upper_pipe = pipe_image.get_rect(
        midbottom=(SCREEN_WIDTH + 100, pipe_position - 300))

    return lower_pipe, upper_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            screen.blit(pipe_image, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_image, False, True)
            screen.blit(flip_pipe, pipe)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit.play()
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= SCREEN_HEIGHT - 100:
        die.play()
        return False

    return True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement*3, 1)
    return new_bird


def update_high_score():
    global hi_score

    if hi_score > score:
        return

    hi_score = score
    with open("high_score.txt", "w") as f:
        f.write(str(hi_score))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state:
                bird_movement = 0
                bird_movement -= 8
                flap.play()

            if event.key == pygame.K_SPACE and not game_state:
                game_state = True
                pipe_list.clear()
                bird_rect.center = (100, 400)
                bird_movement = 0
                score = 0
                UPDATE_SCORE_EVENT = pygame.USEREVENT + 2
                pygame.time.set_timer(UPDATE_SCORE_EVENT, 2000)

        if event.type == SPAWNPIPE_EVENT:
            pipe_list.extend(create_pipe())

        if event.type == UPDATE_SCORE_EVENT:
            score += 1
            point.play()

        if event.type == BIRDFLAP_EVENT:
            bird_index = 0 if bird_index == 2 else bird_index + 1
            bird_image = bird_frames[bird_index]
            bird_image = pygame.transform.scale(bird_image, (50, 40))
            bird_rect = bird_image.get_rect(center=(100, bird_rect.centery))

    screen.blit(bg_image, (0, 0))

    if game_state:
        rotated_bird = rotate_bird(bird_image)
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_state = check_collision(pipe_list)

        score_display(game_state)

        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
    else:
        screen.blit(game_main_screen, game_main_screen_rect)
        score_display(game_state)
        update_high_score()

    draw_floor()
    pygame.display.update()

    if floor_x <= -576:
        floor_x = 0
    else:
        floor_x -= 2

    clock.tick(60)
