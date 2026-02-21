import pygame
import sys
import random
import math

# --- Constants ---
WIDTH, HEIGHT = int(1920/5*4), int(1200/5*4)
FPS = 60
PANEL_WIDTH = 250  # width of the side HUD panel

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
CAR_COLORS = [BLUE, (255, 165, 0), (0, 255, 255)]

# Directions
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

# intersection center
CENTER_X, CENTER_Y = WIDTH//2, HEIGHT//2

# lane offsets (two lanes per approach: left side and right side of the road)
VERT_LANES_X = [WIDTH//2 - 40, WIDTH//2 + 40]   # [left lane x, right lane x]
HORIZ_LANES_Y = [HEIGHT//2 - 40, HEIGHT//2 + 40]  # [top lane y, bottom lane y]


def default_lane_for_direction(direction):
    # returns lane_index (0 or 1) that corresponds to the right-hand driving lane
    # mapping consistent with spawn_* functions:
    # DOWN (from top) -> lane 0, UP (from bottom) -> lane 1
    # RIGHT (from left) -> lane 1, LEFT (from right) -> lane 0
    if direction == DOWN:
        return 0
    if direction == UP:
        return 1
    if direction == RIGHT:
        return 1
    return 0  # LEFT

# --- Classes ---
class TrafficLight:
    def __init__(self, pos, number, orientation='vertical'):
        self.pos = pos
        self.orientation = orientation
        self.number = number
        self.lights = ['red', 'yellow', 'green']
        self.state_index = 0
        self.state = self.lights[self.state_index]
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.state == 'green' and self.timer >= 5:
            self.state_index = 1  # yellow
            self.timer = 0
        elif self.state == 'yellow' and self.timer >= 2:
            self.state_index = 0  # red
            self.timer = 0
        elif self.state == 'red' and self.timer >= 5:
            self.state_index = 2  # green
            self.timer = 0
        self.state = self.lights[self.state_index]

    def change(self, color):
        if color in self.lights:
            self.state_index = self.lights.index(color)
            self.state = color
            self.timer = 0

    def draw(self, screen):
        x, y = self.pos
        radius = 10
        spacing = 30
        color_map = {'red': RED, 'yellow': YELLOW, 'green': GREEN}
        pygame.draw.rect(screen, BLACK, (x-12, y-12, 30, 3*spacing))
        for i, light in enumerate(self.lights):
            color = color_map[light] if light == self.state else BLACK
            pygame.draw.circle(screen, color, (x+3, y + i*spacing), radius)
        font = pygame.font.SysFont(None, 24)
        num_text = font.render(f"Light {self.number}", True, BLACK)
        screen.blit(num_text, (x-30, y + 3*spacing))


class Car:
    def __init__(self, pos, direction, lane_index=None, color=None):
        self.pos = [float(pos[0]), float(pos[1])]
        self.direction = direction
        self.speed = 0.0
        self.max_speed = 150.0
        self.color = color if color else random.choice(CAR_COLORS)
        # if lane_index not provided, use default for direction
        self.lane_index = default_lane_for_direction(direction) if lane_index is None else lane_index
        self.turn_decision = None  # 'left','right','straight'
        self.turning = False
        self.has_passed_intersection = False
        self.requesting_intersection = False
        self.has_priority = False
        # set size & align to lane
        if direction in (UP, DOWN):
            self.size = (20, 40)
            # align x to lane
            self.pos[0] = VERT_LANES_X[self.lane_index] - self.size[0]/2
        else:
            self.size = (40, 20)
            # align y to lane
            self.pos[1] = HORIZ_LANES_Y[self.lane_index] - self.size[1]/2
        # give them initial speed gradually
        self.speed = self.max_speed * 0.6

    def rect(self):
        return pygame.Rect(int(self.pos[0]), int(self.pos[1]), self.size[0], self.size[1])

    def distance_to_center_along_path(self):
        # positive distance if approaching center, negative if past
        cx = self.pos[0] + self.size[0]/2
        cy = self.pos[1] + self.size[1]/2
        if self.direction == DOWN:
            return CENTER_Y - cy
        if self.direction == UP:
            return cy - CENTER_Y
        if self.direction == RIGHT:
            return CENTER_X - cx
        if self.direction == LEFT:
            return cx - CENTER_X
        return 9999

    def update(self, dt, lights, cars):
        # Basic traffic-light stop: if red light is near and car approaching intersection, stop.
        stop_distance = 60
        blocked_by_light = False
        for light in lights:
            lx, ly = light.pos
            # only consider the light that controls this approach
            if light.number == 1 and self.direction in (UP, DOWN):
                if light.state == 'red':
                    if self.direction == DOWN and ly - (self.pos[1] + self.size[1]) < stop_distance and ly > self.pos[1]:
                        blocked_by_light = True
                    elif self.direction == UP and self.pos[1] - ly < stop_distance and ly < self.pos[1]:
                        blocked_by_light = True
            if light.number == 2 and self.direction in (LEFT, RIGHT):
                if light.state == 'red':
                    if self.direction == RIGHT and lx - (self.pos[0] + self.size[0]) < stop_distance and lx > self.pos[0]:
                        blocked_by_light = True
                    elif self.direction == LEFT and self.pos[0] - lx < stop_distance and lx < self.pos[0]:
                        blocked_by_light = True
        if blocked_by_light:
            desired_speed = 0.0
        else:
            # Collision avoidance / car-following: keep safe distance from car ahead in same lane/path.
            safe_gap = 40
            desired_speed = self.max_speed
            for other in cars:
                if other is self:
                    continue
                # only consider cars roughly in same lane (for vertical: similar x; for horizontal: similar y)
                if self.direction in (UP, DOWN) and other.direction in (UP, DOWN):
                    if abs((self.pos[0] + self.size[0]/2) - (other.pos[0] + other.size[0]/2)) < 30:
                        # check if other is ahead
                        if self.direction == DOWN and other.pos[1] > self.pos[1]:
                            dist = other.pos[1] - (self.pos[1] + self.size[1])
                            if dist < safe_gap:
                                desired_speed = 0
                            elif dist < safe_gap*3:
                                desired_speed = min(desired_speed, self.max_speed * 0.5)
                        if self.direction == UP and other.pos[1] < self.pos[1]:
                            dist = self.pos[1] - (other.pos[1] + other.size[1])
                            if dist < safe_gap:
                                desired_speed = 0
                            elif dist < safe_gap*3:
                                desired_speed = min(desired_speed, self.max_speed * 0.5)
                if self.direction in (LEFT, RIGHT) and other.direction in (LEFT, RIGHT):
                    if abs((self.pos[1] + self.size[1]/2) - (other.pos[1] + other.size[1]/2)) < 30:
                        if self.direction == RIGHT and other.pos[0] > self.pos[0]:
                            dist = other.pos[0] - (self.pos[0] + self.size[0])
                            if dist < safe_gap:
                                desired_speed = 0
                            elif dist < safe_gap*3:
                                desired_speed = min(desired_speed, self.max_speed * 0.5)
                        if self.direction == LEFT and other.pos[0] < self.pos[0]:
                            dist = self.pos[0] - (other.pos[0] + other.size[0])
                            if dist < safe_gap:
                                desired_speed = 0
                            elif dist < safe_gap*3:
                                desired_speed = min(desired_speed, self.max_speed * 0.5)

        # Intersection request zone & priority enforcement
        request_zone = 120
        dist_center = self.distance_to_center_along_path()
        self.requesting_intersection = (dist_center > 0 and dist_center < request_zone and not self.has_passed_intersection)
        # If car is requesting and does not have priority, it must yield (stop)
        if self.requesting_intersection and not self.has_priority:
            desired_speed = 0.0

        # Apply desired speed smoothly
        if desired_speed < self.speed:
            self.speed = max(desired_speed, self.speed - 300 * dt)
        else:
            self.speed = min(desired_speed, self.speed + 300 * dt)

        # Decide turning when approaching intersection center
        in_intersection_zone = abs(self.pos[0] + self.size[0]/2 - CENTER_X) < 40 and abs(self.pos[1] + self.size[1]/2 - CENTER_Y) < 40
        if in_intersection_zone and not self.turn_decision and not self.has_passed_intersection:
            r = random.random()
            if r < 0.6:
                self.turn_decision = 'straight'
            elif r < 0.8:
                self.turn_decision = 'left'
            else:
                self.turn_decision = 'right'
            if self.turn_decision != 'straight':
                self.turning = True

        # If turning, when centered, snap to target lane and change direction
        if self.turning and in_intersection_zone:
            # mapping for left/right turns (relative to car heading)
            left_map = {UP: LEFT, DOWN: RIGHT, LEFT: DOWN, RIGHT: UP}
            right_map = {UP: RIGHT, DOWN: LEFT, LEFT: UP, RIGHT: DOWN}
            if self.turn_decision == 'left':
                new_dir = left_map[self.direction]
            elif self.turn_decision == 'right':
                new_dir = right_map[self.direction]
            else:
                new_dir = self.direction
            self.direction = new_dir
            # pick correct lane for new direction to preserve right-hand traffic
            self.lane_index = default_lane_for_direction(self.direction)
            # adjust size/orientation and align to correct lane for new direction
            if self.direction in (UP, DOWN):
                self.size = (20, 40)
                self.pos[0] = VERT_LANES_X[self.lane_index] - self.size[0]/2
            else:
                self.size = (40, 20)
                self.pos[1] = HORIZ_LANES_Y[self.lane_index] - self.size[1]/2
            self.turning = False
            self.has_passed_intersection = True
            # release priority when inside intersection so other cars can be selected next tick
            self.has_priority = False

        # After passing intersection, reset decision after clear area
        if self.has_passed_intersection:
            outside_zone = abs(self.pos[0] + self.size[0]/2 - CENTER_X) > 120 or abs(self.pos[1] + self.size[1]/2 - CENTER_Y) > 120
            if outside_zone:
                self.turn_decision = None
                self.has_passed_intersection = False

        # Move according to direction and current speed
        if self.direction == RIGHT:
            self.pos[0] += self.speed * dt
        elif self.direction == LEFT:
            self.pos[0] -= self.speed * dt
        elif self.direction == DOWN:
            self.pos[1] += self.speed * dt
        elif self.direction == UP:
            self.pos[1] -= self.speed * dt

        # Keep cars on-screen (remove if out of bounds)
        if (self.pos[0] < -200 or self.pos[0] > WIDTH + 200 or
            self.pos[1] < -200 or self.pos[1] > HEIGHT + 200):
            try:
                cars.remove(self)
            except ValueError:
                pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.pos[0]), int(self.pos[1]), self.size[0], self.size[1]))
        # optional: draw small arrow indicating direction
        cx = int(self.pos[0] + self.size[0]/2)
        cy = int(self.pos[1] + self.size[1]/2)
        if self.direction == UP:
            pygame.draw.polygon(screen, BLACK, [(cx-5, cy+6),(cx+5, cy+6),(cx, cy-6)])
        elif self.direction == DOWN:
            pygame.draw.polygon(screen, BLACK, [(cx-5, cy-6),(cx+5, cy-6),(cx, cy+6)])
        elif self.direction == LEFT:
            pygame.draw.polygon(screen, BLACK, [(cx+6, cy-5),(cx+6, cy+5),(cx-6, cy)])
        elif self.direction == RIGHT:
            pygame.draw.polygon(screen, BLACK, [(cx-6, cy-5),(cx-6, cy+5),(cx+6, cy)])


class Button:
    def __init__(self, rect, text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont(None, 30)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt = self.font.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + 5, self.rect.y + 5))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()


# --- Functions ---
def spawn_vertical_car():
    # enforce side-of-road: right-hand traffic
    # for DOWN (from top) use lane 0, for UP (from bottom) use lane 1
    spawn_top = random.choice([True, False])
    if spawn_top:
        direction = DOWN
        lane_index = default_lane_for_direction(direction)
        lane_x = VERT_LANES_X[lane_index] - 10
        start_y = -60
        cars.append(Car([lane_x, start_y], direction, lane_index))
    else:
        direction = UP
        lane_index = default_lane_for_direction(direction)
        lane_x = VERT_LANES_X[lane_index] - 10
        start_y = HEIGHT + 60
        cars.append(Car([lane_x, start_y], direction, lane_index))


def spawn_horizontal_car():
    # enforce side-of-road: right-hand traffic
    # for RIGHT (from left) use lane 1, for LEFT (from right) use lane 0
    spawn_left = random.choice([True, False])
    if spawn_left:
        direction = RIGHT
        lane_index = default_lane_for_direction(direction)
        lane_y = HORIZ_LANES_Y[lane_index] - 10
        start_x = -60
        cars.append(Car([start_x, lane_y], direction, lane_index))
    else:
        direction = LEFT
        lane_index = default_lane_for_direction(direction)
        lane_y = HORIZ_LANES_Y[lane_index] - 10
        start_x = WIDTH - PANEL_WIDTH + 60
        cars.append(Car([start_x, lane_y], direction, lane_index))


# --- Main ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Simulation")
clock = pygame.time.Clock()

# Traffic lights
vertical_light = TrafficLight((WIDTH//2-75, HEIGHT//2-75), 1)
horizontal_light = TrafficLight((WIDTH//2+75, HEIGHT//2-75), 2)
horizontal_light.change('green')  # ensure consistent initial state
lights = [vertical_light, horizontal_light]

cars = []

# Buttons on panel
buttons = [
    Button((WIDTH-PANEL_WIDTH+20, 20, 200, 50), "Spawn Vertical Car", spawn_vertical_car),
    Button((WIDTH-PANEL_WIDTH+20, 90, 200, 50), "Spawn Horizontal Car", spawn_horizontal_car),
    Button((WIDTH-PANEL_WIDTH+20, 170, 200, 50), "Light 1 RED", lambda: vertical_light.change('red')),
    Button((WIDTH-PANEL_WIDTH+20, 250, 200, 50), "Light 1 GREEN", lambda: vertical_light.change('green')),
    Button((WIDTH-PANEL_WIDTH+20, 330, 200, 50), "Light 2 RED", lambda: horizontal_light.change('red')),
    Button((WIDTH-PANEL_WIDTH+20, 410, 200, 50), "Light 2 GREEN", lambda: horizontal_light.change('green')),
]

running = True
while running:
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                button.click(event.pos)

    # Update lights
    for light in lights:
        light.update(dt)

    # Determine intersection priority each tick
    # cars must obey traffic lights to request priority
    request_zone = 120
    requesting = []  # list of (car, eta)
    for car in cars:
        # reset priority flags
        car.has_priority = False
        # identify controlling light
        ctrl_light = vertical_light if car.direction in (UP, DOWN) else horizontal_light
        if ctrl_light.state != 'green':
            continue
        dist = car.distance_to_center_along_path()
        if dist > 0 and dist < request_zone and not car.has_passed_intersection:
            est_speed = max(car.speed, 10.0)
            eta = dist / est_speed
            requesting.append((car, eta))

    # Grant priority only after resolving perpendicular conflicts.
    # Only perpendicular requesters compete for the same intersection space.
    EPS = 0.2  # seconds tolerance to avoid ties
    for car, eta in requesting:
        has_earlier_perp = False
        for other, other_eta in requesting:
            if other is car:
                continue
            perp = (car.direction in (UP, DOWN) and other.direction in (LEFT, RIGHT)) or \
                   (car.direction in (LEFT, RIGHT) and other.direction in (UP, DOWN))
            if perp and other_eta < eta - EPS:
                has_earlier_perp = True
                break
        car.has_priority = not has_earlier_perp

    # update cars; pass full list so cars can avoid each other
    for car in list(cars):
        car.update(dt, lights, cars)

    # Draw
    screen.fill(WHITE)
    # Roads (vertical and horizontal)
    pygame.draw.rect(screen, GRAY, (WIDTH//2-100, 0, 200, HEIGHT))  # vertical road
    pygame.draw.rect(screen, GRAY, (0, HEIGHT//2-100, WIDTH-PANEL_WIDTH, 200))  # horizontal road

    # lane separators (visual)
    pygame.draw.line(screen, BLACK, (WIDTH//2-100, HEIGHT//2-100), (WIDTH//2-100, HEIGHT//2+100), 2)
    pygame.draw.line(screen, BLACK, (WIDTH//2+100, HEIGHT//2-100), (WIDTH//2+100, HEIGHT//2+100), 2)
    pygame.draw.line(screen, BLACK, (0, HEIGHT//2-100), (WIDTH-PANEL_WIDTH, HEIGHT//2-100), 2)
    pygame.draw.line(screen, BLACK, (0, HEIGHT//2+100), (WIDTH-PANEL_WIDTH, HEIGHT//2+100), 2)

    # Side panel
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH-PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT))

    for light in lights:
        light.draw(screen)
    for car in cars:
        car.draw(screen)
    for button in buttons:
        button.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
