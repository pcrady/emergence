import pygame
import random
from enum import Enum

class Color(Enum):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

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

    def __handle_walls(self, position_x: float, position_y: float, screen: 'Screen') -> None:
        epsilon = 1
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

    def __handle_max_velocity(self, velocity_x: float, velocity_y: float) -> None:
        if velocity_x >= 0:
            self.velocity_x = velocity_x if velocity_x <= 500.0 else 500.0
        else:
            self.velocity_x = velocity_x if velocity_x >= -500.0 else -500.0
 
        if velocity_y >= 0:
            self.velocity_y = velocity_y if velocity_y <= 500.0 else 500.0
        else: 
            self.velocity_y = velocity_y if velocity_y >= -500.0 else -500.0
 
    def __truncate(self, value: float) -> float:
        return float('%.3f'%(value))

    def print_position(self, label = "") -> None:
        print("{}Position: ({},{})".format(label, self.__truncate(self.position_x), self.__truncate(self.position_y)))

    def print_velocity(self, label = "") -> None:
        print("{}Velocity: ({},{})".format(label, self.__truncate(self.velocity_x), self.__truncate(self.velocity_y)))

    def draw(self, screen: 'Screen') -> None:
        pygame.draw.circle(screen.screen, self.color, (self.position_x, self.position_y), Particle.radius)

        if self.draw_force_vector:
            particle_position = (self.position_x, self.position_y)
            end_position_force = tuple(map(sum, zip(particle_position, self.force_vector)))
            pygame.draw.line(screen.screen, self.color, particle_position, end_position_force)

    def calculate_position(self, time_delta: float, screen: 'Screen') -> None:
        position_x = self.position_x + self.velocity_x * time_delta
        position_y = self.position_y + self.velocity_y * time_delta
        self.__handle_walls(position_x, position_y, screen)

    def calculate_velocity(self, time_delta: float, other_particle: 'Particle') -> None:
        self.calculate_force(other_particle)
        velocity_x = self.velocity_x + self.force_vector[0] * time_delta 
        velocity_y = self.velocity_y + self.force_vector[1] * time_delta
        self.__handle_max_velocity(velocity_x, velocity_y)

    def calculate_force(self, other_particle: 'Particle') -> tuple[float, float]:
        force_constant = -1000000.0

        delta_x = self.position_x - other_particle.position_x
        delta_y = self.position_y - other_particle.position_y

        magnitude = ((delta_x)**2 + (delta_y)**2)**0.5
        unit_vector = (delta_x / magnitude, delta_y / magnitude)

        force_x = (force_constant / magnitude ** 2) * unit_vector[0]
        force_y = (force_constant / magnitude ** 2) * unit_vector[1]
        return (force_x, force_y)

    def calculate_total_force(self, particles: list['Particle']) -> None:
        sum_force_x = self.force_vector[0]
        sum_force_y = self.force_vector[1]

        for particle in particles:
            force = self.calculate_force(particle)
            sum_force_x += force[0]
            sum_force_y += force[1]

        self.force_vector = (sum_force_x, sum_force_y)
            
    
       

screen = Screen()    

num_particles = 3

#particles = [Particle(random.uniform(50, 950),
#                      random.uniform(50, 950),
#                      random.uniform(-100, 100),
#                      random.uniform(-100, 100),
#                      True) for _ in range(num_particles)]

particles = [
        #Particle(400, 400, 0, 0, True),
        #Particle(500, 900, 0, 0, True),
        #Particle(600, 600, 0, 0, True),

        Particle(400, 600, 0, 0, True),
        Particle(500, 900, 0, 0, True),
        Particle(600, 400, 0, 0, True),
        ]

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
        p.draw(screen)



    pygame.display.flip()
    screen.clock.tick(60)

    # Check for exit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

