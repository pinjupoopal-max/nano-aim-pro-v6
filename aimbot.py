
import pygame
import random
import math

pygame.init()

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("NANO AIM PRO V6")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)
title = pygame.font.Font(None, 34)

BG = (10, 13, 27)
PANEL = (25, 32, 55)
BLUE = (0, 180, 255)
CYAN = (0, 255, 220)
GREEN = (0, 255, 90)
RED = (255, 55, 75)
WHITE = (245, 245, 255)
YELLOW = (255, 220, 30)
GRAY = (90, 100, 120)
ORANGE = (255, 130, 20)

player = [450.0, 300.0]

sensitivity = 5
fps_limit = 60

aimbot = False
esp = False
menu_open = True

joy_active = False
shoot_active = False
slider_active = False

joy_x, joy_y = 790, 490
joy_radius = 65
joy_pos = [joy_x, joy_y]

shoot_x, shoot_y = 700, 300
shoot_radius = 48

score = 0
last_shot = 0
last_auto_shot = 0

enemies = []
bullets = []
particles = []
respawns = []

def new_enemy():
    return [
        random.randint(270, 630),
        random.randint(50, 550),
        random.choice([-2, 2]),
        random.choice([-2, 2])
    ]

for i in range(4):
    enemies.append(new_enemy())


def draw_text(msg, x, y, color=WHITE, f=None):
    screen.blit(
        (f or font).render(str(msg), True, color),
        (x, y)
    )


def draw_panel():
    pygame.draw.rect(
        screen, PANEL, (5, 5, 230, 440),
        border_radius=15
    )
    pygame.draw.rect(
        screen, BLUE, (5, 5, 230, 440),
        2, border_radius=15
    )


def draw_toggle(name, y, active):
    color = GREEN if active else RED

    pygame.draw.rect(
        screen, (40, 50, 70),
        (15, y, 210, 40),
        border_radius=9
    )

    pygame.draw.circle(
        screen, color, (195, y+20), 9
    )

    draw_text(
        name + (" ON" if active else " OFF"),
        27, y+11
    )


def change_slider(x):
    global sensitivity

    sensitivity = max(
        1, min(15, int((x-15)/14)+1)
    )


def touch_down(x, y):
    global aimbot, esp, menu_open
    global joy_active, joy_pos, slider_active
    global fps_limit, shoot_active

    # LEFT MOD MENU
    if x < 240:

        if menu_open:

            if 100 <= y <= 140:
                aimbot = not aimbot
                return

            if 150 <= y <= 190:
                esp = not esp
                return

            if 235 <= y <= 270:
                slider_active = True
                change_slider(x)
                return

            if 315 <= y <= 355:
                if x < 85:
                    fps_limit = 30
                elif x < 155:
                    fps_limit = 60
                else:
                    fps_limit = 120
                return

            if 390 <= y <= 430:
                menu_open = False
                return

        elif 15 <= y <= 60:
            menu_open = True
            return

        return

    # MANUAL SHOOT BUTTON
    distance = math.hypot(
        x-shoot_x, y-shoot_y
    )

    if distance <= shoot_radius:
        shoot_active = True
        return

    # RIGHT JOYSTICK
    if x > 680 and y > 380:
        joy_active = True
        joy_pos = [x, y]


def touch_move(x, y):
    global joy_pos

    if joy_active:

        dx = x - joy_x
        dy = y - joy_y

        distance = math.hypot(dx, dy)

        if distance > joy_radius:
            dx = dx / distance * joy_radius
            dy = dy / distance * joy_radius

        joy_pos = [
            joy_x+dx,
            joy_y+dy
        ]

    if slider_active:
        change_slider(x)


def touch_up():
    global joy_active, slider_active
    global joy_pos, shoot_active

    joy_active = False
    shoot_active = False
    slider_active = False
    joy_pos = [joy_x, joy_y]


def create_explosion(x, y):

    for i in range(20):

        angle = random.uniform(0, math.pi*2)
        speed = random.uniform(2, 7)

        particles.append([
            float(x),
            float(y),
            math.cos(angle)*speed,
            math.sin(angle)*speed,
            random.randint(15, 30)
        ])


def create_bullet(target):

    dx = target[0] - player[0]
    dy = target[1] - player[1]

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    speed = 13

    bullets.append([
        float(player[0]),
        float(player[1]),
        dx/distance*speed,
        dy/distance*speed
    ])


def kill_enemy(enemy):

    global score

    create_explosion(enemy[0], enemy[1])

    enemies.remove(enemy)

    # RESPAWN AFTER 3 SECONDS
    respawns.append(
        (pygame.time.get_ticks()+3000, new_enemy())
    )

    score += 1


running = True

while running:

    clock.tick(fps_limit)
    screen.fill(BG)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.FINGERDOWN:
            touch_down(
                int(event.x*W),
                int(event.y*H)
            )

        elif event.type == pygame.FINGERMOTION:
            touch_move(
                int(event.x*W),
                int(event.y*H)
            )

        elif event.type == pygame.FINGERUP:
            touch_up()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                touch_down(*event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:
                touch_move(*event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                touch_up()

    # PLAYER MOVEMENT
    if joy_active:

        dx = joy_pos[0]-joy_x
        dy = joy_pos[1]-joy_y

        player[0] += dx/joy_radius*sensitivity
        player[1] += dy/joy_radius*sensitivity

    player[0] = max(250, min(650, player[0]))
    player[1] = max(20, min(580, player[1]))

    # ENEMY RESPAWN AFTER 3 SECONDS
    now = pygame.time.get_ticks()

    for respawn in respawns[:]:

        if now >= respawn[0]:

            enemies.append(respawn[1])
            respawns.remove(respawn)

    # ENEMY MOVEMENT
    for e in enemies:

        e[0] += e[2]
        e[1] += e[3]

        if e[0] < 250 or e[0] > 650:
            e[2] *= -1

        if e[1] < 20 or e[1] > 580:
            e[3] *= -1

    # AIMBOT
    if aimbot and enemies:

        target = min(
            enemies,
            key=lambda e: math.hypot(
                e[0]-player[0],
                e[1]-player[1]
            )
        )

        pygame.draw.line(
            screen, YELLOW,
            (int(player[0]), int(player[1])),
            (int(target[0]), int(target[1])), 2
        )

        pygame.draw.circle(
            screen, YELLOW,
            (int(target[0]), int(target[1])), 26, 2
        )

        if now-last_auto_shot > 1000:

            distance = math.hypot(
                target[0]-player[0],
                target[1]-player[1]
            )

            if distance < 450:

                kill_enemy(target)
                last_auto_shot = now

    # MANUAL SHOOTING
    if shoot_active and enemies:

        if now-last_shot > 350:

            target = min(
                enemies,
                key=lambda e: math.hypot(
                    e[0]-player[0],
                    e[1]-player[1]
                )
            )

            distance = math.hypot(
                target[0]-player[0],
                target[1]-player[1]
            )

            if distance <= 450:

                create_bullet(target)
                last_shot = now

    # BULLET MOVEMENT AND HIT
    for bullet in bullets[:]:

        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

        hit = False

        for e in enemies[:]:

            distance = math.hypot(
                bullet[0]-e[0],
                bullet[1]-e[1]
            )

            if distance < 21:

                kill_enemy(e)
                hit = True
                break

        if hit:

            bullets.remove(bullet)

        elif (
            bullet[0] < 0 or bullet[0] > W
            or bullet[1] < 0 or bullet[1] > H
        ):

            bullets.remove(bullet)

    # DRAW BULLETS
    for bullet in bullets:

        pygame.draw.circle(
            screen, YELLOW,
            (int(bullet[0]), int(bullet[1])), 6
        )

        pygame.draw.circle(
            screen, ORANGE,
            (int(bullet[0]), int(bullet[1])), 10, 2
        )

    # EXPLOSION PARTICLES
    for p in particles[:]:

        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1

        if p[4] <= 0:
            particles.remove(p)
            continue

        radius = max(1, int(p[4]/5))

        pygame.draw.circle(
            screen,
            random.choice([
                YELLOW, ORANGE, RED, WHITE
            ]),
            (int(p[0]), int(p[1])),
            radius
        )

    # ENEMIES AND ESP
    for e in enemies:

        pygame.draw.circle(
            screen, RED,
            (int(e[0]), int(e[1])), 17
        )

        if esp:

            distance = int(math.hypot(
                e[0]-player[0],
                e[1]-player[1]
            ))

            pygame.draw.circle(
                screen, CYAN,
                (int(e[0]), int(e[1])), 25, 2
            )

            draw_text(
                str(distance)+" px",
                int(e[0])+20,
                int(e[1])-30,
                CYAN
            )

    # PLAYER
    pygame.draw.circle(
        screen, GREEN,
        (int(player[0]), int(player[1])), 18
    )

    # JOYSTICK
    pygame.draw.circle(
        screen, GRAY,
        (joy_x, joy_y), joy_radius, 3
    )

    pygame.draw.circle(
        screen, BLUE,
        (int(joy_pos[0]), int(joy_pos[1])), 23
    )

    # SHOOT BUTTON
    shoot_color = RED if shoot_active else (180, 45, 60)

    pygame.draw.circle(
        screen, shoot_color,
        (shoot_x, shoot_y), shoot_radius
    )

    pygame.draw.circle(
        screen, WHITE,
        (shoot_x, shoot_y), shoot_radius, 3
    )

    draw_text(
        "SHOOT",
        shoot_x-28,
        shoot_y-9,
        WHITE
    )

    # MOD MENU
    if menu_open:

        draw_panel()

        draw_text(
            "NANO AIM PRO",
            20, 25, CYAN, title
        )

        draw_text("GAME SETTINGS", 20, 65)

        draw_toggle("AIMBOT", 100, aimbot)
        draw_toggle("ESP", 150, esp)

        draw_text(
            "SENSITIVITY: "+str(sensitivity),
            15, 205
        )

        pygame.draw.rect(
            screen, WHITE,
            (15, 245, 210, 7),
            border_radius=5
        )

        pygame.draw.circle(
            screen, CYAN,
            (15+int(sensitivity/15*210), 248),
            11
        )

        draw_text("FPS SETTINGS", 15, 285)

        for x, value in [(15,30),(85,60),(155,120)]:

            color = GREEN if fps_limit == value else BLUE

            pygame.draw.rect(
                screen, color,
                (x, 315, 65, 38),
                border_radius=7
            )

            draw_text(str(value), x+20, 326)

        pygame.draw.rect(
            screen, RED,
            (15, 390, 210, 40),
            border_radius=9
        )

        draw_text("CLOSE MENU", 75, 401)

    else:

        pygame.draw.rect(
            screen, BLUE,
            (15, 20, 210, 40),
            border_radius=9
        )

        draw_text("OPEN MOD MENU", 40, 31)

    # INFORMATION
    draw_text("SCORE: "+str(score), 740, 20, CYAN)
    draw_text("FPS: "+str(int(clock.get_fps())), 740, 50)
    draw_text("BULLETS: "+str(len(bullets)), 740, 80)
    draw_text("NANO AIM PRO V6", 350, 15, CYAN)

    pygame.display.flip()

pygame.quit()

