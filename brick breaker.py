import pyxel
import math
import random

class App:
    def __init__(self):
        pyxel.init(200, 200, title="Brick Breaker")
        pyxel.mouse(True)

        self.balls = [Ball()]
        self.pad = Pad()
        self.bricks = []
        self.warp_blocks = []
        self.stage = 1
        self.background_color = 0
        self.generate_bricks()
        self.score = 0
        self.game_over = False
        self.time_elapsed = 0

        pyxel.run(self.update, self.draw)

    def generate_bricks(self):
        self.bricks = []

        num_bricks = 8 + (self.stage - 1) * 5

        while len(self.bricks) < num_bricks:
            x, y = random.randint(10, 172), random.randint(10, 100)
            new_brick = Brick(x, y, random.randint(1, 3))
            if not any(new_brick.is_overlapping(brick) for brick in self.bricks):
                self.bricks.append(new_brick)

        for _ in range(5):
            x, y = random.randint(10, 172), random.randint(10, 100)
            new_brick = UnbreakableBrick(x, y)
            if not any(new_brick.is_overlapping(brick) for brick in self.bricks):
                self.bricks.append(new_brick)

        for _ in range(5):
            x, y = random.randint(10, 172), random.randint(10, 100)
            new_brick = PermanentBrick(x, y)
            if not any(new_brick.is_overlapping(brick) for brick in self.bricks):
                self.bricks.append(new_brick)

        for _ in range(3):
            x, y = random.randint(10, 172), random.randint(10, 100)
            new_brick = MultiplierBrick(x, y)
            if not any(new_brick.is_overlapping(brick) for brick in self.bricks):
                self.bricks.append(new_brick)

        if self.stage > 1:
            self.warp_blocks = []
            for _ in range(2):
                x, y = random.randint(30, 170), random.randint(30, 150)
                new_warp = WarpBlock(x, y)
                self.warp_blocks.append(new_warp)

    def update(self):
        if self.game_over:
            return

        self.time_elapsed += 1

        if self.time_elapsed % 600 == 0:
            for ball in self.balls:
                ball.increase_speed()

        self.pad.move(self.stage)

        for ball in self.balls[:]:
            ball.move()

            if self.pad.catch(ball):
                ball.bounce_y()

            for brick in self.bricks[:]:
                if brick.check_collision(ball):
                    ball.bounce_y()
                    pyxel.play(0, 0)
                    if isinstance(brick, (UnbreakableBrick, PermanentBrick)):
                        continue
                    if isinstance(brick, MultiplierBrick):
                        self.balls.extend([Ball(ball.x, ball.y) for _ in range(2)])
                    brick.hit()
                    if brick.health <= 0:
                        self.bricks.remove(brick)
                        self.score += 10 * brick.initial_health

            for warp in self.warp_blocks:
                if warp.check_collision(ball):
                    ball.warp(self.warp_blocks)

            if ball.y > pyxel.height:
                self.balls.remove(ball)

        if not self.balls:
            self.game_over = True

        if all(isinstance(brick, (UnbreakableBrick, PermanentBrick)) for brick in self.bricks):
            self.stage += 1
            self.background_color = random.randint(0, 15)
            self.generate_bricks()

    def draw(self):
        pyxel.cls(self.background_color)

        if self.game_over:
            pyxel.text(80, 90, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(70, 110, f"Score: {self.score}", pyxel.COLOR_WHITE)
            return

        pyxel.rect(self.pad.x - self.pad.width // 2, 190, self.pad.width, 5, 11)

        for ball in self.balls:
            pyxel.circ(ball.x, ball.y, 5, 7)

        for brick in self.bricks:
            pyxel.rect(brick.x, brick.y, brick.width, brick.height, brick.color)

        for warp in self.warp_blocks:
            pyxel.circ(warp.x, warp.y, warp.radius, warp.color)

        pyxel.text(5, 5, f"Score: {self.score}", pyxel.COLOR_WHITE)
        pyxel.text(5, 15, f"Stage: {self.stage}", pyxel.COLOR_WHITE)

class Ball:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else pyxel.width // 2
        self.y = y if y is not None else pyxel.height // 2
        self.radius = 5
        self.speed = 2
        angle = math.radians(pyxel.rndi(30, 150))
        self.vx = math.cos(angle) * self.speed
        self.vy = -math.sin(angle) * self.speed

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > pyxel.width:
            self.vx *= -1
        if self.y < 0:
            self.vy *= -1

    def bounce_y(self):
        self.vy *= -1

    def increase_speed(self):
        self.vx *= 1.1
        self.vy *= 1.1

    def warp(self, warp_blocks):
        other = random.choice([w for w in warp_blocks if w != self])
        self.x, self.y = other.x, other.y

class Pad:
    def __init__(self):
        self.x = pyxel.width // 2
        self.width = 40

    def move(self, stage):
        self.x = pyxel.mouse_x
        self.width = max(20, 40 - (stage - 1) * 5)
        self.x = max(self.width // 2, min(pyxel.width - self.width // 2, self.x))

    def catch(self, ball):
        return (
            190 <= ball.y + ball.radius <= 195
            and self.x - self.width // 2 <= ball.x <= self.x + self.width // 2
        )

class Brick:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.width = 28
        self.height = 10
        self.health = health
        self.initial_health = health
        self.color = self.get_color()

    def get_color(self):
        return {1: 6, 2: 10, 3: 14}.get(self.health, 0)

    def check_collision(self, ball):
        if (
            self.x < ball.x < self.x + self.width
            and self.y < ball.y < self.y + self.height
        ):
            return True
        return False

    def hit(self):
        self.health -= 1
        self.color = self.get_color()

    def is_overlapping(self, other):
        return not (
            self.x + self.width < other.x or
            self.x > other.x + other.width or
            self.y + self.height < other.y or
            self.y > other.y + other.height
        )

class UnbreakableBrick(Brick):
    def __init__(self, x, y):
        super().__init__(x, y, health=0)
        self.color = 7

    def hit(self):
        pass

class PermanentBrick(Brick):
    def __init__(self, x, y):
        super().__init__(x, y, health=0)
        self.color = 15

    def hit(self):
        pass

class MultiplierBrick(Brick):
    def __init__(self, x, y):
        super().__init__(x, y, health=1)
        self.color = 13

class WarpBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = 0

    def check_collision(self, ball):
        return math.hypot(self.x - ball.x, self.y - ball.y) < self.radius

App()
