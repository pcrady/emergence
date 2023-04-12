import pygame
import random
import math
from enum import Enum

def truncate(value: float) -> float:
    return float('%.3f'%(value))

class Color(Enum):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

# Define Particle class
class Particle:
    radius: float = 10.0
    mass: float = 1.0

    def __init__(self, x, y, velocity_x, velocity_y) -> None:
        self.position_x: float = x
        self.position_y: float = y

        self.velocity_x: float = velocity_x
        self.velocity_y: float = velocity_y

        self.color: str = self.random_color()

        self.position_x_left_edge: float = self.position_x - Particle.radius
        self.position_x_right_edge: float = self.position_x + Particle.radius

        self.position_y_top_edge: float = self.position_y + Particle.radius
        self.position_y_bottom_edge: float = self.position_y - Particle.radius

    @staticmethod
    def random_color() -> str:
        return random.choice(list(Color.__members__))

    def truncate(self, value: float) -> float:
        return float('%.3f'%(value))

    def print_position(self, label = "") -> None:
        if self.position_x < 0 or self.position_y < 0:
            print("{}Position: ({},{})".format(label, truncate(self.position_x), truncate(self.position_y)))

    def print_velocity(self, label = "") -> None:
        print("{}Velocity: ({},{})".format(label, truncate(self.velocity_x), truncate(self.velocity_y)))

    def draw(self, screen) -> None:
        pygame.draw.circle(screen, self.color, (int(self.position_x), int(self.position_y)), Particle.radius)

    def calculate_position(self, time_delta, screen) -> None:
        epsilon = 1.0
        if (self.position_x < 0 + epsilon):
            self.position_x = screen.x_screen - epsilon
        if (self.position_x > screen.x_screen - epsilon):
            self.position_x = 0 + epsilon
        if (self.position_y < 0 + epsilon):
            self.position_y = screen.y_screen - epsilon
        if (self.position_y > screen.y_screen - epsilon):
            self.position_y = 0 + epsilon
        else:
            self.position_x += self.velocity_x * time_delta
            self.position_y += self.velocity_y * time_delta

    def calculate_velocity(self, time_delta, other_particle) -> None:
        force = self.calculate_force(other_particle)
        velocity_x = self.velocity_x + force[0] * time_delta 
        velocity_y = self.velocity_y + force[1] * time_delta

        if velocity_x >= 0:
            self.velocity_x = velocity_x if velocity_x <= 500.0 else 500.0
        else:
            self.velocity_x = velocity_x if velocity_x >= -500.0 else -500.0
 
        if velocity_y >= 0:
            self.velocity_y = velocity_y if velocity_y <= 500.0 else 500.0
        else: 
            self.velocity_y = velocity_y if velocity_y >= -500.0 else -500.0
 

    def calculate_force(self, other_particle) -> tuple[float, float]:
        numerator = 10000000.0 if self.color == other_particle.color else -1000000.0

        total_distance = (self.position_x - other_particle.position_x) ** 2 + (self.position_y - other_particle.position_y) ** 2
        total_distance = total_distance if total_distance != 0 else 0.001
        force_magnitude = numerator / total_distance

        delta_y = self.position_y - other_particle.position_y
        delta_x = self.position_x - other_particle.position_x if self.position_x != other_particle.position_x else 0.0001

        angle = math.atan(delta_y / delta_x)

        force_x = math.cos(angle) * force_magnitude
        force_y = math.sin(angle) * force_magnitude

        if self.position_x < other_particle.position_x:
            force_x *= -1
        if self.position_y < other_particle.position_y:
            force_y *= -1

        return (force_x, force_y)


class Screen:
    x_screen: float = 1000
    y_screen: float = 1000

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Screen.x_screen, Screen.y_screen))
        pygame.display.set_caption("Emergent Phenomena Simulation")
        self.clock = pygame.time.Clock()


    def fill(self) -> None:
        self.screen.fill((255, 255, 255))

    def get_time(self) -> int:
        return self.clock.get_time()

       

screen = Screen()    

num_particles = 100

particles = [Particle(random.uniform(50, 950),
                      random.uniform(50, 950),
                      random.uniform(-100, 100),
                      random.uniform(-100, 100)) for _ in range(num_particles)]

#particles = [Particle(200, 100, 0, 0), Particle(600, 500, 0, 0)]
# Main simulation loop
running = True
while running:
    screen.fill()

    time_delta = screen.get_time() / 1000

    # Draw and update particle positions
    for i in range(num_particles):
        particles[i].print_position()

        for j in range(i + 1, num_particles):
            particles[i].calculate_velocity(time_delta, particles[j])
            particles[j].calculate_velocity(time_delta, particles[i])
            
    for p in particles:
        p.calculate_position(time_delta, screen)
        p.draw(screen.screen)



    pygame.display.flip()
    screen.clock.tick(60)

    # Check for exit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

