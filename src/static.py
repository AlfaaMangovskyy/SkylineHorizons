import math

WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60

DIAGONAL = 1 / math.sqrt(2)

def approx(a : float, b : float, diff : float):
    return a - diff <= b <= a + diff

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

class Player:
    def __init__(self, arena, x : float = 0.0, y : float = 0.0, nickname : str = "???"):
        self.x, self.y = x, y
        self.arena : Arena | None = arena
        self.nickname = nickname

        self.isGravity : bool = True
        self.gravity : float = 0.35
        self.speed : float = 0.15

        self.grounded : bool = False
        self.coyote : int = 0
        self.jumpTimer : int = 0
        self.doubleJump : bool = False

        self.direction : int = 0

        self.px : float = 0.0
        self.py : float = 0.0

    def moveX(self, deltaX : float):
        self.x += deltaX
        for block in self.arena.layout:
            col, tcol = block.collides(self)

    def moveY(self, deltaY : float):
        self.y += deltaY
        for block in self.arena.layout:
            col, tcol = block.collides(self)
            if tcol:
                self.grounded = True
                self.doubleJump = True
                self.jumpTimer = 0
            else:
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

class Arena:
    def __init__(self, layout : list[Block]):
        self.layout = layout
        self.player = Player(self)
        self.cambox : list[float, float] = [0, 0]

        self.camW : float = 2.5
        self.camH : float = 2.5

        self.scale : int = 75

    def tick(self):
        self.player.tick()
        if self.player.x + 0.5 >= self.cambox[0] + self.camW:
            self.cambox[0] += self.player.x - self.cambox[0] - self.camW + 0.05
        if self.player.x - 0.5 <= self.cambox[0] - self.camW:
            self.cambox[0] += self.player.x - self.cambox[0] + self.camW - 0.05

    def getCamera(self) -> tuple[float, float]:
        return (
            self.cambox[0] * self.scale,
            self.cambox[1] * self.scale,
        )