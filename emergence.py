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
    runge_kutta = 3


class Screen:
    screen_min: np.ndarray = np.array([0.0, 0.0])
    screen_max: np.ndarray = np.array([2000.0, 2000.0])

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
    epsilon: float = 1e-3

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

        self.color: Color = self.__random_color()
        self.draw_force_vector: bool = draw_force_vector
        self.label: str = label

    @staticmethod
    def __random_color() -> Color:
        return random.choice([Color.red, Color.green, Color.blue])

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
        pygame.draw.circle(self.screen.surface, self.color.value, position_tuple, Particle.radius)
 
        if self.draw_force_vector:
            size_multiplier = 1
            ndarray_end_position = self.position_vector + (self.force_vector) * size_multiplier
            end_position = (ndarray_end_position[0], ndarray_end_position[1])
            pygame.draw.line(self.screen.surface, self.color.value, position_tuple, end_position)

    def set_position(self) -> None:
        if self.method == NumericalMethod.euler:
            self.__eulers_method_position()

        if self.method == NumericalMethod.leapfrog:
            self.__leapfrog_position()

    def set_velocity(self) -> None:
        if self.method == NumericalMethod.euler:
            self.__eulers_method_velocity()

        if self.method == NumericalMethod.leapfrog:
            self.previous_force_vector = self.force_vector
            self.__leapfrog_velocity()

    def set_total_force(self, particles: list['Particle']):
        self.force_vector = self.__calculate_total_force(particles)
 
    def __calculate_total_force(self,  particles: list['Particle']) -> np.ndarray:
        force_vector = np.array([0, 0])
        for particle in particles:
            force_vector = force_vector + self.__calculate_force(particle)
        return force_vector
            
    def __calculate_force(self, other_particle: 'Particle') -> np.ndarray:
        position_delta = self.position_vector - other_particle.position_vector
        r = self.__magnitude(position_delta)
        unit_vector = np.array([position_delta[0] / r, position_delta[1] / r])

        if ((self.color == Color.green) & (self.color == other_particle.color)):
            return np.zeros(2)
        elif ((self.color == Color.green) & (other_particle.color == Color.red)):
            return np.zeros(2)
        elif ((self.color == Color.green) & (other_particle.color == Color.blue)):
            if r > 10 * Particle.radius:
                return -unit_vector * r
            else:
                return unit_vector * r**4

        elif ((self.color == Color.red) & (self.color == other_particle.color)):
            return np.zeros(2)
        elif ((self.color == Color.red) & (other_particle.color == Color.green)):
            if r > 10 * Particle.radius:
                return -unit_vector * r
            else:
                return unit_vector * r**4
        elif ((self.color == Color.red) & (other_particle.color == Color.blue)):
            return np.zeros(2)

        elif ((self.color == Color.blue) & (self.color == other_particle.color)):
            return np.zeros(2)
        elif ((self.color == Color.blue) & (other_particle.color == Color.red)):
            if r <= 15 * Particle.radius:
                return -unit_vector * r**3
            else: 
                return np.zeros(2)
        elif ((self.color == Color.blue) * (other_particle.color == Color.green)):
            return np.zeros(2)
        else:
            return np.zeros(2)


def main():

    screen = Screen()    
    time_delta = 0.005
    method = NumericalMethod.leapfrog
    num_particles = 100
    particles = [Particle(
        screen,
        np.random.rand(1, 2)[0] * screen.screen_max,
        (np.random.rand(1, 2)[0] * 500) - 250,
        time_delta,
        draw_force_vector = False,
        method = method) for _ in range(num_particles)]

    running = True
    while running:
        screen.fill()
        screen.surface.blit(screen.update_fps(), (10,0))

        for i in range(len(particles)):
            sublist = particles[:i] + particles[i + 1:]
            particles[i].set_position()
            particles[i].set_velocity()
            particles[i].set_total_force(sublist)
            particles[i].draw()

        pygame.display.flip()
        screen.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()

