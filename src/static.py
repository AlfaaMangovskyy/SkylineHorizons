import math
import random

WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60

DIAGONAL = 1 / math.sqrt(2)

def approx(a : float, b : float, diff : float):
    return a - diff <= b <= a + diff
def sign(self, a : float) -> int:
    if a == 0: return 0
    return a // abs(a)

class Block:
    def __init__(self, x : float, y : float, w : float, h : float):
        self.x, self.y = x, y
        self.w, self.h = w, h

    def collides(self, other) -> tuple[bool, bool]:
        """
        Corrects the player's position on collision.
        Returns two booleans: one for overall collision, one for top collision.
        """
        if not isinstance(other, Player): return

        collision = False
        topCollision = False
        if other.x - 0.5 <= self.x <= other.x + 0.5 and self.y <= other.y <= self.y + self.h:
            other.x = self.x - 0.5
            collision = True
        if other.x - 0.5 <= self.x + self.w <= other.x + 0.5 and self.y <= other.y <= self.y + self.h:
            other.x = self.x + self.w + 0.5
            collision = True
        if other.y - 0.5 <= self.y <= other.y + 0.5 and self.x <= other.x <= self.x + self.w:
            other.y = self.y - 0.5
            collision = True
            topCollision = True
        if other.y - 0.5 <= self.y + self.h <= other.y + 0.5 and self.x <= other.x <= self.x + self.w:
            other.y = self.y + self.h + 0.5
            collision = True

        return collision, topCollision

class Spikes:
    def __init__(self, x : float, y : float, l : float, d : int = 0):
        # d = 1: Horizontal Spikes
        # d = 2: Vertical Spikes
        self.x, self.y = x, y
        self.l = l
        self.d = d

    def collides(self, other) -> tuple[bool, bool]:
        if not isinstance(other, Player): return

        if self.d == 0:
            collision = self.x <= other.x + 0.5 and self.x + self.l >= other.x - 0.5 and other.y - 0.5 <= self.y <= other.y + 0.5
        else:
            collision = self.y <= other.y + 0.5 and self.y + self.l >= other.y - 0.5 and other.x - 0.5 <= self.x <= other.x + 0.5

        if collision:
            other.eliminate()

        return collision, False

class Player:
    def __init__(self, arena, x : float = 0.0, y : float = 0.0, nickname : str = "???"):
        self.x, self.y = x, y
        self.arena : Arena | None = arena
        self.nickname = nickname

        self.gravity : float = 0.35
        self.speed : float = 0.15

        self.checkpoint : list[float, float] = [0.0, 0.0]

        self.reset()

    def reset(self):
        self.isGravity : bool = True

        self.grounded : bool = False
        self.coyote : int = 0
        self.jumpTimer : int = 0
        self.doubleJump : bool = False
        self.respawnTimer : int = 0

        self.direction : int = 0
        # self.controller : Controller | None = None #

        self.px : float = 0.0
        self.py : float = 0.0

    def eliminate(self):
        self.reset()
        self.x = self.checkpoint[0]
        self.y = self.checkpoint[1]
        self.arena.cameraShake(1.5, round(FRAMERATE * 0.5))

    def moveX(self, deltaX : float):
        self.x += deltaX
        for block in self.arena.layout:
            col, tcol = block.collides(self)

    def moveY(self, deltaY : float):
        self.y += deltaY
        topCollision = False
        for block in self.arena.layout:
            col, tcol = block.collides(self)
            if tcol and isinstance(block, Block):
                self.grounded = True
                self.doubleJump = True
                self.jumpTimer = 0
                topCollision = True
            # else:
            #     if self.grounded:
            #         self.coyote = 4
            #         self.grounded = False
        if not topCollision:
            if self.grounded:
                self.coyote = 4
                self.grounded = False

    def tick(self):
        if self.gravity and self.jumpTimer == 0:
            self.moveY(self.gravity * self.py)
            self.py += 0.05

        if self.jumpTimer > 0:
            self.jumpTimer -= 1
            self.moveY(-self.gravity * 0.8 * (1 if self.doubleJump else 1.2))
            self.py = 0

        self.moveX(self.speed * self.px)
        if self.direction > 0:
            if self.px < 1:
                self.px += 1 / 6
        if self.direction < 0:
            if self.px > -1:
                self.px -= 1 / 6
        if self.direction == 0:
            if self.px < 0:
                self.px += 1 / 3
            elif self.px > 0:
                self.px -= 1 / 3
            if approx(self.px, 0, 0.17):
                self.px = 0

        # print(self.direction, self.px) #

        if self.coyote > 0:
            self.coyote -= 1
            if self.coyote == 0:
                self.grounded = False

        if self.grounded:
            self.py = 0

        if self.y >= 12:
            self.eliminate()

        # print(self.py, self.coyote) #

    def jump(self):
        if self.grounded or self.coyote > 0:
            self.jumpTimer = 15
            self.grounded = False
        elif self.doubleJump:
            self.jumpTimer += 15
            self.doubleJump = False

    def left(self):
        self.direction = -1

    def right(self):
        self.direction = 1

    def central(self):
        self.direction = 0

class Controller:
    def __init__(self, joy, player : Player):
        self.joy = joy
        self.player = player

        self.sensitivity = 0.25
        self.joydirection = 0

    def buttonDown(self, id : int):
        print(id)
        if id == 1:
            self.player.jump()

    def buttonUp(self, id : int):
        pass

    def axisMotion(self, axis : int, value : float):
        if axis == 0:
            # print(value) #
            if value >= self.sensitivity:
                self.joydirection = 1
                self.player.right()
            elif value <= -self.sensitivity:
                self.joydirection = -1
                self.player.left()
            else:
                self.joydirection = 0
                self.player.central()
            # print("DIR", self.player.direction) #

class Arena:
    def __init__(self, layout : list[Block | Spikes] = [], checkpoints : list[tuple[float, float]] = []):
        self.layout = layout
        self.checkpoints = checkpoints

        self.player = Player(self)
        self.cambox : list[float, float] = [0, 0]

        self.controller : Controller | None = None

        self.camW : float = 2.5
        self.camH : float = 2.5
        self.camShakeTimer : int = 0
        self.camShakeForce : float = 0.0

        self.scale : int = 75

    def tick(self):
        self.player.tick()
        # if self.player.x + 0.5 >= self.cambox[0] + self.camW:
        #     self.cambox[0] += self.player.x - self.cambox[0] - self.camW + 0.05
        # if self.player.x - 0.5 <= self.cambox[0] - self.camW:
        #     self.cambox[0] += self.player.x - self.cambox[0] + self.camW - 0.05
        theta = math.atan2(self.cambox[1] - self.player.y, self.cambox[0] - self.player.x)
        distance = math.sqrt((self.cambox[1] - self.player.y) ** 2 + (self.cambox[0] - self.player.x) ** 2)
        # print(distance, theta * 180 / math.pi) #
        if distance <= 0.12:
            self.cambox[0] = self.player.x
            self.cambox[1] = self.player.y
        else:
            self.cambox[0] += -0.12 * distance * math.cos(theta)
            self.cambox[1] += -0.12 * distance * math.sin(theta)

        if self.camShakeTimer > 0:
            self.camShakeTimer -= 1
            if self.camShakeTimer == 0:
                self.camShakeForce = 0

        for checkpoint in self.checkpoints:
            distance = math.sqrt((checkpoint[1] - self.player.y) ** 2 + (checkpoint[0] - self.player.x) ** 2)
            if distance <= 1:
                self.player.checkpoint = list(checkpoint)
                self.checkpoints.remove(checkpoint)

    def cameraShake(self, force : float, duration : int):
        self.camShakeForce += force
        self.camShakeTimer += duration

    def getCamera(self) -> tuple[float, float]:
        shakeX = (1 if self.camShakeTimer > 0 else 0) * self.camShakeForce * random.randint(-100, 100) / 10
        shakeY = (1 if self.camShakeTimer > 0 else 0) * self.camShakeForce * random.randint(-100, 100) / 10
        return (
            self.cambox[0] * self.scale + shakeX,
            self.cambox[1] * self.scale + shakeY,
        )