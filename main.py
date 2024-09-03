import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game with Bushes")

SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
ROAD_GRAY = (100, 100, 100)
MARKING_COLOR = (240, 240, 240)
CAR_COLOR = (255, 0, 0)
BUSH_COLOR = (0, 100, 0)

HORIZON_Y = HEIGHT // 3
VANISHING_POINT_Y = HORIZON_Y - 50
ROAD_WIDTH = 600

MARKING_WIDTH = 20
MARKING_LENGTH = 60
MARKING_GAP = 40

SPEED = 0.8
PERSPECTIVE_SPEED_FACTOR = 5

CAR_WIDTH = 100
CAR_HEIGHT = 60

CAR_Y_MIN = HEIGHT - CAR_HEIGHT - 100
CAR_Y_MAX = HEIGHT - CAR_HEIGHT

CAR_X_MIN = 180
CAR_X_MAX = 620

ACCELERATION = 0.2
FRICTION = 0.98
MAX_SPEED = 8

BUSH_SIZE = 40
NUM_BUSHES = 40

class Bush:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, speed):
        self.y += apply_perspective_speed(self.y, speed)
        if self.y > screen_to_y(HEIGHT):
            self.respawn()

    def respawn(self):
        self.y = random.uniform(0, screen_to_y(HORIZON_Y))
        self.x = random.choice([-1, 1]) * (ROAD_WIDTH // 2 + random.randint(50, 200))

def render_surface():
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GROUND_GREEN, (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y))

def render_road():
    road_left_bottom = (WIDTH - ROAD_WIDTH) // 2
    road_right_bottom = road_left_bottom + ROAD_WIDTH
    
    horizon_width = ROAD_WIDTH * (HORIZON_Y - VANISHING_POINT_Y) / (HEIGHT - VANISHING_POINT_Y)
    road_left_horizon = (WIDTH - horizon_width) // 2
    road_right_horizon = road_left_horizon + horizon_width
    
    pygame.draw.polygon(screen, ROAD_GRAY, [
        (road_left_bottom, HEIGHT),
        (road_right_bottom, HEIGHT),
        (road_right_horizon, HORIZON_Y),
        (road_left_horizon, HORIZON_Y)
    ])
    
    return (road_left_bottom, road_right_bottom), (road_left_horizon, road_right_horizon)

def y_to_screen(y):
    total_height = HEIGHT - VANISHING_POINT_Y
    return VANISHING_POINT_Y + (y * y) / (total_height * 4)

def screen_to_y(screen_y):
    total_height = HEIGHT - VANISHING_POINT_Y
    return math.sqrt((screen_y - VANISHING_POINT_Y) * total_height * 4)

def apply_perspective_speed(y, speed):
    total_height = HEIGHT - VANISHING_POINT_Y
    perspective_factor = y / total_height
    return speed * (1 + PERSPECTIVE_SPEED_FACTOR * perspective_factor)

def render_road_markings(offset):
    total_height = HEIGHT - HORIZON_Y
    y = 0
    
    while True:
        top_y = y + offset
        screen_top_y = y_to_screen(top_y)
        
        if screen_top_y >= HEIGHT:
            break
        
        bottom_y = y + MARKING_LENGTH + offset
        screen_bottom_y = y_to_screen(bottom_y)
        
        width_top = MARKING_WIDTH * (screen_top_y - HORIZON_Y) / total_height
        width_bottom = MARKING_WIDTH * (screen_bottom_y - HORIZON_Y) / total_height
        
        x_center = WIDTH / 2
        
        if screen_top_y >= HORIZON_Y:
            pygame.draw.polygon(screen, MARKING_COLOR, [
                (x_center - width_top / 2, screen_top_y),
                (x_center + width_top / 2, screen_top_y),
                (x_center + width_bottom / 2, screen_bottom_y),
                (x_center - width_bottom / 2, screen_bottom_y)
            ])
        elif screen_bottom_y > HORIZON_Y:
            clip_factor = (HORIZON_Y - screen_top_y) / (screen_bottom_y - screen_top_y)
            width_clip = width_top + (width_bottom - width_top) * clip_factor
            pygame.draw.polygon(screen, MARKING_COLOR, [
                (x_center - width_clip / 2, HORIZON_Y),
                (x_center + width_clip / 2, HORIZON_Y),
                (x_center + width_bottom / 2, screen_bottom_y),
                (x_center - width_bottom / 2, screen_bottom_y)
            ])
        
        y += MARKING_LENGTH + MARKING_GAP
    
    new_offset = offset + apply_perspective_speed(screen_to_y(HEIGHT), SPEED)
    return new_offset % (MARKING_LENGTH + MARKING_GAP)

def render_player_car(x, y):
    vanishing_x = WIDTH // 2
    base_width = CAR_WIDTH
    car_bottom_y = y + CAR_HEIGHT
    car_top_y = y
    
    def get_x_on_vanishing_line(base_x, y):
        if y == VANISHING_POINT_Y:
            return vanishing_x
        return vanishing_x + (base_x - vanishing_x) * (y - VANISHING_POINT_Y) / (HEIGHT - VANISHING_POINT_Y)
    
    bottom_left = (get_x_on_vanishing_line(x - base_width / 2, car_bottom_y), car_bottom_y)
    bottom_right = (get_x_on_vanishing_line(x + base_width / 2, car_bottom_y), car_bottom_y)
    top_left = (get_x_on_vanishing_line(x - base_width / 2, car_top_y), car_top_y)
    top_right = (get_x_on_vanishing_line(x + base_width / 2, car_top_y), car_top_y)
    
    pygame.draw.polygon(screen, CAR_COLOR, [top_left, top_right, bottom_right, bottom_left])

def render_bush(bush):
    screen_y = y_to_screen(bush.y)
    if screen_y < HORIZON_Y or screen_y > HEIGHT:
        return

    size_factor = (screen_y - VANISHING_POINT_Y) / (HEIGHT - VANISHING_POINT_Y)
    bush_size = int(BUSH_SIZE * size_factor)

    x_offset = bush.x * size_factor
    screen_x = WIDTH // 2 + x_offset

    pygame.draw.circle(screen, BUSH_COLOR, (int(screen_x), int(screen_y)), bush_size)

def get_road_width_at_y(y, road_bottom, road_top):
    total_height = HEIGHT - VANISHING_POINT_Y
    y_factor = (y - VANISHING_POINT_Y) / total_height
    return road_bottom[1] - road_bottom[0] + (road_top[1] - road_top[0] - (road_bottom[1] - road_bottom[0])) * (1 - y_factor)

def main():
    clock = pygame.time.Clock()
    offset = 0
    car_x = WIDTH // 2
    car_y = CAR_Y_MAX
    
    car_speed_x = 0
    car_speed_y = 0
    
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
    if joystick:
        joystick.init()
    
    bushes = [Bush(random.choice([-1, 1]) * (ROAD_WIDTH // 2 + random.randint(50, 200)), 
                   random.uniform(0, screen_to_y(HEIGHT))) for _ in range(NUM_BUSHES)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        render_surface()
        road_bottom, road_top = render_road()
        offset = render_road_markings(offset)
        
        if joystick:
            joystick_x = joystick.get_axis(0)
            joystick_y = joystick.get_axis(1)
            
            car_speed_x += joystick_x * ACCELERATION
            car_speed_y += joystick_y * ACCELERATION
        
        car_speed_x *= FRICTION
        car_speed_y *= FRICTION
        
        speed = math.sqrt(car_speed_x**2 + car_speed_y**2)
        if speed > MAX_SPEED:
            car_speed_x = (car_speed_x / speed) * MAX_SPEED
            car_speed_y = (car_speed_y / speed) * MAX_SPEED
        
        car_x += car_speed_x
        car_y += car_speed_y
        
        road_width_at_car = get_road_width_at_y(car_y, road_bottom, road_top)
        road_left_at_car = (WIDTH - road_width_at_car) / 2
        road_right_at_car = road_left_at_car + road_width_at_car
        
        if car_x < CAR_X_MIN:
            car_x = CAR_X_MIN
            car_speed_x = 0
        elif car_x > CAR_X_MAX:
            car_x = CAR_X_MAX
            car_speed_x = 0
        
        if car_y < CAR_Y_MIN:
            car_y = CAR_Y_MIN
            car_speed_y = 0
        elif car_y > CAR_Y_MAX:
            car_y = CAR_Y_MAX
            car_speed_y = 0
        
        for bush in bushes:
            bush.move(SPEED)
            render_bush(bush)

        render_player_car(car_x, car_y)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
