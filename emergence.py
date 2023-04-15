import pygame
import random
from enum import Enum
import numpy as np


class Color(Enum):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)


class NumericalMethod(Enum):
    euler = 1
    leapfrog = 2


class Screen:
    screen_min: np.ndarray = np.array([0.0, 0.0])
    screen_max: np.ndarray = np.array([1000.0, 1000.0])

    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode((Screen.screen_max[0], Screen.screen_max[1]))
        pygame.display.set_caption("Emergent Phenomena Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

    def fill(self) -> None:
        self.surface.fill((0, 0, 0))

    def get_time(self) -> int:
        return self.clock.get_time()

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, False, pygame.Color("white"))
        return fps_text


class Particle:
    radius: float = 5.0
    mass: float = 1.0
    max_velocity: float = 1000.0
    epsilon: float = 1e-9

    def __init__(
            self,
            screen: Screen,
            position_vector: np.ndarray,
            velocity_vector: np.ndarray,
            time_delta: float,
            method: NumericalMethod = NumericalMethod.euler,
            draw_force_vector: bool = True,
            label: str = "",
        ) -> None:

        self.screen: Screen = screen
        self.position_vector: np.ndarray = position_vector
        self.velocity_vector: np.ndarray = velocity_vector
        self.force_vector: np.ndarray = np.array([0, 0])
        self.previous_force_vector: np.ndarray = np.array([0, 0])

        self.time_delta: float = time_delta
        self.method: NumericalMethod = method

        self.color: str = self.__random_color()
        self.draw_force_vector: bool = draw_force_vector
        self.label: str = label

    @staticmethod
    def __random_color() -> str:
        return random.choice(list(Color.__members__))

    @staticmethod
    def __magnitude(vector: np.ndarray) -> float:
        r = sum(i ** 2 for i in vector) ** 0.5
        return r if r >= Particle.epsilon else Particle.epsilon

    def __handle_walls(self) -> None:
        for i in range(len(self.position_vector)):
            if self.position_vector[i] < 0:
                self.position_vector[i] = 0 + Particle.epsilon
                self.velocity_vector[i] *= -1.0
            elif self.position_vector[i] > self.screen.screen_max[i]:
                self.position_vector[i] = self.screen.screen_max[i] - Particle.epsilon
                self.velocity_vector[i] *= -1.0

    def __handle_max_velocity(self) -> None:
        for i in range(len(self.velocity_vector)):
            if self.velocity_vector[i] >= Particle.max_velocity:
                self.velocity_vector[i] = Particle.max_velocity
            elif self.velocity_vector[i] <= -Particle.max_velocity:
                self.velocity_vector[i] = -Particle.max_velocity

    def __eulers_method_position(self) -> None:
        self.position_vector = self.position_vector + self.velocity_vector * self.time_delta
        self.__handle_walls()

    def __eulers_method_velocity(self) -> None:
        self.velocity_vector = self.velocity_vector + self.force_vector * self.time_delta
        self.__handle_max_velocity()

    def __leapfrog_position(self) -> None:
        self.position_vector = self.position_vector + (self.velocity_vector * self.time_delta) + (0.5 * self.force_vector * self.time_delta**2)
        self.__handle_walls()

    def __leapfrog_velocity(self) -> None:
        self.velocity_vector = self.velocity_vector + 0.5 * (self.previous_force_vector + self.force_vector) * self.time_delta
        self.__handle_max_velocity()

    def draw(self) -> None:
        position_tuple = (self.position_vector[0], self.position_vector[1])
        pygame.draw.circle(self.screen.surface, self.color, position_tuple, Particle.radius)
 
        if self.draw_force_vector:
            ndarray_end_position = self.position_vector + self.force_vector
            end_position = (ndarray_end_position[0], ndarray_end_position[1])
            pygame.draw.line(self.screen.surface, self.color, position_tuple, end_position)

    def calculate_position(self, particles: list['Particle']) -> None:
        self.__calculate_velocity(particles)

        if self.method == NumericalMethod.euler:
            self.__eulers_method_position()
        if self.method == NumericalMethod.leapfrog:
            self.__leapfrog_position()

    def __calculate_velocity(self, particles: list['Particle']) -> None:
        self.previous_force_vector = self.force_vector
        self.__calculate_total_force(particles)

        if self.method == NumericalMethod.euler:
            self.__eulers_method_velocity()
        if self.method == NumericalMethod.leapfrog:
            self.__leapfrog_velocity()
 
    def __calculate_total_force(self, particles: list['Particle']) -> None:
        self.force_vector = np.array([0, 0])
        for particle in particles:
            self.force_vector = self.force_vector + self.__calculate_force(particle)
            
    def __calculate_force(self, other_particle: 'Particle') -> np.ndarray:
        force_constant = -1000000.0
        position_delta = self.position_vector - other_particle.position_vector
        r = self.__magnitude(position_delta)
        unit_vector = np.array([position_delta[0] / r, position_delta[1] / r])
        return unit_vector * (force_constant / r**2)


def main():
    screen = Screen()    
    time_delta = 0.016
    method = NumericalMethod.leapfrog
 
    particles = [
        Particle(screen, np.array([400.0, 400.0]), np.array([0.0, 0.0]), time_delta, draw_force_vector = True, method=method),
        Particle(screen, np.array([600.0, 400.0]), np.array([0.0, 0.0]), time_delta, draw_force_vector = True, method=method),
    ]

    running = True
    while running:
        screen.fill()
        screen.surface.blit(screen.update_fps(), (10,0))

        for i in range(len(particles)):
            sublist = particles[:i] + particles[i + 1:]
            particles[i].calculate_position(sublist)
            particles[i].draw()

        pygame.display.flip()
        screen.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()

