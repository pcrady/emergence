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
    radius: float = 3.0
    mass: float = 1.0

    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float, bounce: bool = True, draw_force_vector: bool = True) -> None:
        self.position_x: float = x
        self.position_y: float = y

        self.velocity_x: float = velocity_x
        self.velocity_y: float = velocity_y

        self.color: str = self.__random_color()
        self.bounce: bool = bounce
        self.draw_force_vector: bool = draw_force_vector

        self.position_x_left_edge: float = self.position_x - Particle.radius
        self.position_x_right_edge: float = self.position_x + Particle.radius

        self.position_y_top_edge: float = self.position_y + Particle.radius
        self.position_y_bottom_edge: float = self.position_y - Particle.radius

        self.force_vector: tuple[float, float] = (0, 0)

    @staticmethod
    def __random_color() -> str:
        return random.choice(list(Color.__members__))

    def truncate(self, value: float) -> float:
        return float('%.3f'%(value))

    def print_position(self, label = "") -> None:
        print("{}Position: ({},{})".format(label, truncate(self.position_x), truncate(self.position_y)))

    def print_velocity(self, label = "") -> None:
        print("{}Velocity: ({},{})".format(label, truncate(self.velocity_x), truncate(self.velocity_y)))

    def draw(self, screen) -> None:
        pygame.draw.circle(screen, self.color, (self.position_x, self.position_y), Particle.radius)

        if self.draw_force_vector:
            start_position = (self.position_x, self.position_y)
            end_position = tuple(map(sum, zip(start_position, self.force_vector)))
            pygame.draw.line(screen, self.color, start_position, end_position)
            

    def calculate_position(self, time_delta, screen) -> None:
        epsilon = 1
        position_x = self.position_x + self.velocity_x * time_delta
        position_y = self.position_y + self.velocity_y * time_delta

        if not self.bounce:
            # calculate the x position withOUT bouncing
            if position_x < 0:
                self.position_x = screen.x_screen - epsilon
            elif position_x > screen.x_screen:
                self.position_x = 0 + epsilon
            else:
                self.position_x = position_x

            # calculate the y position withOUT bouncing
            if position_y < 0:
                self.position_y = screen.y_screen - epsilon
            elif position_y > screen.y_screen:
                self.position_y = 0 + epsilon
            else:
                self.position_y = position_y
        else:
            # calculate the x position WITH bounching
            # inverts velocity_x if necessary
            if position_x < 0:
                self.position_x = 0 + epsilon
                self.velocity_x *= -1.0
            elif position_x > screen.x_screen:
                self.position_x = screen.x_screen - epsilon
                self.velocity_x *= -1.0
            else:
                self.position_x = position_x

            # calculate the y position WITH bouncing
            # inverts velocity_y if necessary
            if position_y < 0:
                self.position_y = 0 + epsilon
                self.velocity_y *= -1.0
            elif position_y > screen.y_screen:
                self.position_y = screen.y_screen - epsilon
                self.velocity_y *= -1.0
            else:
                self.position_y = position_y
            

    def calculate_velocity(self, time_delta, other_particle) -> None:
        self.calculate_force(other_particle)
        velocity_x = self.velocity_x + self.force_vector[0] * time_delta 
        velocity_y = self.velocity_y + self.force_vector[1] * time_delta

        if velocity_x >= 0:
            self.velocity_x = velocity_x if velocity_x <= 500.0 else 500.0
        else:
            self.velocity_x = velocity_x if velocity_x >= -500.0 else -500.0
 
        if velocity_y >= 0:
            self.velocity_y = velocity_y if velocity_y <= 500.0 else 500.0
        else: 
            self.velocity_y = velocity_y if velocity_y >= -500.0 else -500.0
 

    def calculate_force(self, other_particle) -> None:
        numerator = 10000000.0 if self.color == other_particle.color else -10000000.0

        total_distance = (self.position_x - other_particle.position_x) ** 2 + (self.position_y - other_particle.position_y) ** 2

        total_distance = total_distance if total_distance >= 0.0001 else 0.0001
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

        self.force_vector = (force_x, force_y)


class Screen:
    x_screen: float = 1000
    y_screen: float = 1000

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Screen.x_screen, Screen.y_screen))
        pygame.display.set_caption("Emergent Phenomena Simulation")
        self.clock = pygame.time.Clock()

    def fill(self) -> None:
        self.screen.fill((0, 0, 0))

    def get_time(self) -> int:
        return self.clock.get_time()

       

screen = Screen()    

num_particles = 2

particles = [Particle(random.uniform(50, 950),
                      random.uniform(50, 950),
                      random.uniform(-100, 100),
                      random.uniform(-100, 100),
                      True) for _ in range(num_particles)]

particles = [Particle(500, 100, 100, 100, True), Particle(500, 900, -100, -90, True)]
#particles = [Particle(200, 100, 0, 0), Particle(600, 500, 0, 0)]
# Main simulation loop
running = True
while running:
    screen.fill()

    time_delta = screen.get_time() / 1000

    # Draw and update particle positions
    for i in range(num_particles):
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

