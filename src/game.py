import pygame
from static import *

pygame.init()
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.NOFRAME,
)
clock = pygame.time.Clock()

arena = Arena([
    Block(-7, 5, 14, 2)
])

running = True
while running:

    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                running = False
                break
            elif e.key == pygame.K_s:
                arena.player.jump()

    if not running: break

    keymap = pygame.key.get_pressed()
    if keymap[pygame.K_a]:
        arena.player.left()
    if keymap[pygame.K_d]:
        arena.player.right()
    if (not keymap[pygame.K_a]) and (not keymap[pygame.K_d]):
        arena.player.central()

    arena.tick()
    camX, camY = arena.getCamera()

    screen.fill("#030303")

    pygame.draw.rect(
        screen, "#FF0000" if arena.player.grounded else "#FFFFFF",
        (
            (arena.player.x - 0.5) * arena.scale + WIDTH // 2 - camX,
            (arena.player.y - 0.5) * arena.scale + HEIGHT // 2 - camY,
            arena.scale, arena.scale,
        )
    )

    for block in arena.layout:
        pygame.draw.rect(
            screen, "#FFFFFF",
            (
                block.x * arena.scale + WIDTH // 2 - camX,
                block.y * arena.scale + HEIGHT // 2 - camY,
                block.w * arena.scale,
                block.h * arena.scale,
            )
        )

    pygame.draw.rect(
        screen, "#FF0000",
        (
            (arena.cambox[0] - arena.camW) * arena.scale + WIDTH // 2 - camX,
            (arena.cambox[1] - arena.camH) * arena.scale + HEIGHT // 2 - camY,
            arena.camW * arena.scale * 2, arena.camH * arena.scale * 2,
        ), 5,
    )

    pygame.display.update()
    clock.tick(FRAMERATE)