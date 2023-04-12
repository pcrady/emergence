import pygame
import random
import math

# Define Particle class
class Particle:
    def __init__(self, x, y, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.radius = 20
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = self.random_color()

    def move(self, time_delta):
        self.x += self.velocity_x * time_delta
        self.y += self.velocity_y * time_delta

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move_to(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def random_color():
        allowed_colors = [
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 255, 0)  # Yellow
        ]
        return random.choice(allowed_colors)


# Initialize Pygame
pygame.init()
x_screen = 800
y_screen = 600
screen = pygame.display.set_mode((x_screen, y_screen))
pygame.display.set_caption("Particle Collision Simulation")
clock = pygame.time.Clock()

# Create particles
num_particles = 20
particles = [Particle(random.uniform(50, 750),
                      random.uniform(50, 550),
                      random.uniform(-200, 200),
                      random.uniform(-200, 200)) for _ in range(num_particles)]

# Main simulation loop
running = True
while running:
    screen.fill((255, 255, 255))

    # Draw and update particle positions
    for p in particles:
        p.move(clock.get_time() / 1000)
        p.draw(screen)

    # Detect and resolve collisions
    for i in range(num_particles):
        x_left_edge = particles[i].x - particles[i].radius;
        y_top_edge = particles[i].y + particles[i].radius;

        x_right_edge = particles[i].x + particles[i].radius;
        y_bottom_edge = particles[i].y - particles[i].radius;

        padding = 1
        if x_left_edge < 0 or x_right_edge >= x_screen:
            particles[i].velocity_x = particles[i].velocity_x * -1.0
            particles[i].x += padding if x_left_edge < 0 else -padding
 
        if y_bottom_edge < 0 or y_top_edge >= y_screen:
            particles[i].velocity_y = particles[i].velocity_y * -1.0
            particles[i].y += padding if y_bottom_edge < 0 else -padding

        for j in range(i + 1, num_particles):
            dx = particles[i].x - particles[j].x
            dy = particles[i].y - particles[j].y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < particles[i].radius + particles[j].radius:

                normal_x, normal_y = dx / distance, dy / distance
                tangent_x, tangent_y = -normal_y, normal_x
                vi_normal = particles[i].velocity_x * normal_x + particles[i].velocity_y * normal_y
                vi_tangent = particles[i].velocity_x * tangent_x + particles[i].velocity_y * tangent_y
                vj_normal = particles[j].velocity_x * normal_x + particles[j].velocity_y * normal_y
                vj_tangent = particles[j].velocity_x * tangent_x + particles[j].velocity_y * tangent_y

                # Swap normal velocities
                particles[i].velocity_x = vi_tangent * tangent_x + vj_normal * normal_x
                particles[i].velocity_y = vi_tangent * tangent_y + vj_normal * normal_y
                particles[j].velocity_x = vj_tangent * tangent_x + vi_normal * normal_x
                particles[j].velocity_y = vj_tangent * tangent_y + vi_normal * normal_y

                # Separate overlapping particles
                overlap = 0.5 * (particles[i].radius + particles[j].radius - distance + 1)
                particles[i].move_to(particles[i].x + normal_x * overlap, particles[i].y + normal_y * overlap)
                particles[j].move_to(particles[j].x - normal_x * overlap, particles[j].y - normal_y * overlap)

    pygame.display.flip()
    clock.tick(60)

    # Check for exit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

