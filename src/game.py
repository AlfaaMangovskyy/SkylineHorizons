import pygame
from static import *

pygame.init()
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.NOFRAME,
)
clock = pygame.time.Clock()

arena = Arena([
    Block(-7, 5, 14, 2),
    Block(7, 3, 2, 4),
    Spikes(-7, 5, 3, 0),
], [(5.5, 3.5)])

if pygame.joystick.get_count() > 0:
    arena.controller = Controller(pygame.joystick.Joystick(0), arena.player)

running = True
while running:

    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                running = False
                break
            elif e.key == pygame.K_s:
                if not arena.controller:
                    arena.player.jump()

        elif e.type == pygame.JOYBUTTONDOWN:
            if e.joy == arena.controller.joy.get_id():
                arena.controller.buttonDown(e.button)

        elif e.type == pygame.JOYBUTTONUP:
            if e.joy == arena.controller.joy.get_id():
                arena.controller.buttonUp(e.button)

        elif e.type == pygame.JOYAXISMOTION:
            if e.joy == arena.controller.joy.get_id():
                arena.controller.axisMotion(e.axis, round(e.value, 2))

    if not running: break

    if not arena.controller:
        keymap = pygame.key.get_pressed()
        if keymap[pygame.K_a]:
            arena.player.left()
        if keymap[pygame.K_d]:
            arena.player.right()
        if (not keymap[pygame.K_a]) and (not keymap[pygame.K_d]):
            arena.player.central()

    arena.tick()
    camX, camY = arena.getCamera()
    # print(arena.player.py) #

    screen.fill("#030303")

    pygame.draw.rect(
        screen, "#FFFFFF", #"#FF0000" if arena.player.grounded else #
        (
            (arena.player.x - 0.5) * arena.scale + WIDTH // 2 - camX,
            (arena.player.y - 0.5) * arena.scale + HEIGHT // 2 - camY,
            arena.scale, arena.scale,
        )
    )

    for object in arena.layout:
        if isinstance(object, Block):
            pygame.draw.rect(
                screen, "#FFFFFF",
                (
                    object.x * arena.scale + WIDTH // 2 - camX,
                    object.y * arena.scale + HEIGHT // 2 - camY,
                    object.w * arena.scale,
                    object.h * arena.scale,
                )
            )

        if isinstance(object, Spikes):
            if object.d == 0:
                pygame.draw.rect(
                    screen, "#FF0000",
                    (
                        object.x * arena.scale + WIDTH // 2 - camX,
                        object.y * arena.scale + HEIGHT // 2 - camY - 10,
                        object.l * arena.scale, 20,
                    )
                )
            else:
                pygame.draw.rect(
                    screen, "#FF0000",
                    (
                        object.x * arena.scale + WIDTH // 2 - camX - 10,
                        object.y * arena.scale + HEIGHT // 2 - camY,
                        20, object.l * arena.scale,
                    )
                )

    # pygame.draw.rect(
    #     screen, "#FF0000",
    #     (
    #         (arena.cambox[0] - arena.camW) * arena.scale + WIDTH // 2 - camX,
    #         (arena.cambox[1] - arena.camH) * arena.scale + HEIGHT // 2 - camY,
    #         arena.camW * arena.scale * 2, arena.camH * arena.scale * 2,
    #     ), 5,
    # )
    pygame.draw.circle(
        screen, "#FF0000",
        (
            WIDTH // 2,
            HEIGHT // 2,
        ), 5,
    )

    for checkpoint in arena.checkpoints:
        checkX = checkpoint[0] * arena.scale + WIDTH // 2 - camX
        checkY = checkpoint[1] * arena.scale + HEIGHT // 2 - camY
        pygame.draw.polygon(
            screen, "#00FF00",
            (
                (checkX - 25, checkY),
                (checkX, checkY - 25),
                (checkX + 25, checkY),
                (checkX, checkY + 25),
            )
        )

    pygame.display.update()
    clock.tick(FRAMERATE)