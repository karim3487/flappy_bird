import random
import pygame
from pygame.locals import *


def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 900))
    screen.blit(floor_surface, (floor_x_pos + 576, 900))


def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(1000, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(1000, random_pipe_pos - 300))
    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


def delete_pipe(pipes):
    for pipe in pipes:
        if pipe.right < -10:
            pipes.pop(pipes.index(pipe))


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False

    if bird_rect.bottom > 900 or bird_rect.top < -100:
        hit_sound.play()
        return False

    return True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect


def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255 ,255))
        score_rect = score_surface.get_rect(center=(288, 100))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(288, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(288, 850))
        screen.blit(high_score_surface, high_score_rect)


def update_score(s, h_s):
    if s > h_s:
        h_s = s
        f = open('records.dat', 'w')
        f.write(str(h_s))
    return h_s


def get_record():
    f = open('records.dat', 'r')
    rec = f.read()
    if rec == '':
        rec = 0
    return int(rec)


screen_width = 576
screen_height = 1024

pygame.mixer.pre_init(channels=1, buffer=512)
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

icon = pygame.image.load('favicon.ico')
pygame.display.set_icon(icon)
game_font = pygame.font.Font('04B_19.TTF', 40)

clock = pygame.time.Clock()

# Game variables
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
high_score = get_record()
score_countdown = 200

bg_surface = [pygame.image.load('assets/background-day.png').convert(),
              pygame.image.load('assets/background-night.png').convert()]
bg_surface = [pygame.transform.scale2x(bg_surface[0]), pygame.transform.scale2x(bg_surface[1])]

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0

bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-downflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-midflap.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-upflap.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(100, 512))

BIRD_FLAP = pygame.USEREVENT
pygame.time.set_timer(BIRD_FLAP, 200)

# bird_surface = pygame.image.load('assets/bluebird-midflap.png').convert()
# bird_surface = pygame.transform.scale2x(bird_surface)
# bird_rect = bird_surface.get_rect(center=(100, 512))

pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWN_PIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWN_PIPE, 2000)
pipe_height = [400, 500, 600, 700, 750]

game_over_surface = pygame.image.load('assets/message.png').convert_alpha()
game_over_surface = pygame.transform.scale2x(game_over_surface)
game_over_rect = game_over_surface.get_rect(center=(screen_width / 2, screen_height / 2))

# bg selector
bg_selector = random.choice(bg_surface)

# sound
flap_sound = pygame.mixer.Sound('sound/wing.wav')
die_sound = pygame.mixer.Sound('sound/die.wav')
hit_sound = pygame.mixer.Sound('sound/hit.wav')
point_sound = pygame.mixer.Sound('sound/point.wav')
swoosh_sound = pygame.mixer.Sound('sound/swoosh.wav')
wing_sound = pygame.mixer.Sound('sound/swoosh.wav')

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_movement = 0
                bird_movement -= 9
                flap_sound.play()
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, 312)
                bird_movement = 0
                score = 0

        if event.type == SPAWN_PIPE:
            pipe_list.extend(create_pipe())
            # flag += 1
            # if flag > 2:
            #     score += 1

        if event.type == BIRD_FLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            bird_surface, bird_rect = bird_animation()
    screen.blit(bg_selector, (0, 0))

    if game_active:
        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        delete_pipe(pipe_list)

        # Score
        score_display('main_game')
        score_countdown -= 1
        if score_countdown <= 0:
            point_sound.play()
            score += 1
            score_countdown = 200
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        get_record()
        score_display('game_over')

    # Floor
    floor_x_pos -= 2
    draw_floor()
    if floor_x_pos == -576:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)

pygame.quit()
