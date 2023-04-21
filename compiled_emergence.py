#!/usr/bin/env python3.10
import pygame
import random
from enum import Enum
import numpy as np
from numba import njit, typed, int32, float32, prange
from numba.experimental import jitclass


class Color(Enum):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    magenta = (255, 0, 255)

class NumericalMethod(Enum):
    euler = 0
    leapfrog = 1


class Screen:
    screen_min: np.ndarray = np.array([0.0, 0.0], dtype=np.float32)
    screen_max: np.ndarray = np.array([1200.0, 1000.0], dtype=np.float32)

    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode((float(Screen.screen_max[0]), float(Screen.screen_max[1])))
        pygame.display.set_caption("Emergent Phenomena Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

    def fill(self) -> None:
        self.surface.fill((0, 0, 0))

    def get_time(self) -> int:
        return self.clock.get_time()

    def update_fps(self):
        fps = 'Fps: ' + str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, False, pygame.Color("white"))
        return fps_text

    def number_of_particles(self, number_of_particles):
        fps_text = self.font.render('Particles: ' + str(number_of_particles), False, pygame.Color("white"))
        return fps_text


spec = [
        ('screen_max', float32[:]),
        ('position_vector', float32[:]),
        ('velocity_vector', float32[:]),
        ('force_vector', float32[:]),
        ('previous_force_vector', float32[:]),
        ('time_delta', float32),
        ('method', int32),
        ('radius', float32),
        ('color', int32),
        ('max_velocity', float32),
        ('epsilon', float32),
        ('mult', float32),
        ('slice', int32),
    ]

@jitclass(spec)
class Particle(object):
    def __init__(
            self,
            screen_max: np.ndarray,
            position_vector: np.ndarray,
            velocity_vector: np.ndarray,
            color: int,
            time_delta: float,
            method: int = 1,
        ) -> None:

        self.screen_max: np.ndarray = screen_max
        self.position_vector: np.ndarray = position_vector
        self.velocity_vector: np.ndarray = velocity_vector
        self.force_vector: np.ndarray = np.array([0, 0], dtype=np.float32)
        self.previous_force_vector: np.ndarray = np.array([0, 0], dtype=np.float32)
        self.time_delta: float = time_delta
        self.method: int = method
        self.color: int = color
        self.radius: float = 2.0
        self.max_velocity: float = 1000.0
        self.epsilon: float = 1e-7
        self.mult: float = 5.0
        self.slice: int = 10

    def __magnitude(self, vector: np.ndarray) -> np.float32:
        return np.float32(0.1 * (vector[0]**2 + vector[1]**2) ** 0.5 + self.epsilon)

    def __handle_walls(self) -> None:
        for i in range(len(self.position_vector)):
            if self.position_vector[i] < 0:
                self.position_vector[i] = 0 + self.epsilon
                self.velocity_vector[i] *= -1.0
            elif self.position_vector[i] > self.screen_max[i]:
                self.position_vector[i] = self.screen_max[i] - self.epsilon
                self.velocity_vector[i] *= -1.0

    def __handle_max_velocity(self) -> None:
        for i in range(len(self.velocity_vector)):
            if self.velocity_vector[i] >= self.max_velocity:
                self.velocity_vector[i] = self.max_velocity
            elif self.velocity_vector[i] <= -self.max_velocity:
                self.velocity_vector[i] = -self.max_velocity

    def __eulers_method_position(self) -> None:
        self.position_vector = self.position_vector + self.velocity_vector * self.time_delta
        self.__handle_walls()

    def __eulers_method_velocity(self) -> None:
        self.velocity_vector = self.velocity_vector + self.force_vector * self.time_delta
        self.__handle_max_velocity()

    def __leapfrog_position(self) -> None:
        self.position_vector = (self.position_vector 
                                + (self.velocity_vector * self.time_delta) 
                                + (0.5 * self.force_vector * self.time_delta**2)).astype(np.float32)
        self.__handle_walls()

    def __leapfrog_velocity(self) -> None:
        self.velocity_vector = (self.velocity_vector 
                                + 0.5 * (self.previous_force_vector + self.force_vector) 
                                * self.time_delta).astype(np.float32)
        self.__handle_max_velocity()

    def set_position(self) -> None:
        if self.method == 0:
            self.__eulers_method_position()

        if self.method == 1:
            self.__leapfrog_position()

    def set_velocity(self) -> None:
        if self.method == 0:
            self.__eulers_method_velocity()

        if self.method == 1:
            self.previous_force_vector = self.force_vector
            self.__leapfrog_velocity()

    def set_total_force(self, particles: list['Particle']) -> None:
        self.force_vector = np.zeros(2, dtype=np.float32)
        for particle in particles[:self.slice]:
            self.force_vector = self.force_vector + self.__calculate_force(particle).astype(np.float32)

    # TODO not working
    def __calculate_parameters(self, other_particle: 'Particle') -> np.ndarray:
        position_delta = self.position_vector - other_particle.position_vector
        r = self.__magnitude(position_delta)
        unit_vector = position_delta / r
        return np.array([r, unit_vector], dtype=np.float32)
             
    def __calculate_force(self, other_particle: 'Particle') -> np.ndarray:
        position_delta = self.position_vector - other_particle.position_vector
        r = self.__magnitude(position_delta)
        unit_vector = position_delta / r
        
        # red
        if (self.color == 0):
            if (other_particle.color == 0):
                return np.zeros(2, dtype=np.float32)
            elif (other_particle.color == 1):
                if r > 5 * self.radius:
                    return -unit_vector * r * self.mult
                else:
                    return unit_vector * r**2 * self.mult
            elif (other_particle.color == 2):
                return unit_vector**2 * self.mult
        # green
        if (self.color == 1):
            if (other_particle.color == 0):
                return np.zeros(2, dtype=np.float32)
            elif (other_particle.color == 1):
                return np.zeros(2, dtype=np.float32)
            elif (other_particle.color == 2):
                return np.zeros(2, dtype=np.float32)
            else:
                if r > 10 * self.radius:
                    return -unit_vector * r * self.mult
                else:
                    return -unit_vector * r**3 * self.mult
        # blue
        if (self.color == 2):
            if (other_particle.color == 0):
                return np.zeros(2, dtype=np.float32)
            elif (other_particle.color == 1):
                if r > 5 * self.radius:
                    return -unit_vector * r * self.mult
                else:
                    return unit_vector * r**3 * self.mult
            elif (other_particle.color == 2):
                return np.zeros(2, dtype=np.float32)
            else:
                return -unit_vector * r * self.mult
        # magenta
        if (self.color == 3):
            if (other_particle.color == 2):
                return np.zeros(2, dtype=np.float32)
            elif (other_particle.color == 1):
                if r > 10 * self.radius:
                    return -unit_vector * r * self.mult
                else:
                    return unit_vector * r**3 * self.mult
            else:
                return np.zeros(2, dtype=np.float32)
 
        return np.zeros(2, dtype=np.float32)


def draw(position_vector: np.ndarray, color: int, screen: Screen, radius) -> None:
    position_tuple = (float(position_vector[0]), float(position_vector[1]))
    end_tuple = (float(position_vector[0]), float(position_vector[1] - 1.0))

    if (color == 0):
        colorValue = Color.red
    elif (color == 1):
        colorValue = Color.green
    elif (color == 2):
        colorValue = Color.blue
    else:
        colorValue = Color.magenta

    pygame.draw.line(screen.surface, colorValue.value, position_tuple, end_tuple, int(radius))

def draw_particles(particles: list[Particle], screen: Screen) -> None:
    for particle in particles:
        draw(particle.position_vector, particle.color, screen, particle.radius)

@njit(fastmath=True, parallel=True)
def perform_computations(particles: list[Particle]) -> None:
    for i in prange(len(particles)):
        particles[i].set_position()
        particles[i].set_velocity()
        particles[i].set_total_force(typed.List(particles))

def main():
    screen = Screen()    
    time_delta = 0.005
    method = NumericalMethod.leapfrog
    num_particles = 1500

    particles = [Particle(
        screen_max = screen.screen_max,
        position_vector = (np.random.rand(1, 2)[0] * screen.screen_max).astype(np.float32),
        velocity_vector = ((np.random.rand(1, 2)[0] * 500) - 250).astype(np.float32),
        color = random.choice([0, 1, 2, 3]),
        time_delta = time_delta,
        method = method.value) for _ in range(num_particles)]

    running = True
    while running:
        screen.fill()
        screen.surface.blit(screen.update_fps(), (10, 25))
        screen.surface.blit(screen.number_of_particles(num_particles), (10, 0))

        perform_computations(typed.List(particles))
        draw_particles(particles, screen)

        pygame.display.flip()
        screen.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()

