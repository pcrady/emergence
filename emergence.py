import pygame
import random
from enum import Enum
import numpy as np


class Color(Enum):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)


class Screen:
    screen_min: np.ndarray = np.array([0.0, 0.0])
    screen_max: np.ndarray = np.array([1000.0, 1000.0])

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Screen.screen_max[0], Screen.screen_max[1]))
        pygame.display.set_caption("Emergent Phenomena Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

    def fill(self) -> None:
        self.screen.fill((0, 0, 0))

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
            position_vector: np.ndarray,
            velocity_vector: np.ndarray,
            draw_force_vector: bool = True,
            label: str = "") -> None:

        self.position_vector: np.ndarray = position_vector
        self.velocity_vector: np.ndarray = velocity_vector
        self.force_vector: np.ndarray = np.array([0, 0])

        self.color: str = self.__random_color()
        self.draw_force_vector: bool = draw_force_vector
        self.label = label

    @staticmethod
    def __random_color() -> str:
        return random.choice(list(Color.__members__))

    @staticmethod
    def __magnitude(vector: np.ndarray) -> float:
        r = sum(i ** 2 for i in vector) ** 0.5
        return r if r >= Particle.epsilon else Particle.epsilon

    @property
    def __unit_velocity_vector(self) -> np.ndarray:
        return self.velocity_vector / self.__magnitude(self.velocity_vector)

    def __handle_walls(self, position: np.ndarray, screen: 'Screen') -> None:
        for i in range(len(position)):
            if position[i] < 0:
                self.position_vector[i] = 0 + Particle.epsilon
                self.velocity_vector[i] *= -1.0
            elif position[i] > screen.screen_max[i]:
                self.position_vector[i] = screen.screen_max[i] - Particle.epsilon
                self.velocity_vector[i] *= -1.0
            else:
                self.position_vector[i] = position[i]

    def __handle_max_velocity(self, velocity: np.ndarray) -> None:
        velocity_tmp = velocity

        for i in range(len(velocity)):
            if velocity[i] >= Particle.max_velocity:
                velocity_tmp[i] = Particle.max_velocity
            elif velocity[i] <= -Particle.max_velocity:
                velocity_tmp[i] = -Particle.max_velocity

        self.velocity_vector = velocity_tmp

    def draw(self, screen: 'Screen') -> None:
        position_tuple = (self.position_vector[0], self.position_vector[1])
        pygame.draw.circle(screen.screen, self.color, position_tuple, Particle.radius)
 
        if self.draw_force_vector:
            ndarray_end_position = self.position_vector + self.force_vector
            end_position = (ndarray_end_position[0], ndarray_end_position[1])
            pygame.draw.line(screen.screen, self.color, position_tuple, end_position)

    def calculate_position(
            self,
            time_delta: float,
            screen: 'Screen',
            particles: list['Particle'],
            ) -> None:

        self.__calculate_velocity(time_delta, particles)
        position = self.position_vector + self.velocity_vector * time_delta
        self.__handle_walls(position, screen)

    def __calculate_velocity(self, time_delta: float, particles: list['Particle']) -> None:
        self.__calculate_total_force(particles)
        velocity = self.velocity_vector + self.force_vector * time_delta
        self.__handle_max_velocity(velocity)
 
    def __calculate_total_force(self, particles: list['Particle']) -> None:
        force = np.array([0, 0])
        for particle in particles:
            force = force + self.__calculate_force(particle)
        self.force_vector = force
            
    def __calculate_force(self, other_particle: 'Particle') -> np.ndarray:
        force_constant = -1000000.0
        position_delta = self.position_vector - other_particle.position_vector

        r = self.__magnitude(position_delta)
        unit_vector = np.array([position_delta[0] / r, position_delta[1] / r])
        return unit_vector * (force_constant / r**2)


def main():
    screen = Screen()    

    particles = [
        Particle(np.array([400.0, 400.0]), np.array([0.0, 0.0]), True, "Upper"),
        Particle(np.array([600.0, 400.0]), np.array([0.0, 0.0]), True, "Lower"),
        ]

    running = True
    while running:
        screen.fill()
        screen.screen.blit(screen.update_fps(), (10,0))

        time_delta = screen.get_time() / 1000

        for i in range(len(particles)):
            sublist = particles[:i] + particles[i + 1:]
            particles[i].calculate_position(time_delta, screen, sublist)
            particles[i].draw(screen)

        pygame.display.flip()
        screen.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()

