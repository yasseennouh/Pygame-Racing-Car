import pygame
import random
from sys import exit as sys_exit

pygame.init()
pygame.mixer.init()


class Cars:
    def __init__(self, screen_width, screen_height):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_width, screen_height
        self.speed_factor = self.SCREEN_HEIGHT / 660
        self.car_lane = "R"
        self.car2_lane = "L"
        self.speed = 3

        self.original_car = pygame.image.load("assets/car.png")
        self.car = pygame.transform.scale(
            self.original_car,
            (
                int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car_rect = self.car.get_rect()
        self.car_rect.center = (
            self.SCREEN_WIDTH / 2 + self.SCREEN_WIDTH / 8,
            self.SCREEN_HEIGHT - self.car_rect.height * 0.5,
        )

        self.original_car2 = pygame.image.load("assets/otherCar.png")
        self.car2 = pygame.transform.scale(
            self.original_car2,
            (
                int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car2_rect = self.car2.get_rect()
        self.car2_rect.center = self.SCREEN_WIDTH / 2 - self.SCREEN_WIDTH / 8, self.SCREEN_HEIGHT * 0.2

    def update(self):
        self.car2_rect.y += self.speed * self.speed_factor

        if self.car2_rect.y > self.SCREEN_HEIGHT:
            if random.randint(0, 1) == 0:
                self.car2_rect.center = (
                    self.SCREEN_WIDTH / 2 + self.SCREEN_WIDTH / 8,
                    -self.car2_rect.height,
                )
                self.car2_lane = "R"
            else:
                self.car2_rect.center = (
                    self.SCREEN_WIDTH / 2 - self.SCREEN_WIDTH / 8,
                    -self.car2_rect.height,
                )
                self.car2_lane = "L"


class Road:
    def __init__(self, screen, road_width, roadmark_width, speed, speed_factor):
        self.screen = screen
        self.road_width = road_width
        self.roadmark_width = roadmark_width
        self.speed = speed
        self.speed_factor = speed_factor

    def draw(self, event_updater_counter):
        self.screen.fill((60, 220, 0))
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            (self.screen.get_width() / 2 - self.road_width / 2, 0, self.road_width, self.screen.get_height()),
        )
        self.draw_yellow_dashed_line(event_updater_counter)
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (
                self.screen.get_width() / 2 + self.road_width / 2 - self.roadmark_width * 3,
                0,
                self.roadmark_width,
                self.screen.get_height(),
            ),
        )

    def draw_yellow_dashed_line(self, event_updater_counter):
        num_yellow_lines = 11
        line_positions = [
            (
                self.screen.get_width() / 2 - self.roadmark_width / 2,
                int(
                    (self.screen.get_height() / 20
                    + 2 * self.screen.get_height() / 20 * num_line
                    + self.speed * self.speed_factor * event_updater_counter * 0.75)
                    % (self.screen.get_height() / 10 * 11)
                    - self.screen.get_height() / 20
                ),
                self.roadmark_width,
                self.screen.get_height() / 20,
            )
            for num_line in range(num_yellow_lines)
        ]

        for line_position in line_positions:
            pygame.draw.rect(self.screen, (255, 240, 60), line_position)



class ScoreManager:
    def __init__(self, high_scores_file="high_scores.txt"):
        self.high_scores_file = high_scores_file
        self.scores = []
        self.has_update_scores = False

    def update_high_scores(self, new_score):
        with open(self.high_scores_file, "r") as hs_file:
            high_scores = hs_file.read()
            hs_file.close()

        self.scores = [int(i) for i in high_scores.split()]
        self.scores.append(new_score)

        self.scores.sort(reverse=True)

        if len(self.scores) > 5:
            self.scores = self.scores[:5]

        with open(self.high_scores_file, "w") as hs_file:
            hs_file.write(" ".join(map(str, self.scores)))

        self.has_update_scores = True

    def get_high_scores(self):
        if not self.has_update_scores:
            self.update_high_scores(0)

        return self.scores


class CarGame:
    def __init__(self):
        self.initialize_pygame()
        self.initialize_screen()
        self.initialize_fonts()
        self.initialize_sound_effects()
        self.initialize_game_parameters()
        self.initialize_road()
        self.initialize_cars()
        self.initialize_score_manager()
        self.speed = 3


    def initialize_pygame(self):
        pygame.init()
        pygame.mixer.init()

    def initialize_screen(self):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 660
        self.SCREEN = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("2D Car Game")

    def initialize_fonts(self):
        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.score_font = pygame.font.Font("assets/fonts/joystix monospace.otf", 30)

    def initialize_sound_effects(self):
        self.car_crash_sound = pygame.mixer.Sound("assets/carCrash.wav")

    def initialize_game_parameters(self):
        self.FPS = 60
        self.speed_factor = self.SCREEN_HEIGHT / 660
        self.event_updater_counter = 0
        self.game_state = "MAIN GAME"
        self.score = 0
        self.level = 0
        self.CLOCK = pygame.time.Clock()
        self.speed = 3  # Add this line to define the speed attribute

    def initialize_cars(self):
        self.cars = Cars(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def initialize_road(self):
        self.road = Road(
            self.SCREEN,
            int(self.SCREEN_WIDTH / 1.6),
            self.SCREEN_WIDTH // 80,
            self.speed,  # Add the speed parameter
            self.speed_factor
        )

    def initialize_score_manager(self):
        self.score_manager = ScoreManager()

    def main_loop(self):
        while True:
            self.event_loop()
            self.event_updater_counter += 1

            if self.event_updater_counter > self.SCREEN_HEIGHT:
                self.event_updater_counter = 0

            if self.game_state == "GAME OVER":
                self.game_over_draw()
                pygame.display.update()
                self.CLOCK.tick(self.FPS)
                continue

            # Update game elements
            self.cars.update()

            # Render game elements
            self.road.draw(self.event_updater_counter)  # Updated this line
            # Render cars
            self.SCREEN.blit(self.cars.car, self.cars.car_rect)
            self.SCREEN.blit(self.cars.car2, self.cars.car2_rect)

            # Update the game state and check for collisions
            self.update_game_state()
            self.display_score()

            self.score += 1

            self.CLOCK.tick(self.FPS)
            pygame.display.update()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                self.handle_key_events(event)
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize_event(event)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.game_state == "GAME OVER":
            self.restart_game()

    def handle_key_events(self, event):
        road_boundary_left = self.SCREEN_WIDTH / 2 - self.road.road_width / 2
        road_boundary_right = self.SCREEN_WIDTH / 2 + self.road.road_width / 2 - self.cars.car_rect.width

        if event.key in [pygame.K_a, pygame.K_LEFT] and self.cars.car_lane == "R":
            if self.cars.car_rect.x > road_boundary_left:
                self.cars.car_rect.move_ip(-int(self.road.road_width / 2), 0)
                self.cars.car_lane = "L"
        if event.key in [pygame.K_d, pygame.K_RIGHT] and self.cars.car_lane == "L":
            if self.cars.car_rect.x < road_boundary_right:
                self.cars.car_rect.move_ip(int(self.road.road_width / 2), 0)
                self.cars.car_lane = "R"

    def handle_resize_event(self, event):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = event.w, event.h
        self.SCREEN = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
        )
        self.road = Road(self.SCREEN_WIDTH, int(self.SCREEN_WIDTH / 1.6), self.speed_factor)
        self.cars.car_rect.move_ip(self.SCREEN_WIDTH / 2 - self.cars.car_rect.width / 2, 0)
        self.cars.car2_rect.move_ip(self.SCREEN_WIDTH / 2 - self.SCREEN_WIDTH / 8, self.SCREEN_HEIGHT * 0.2)

    def update_game_state(self):
        if self.game_state == "MAIN GAME":
            self.update_main_game_state()

    def update_main_game_state(self):
        if self.score % 5000 == 0:
            self.level_up()

        self.move_enemy_car()

        if self.cars.car2_rect.y > self.SCREEN_HEIGHT:
            self.reset_enemy_car()

        if self.cars.car2_rect.colliderect(self.cars.car_rect):
            self.handle_collision()

            self.move_enemy_car()

            if self.cars.car2_rect.y > self.SCREEN_HEIGHT:
                self.reset_enemy_car()

            if self.cars.car2_rect.colliderect(self.cars.car_rect):
                self.handle_collision()

    def level_up(self):
        self.speed += 0.16
        self.level += 1
        print("Level Up!")
    def display_score(self):
        self.message_display(
            "SCORE ",
            (255, 50, 50),
            self.SCREEN_WIDTH / 2 + self.road.road_width / 2.5,
            20,
        )
        self.message_display(
            self.score,
            (255, 50, 50),
            self.SCREEN_WIDTH / 2 + self.road.road_width / 2.5, 
            55,
        )

    def move_enemy_car(self):
        self.cars.car2_rect.y += self.speed * self.speed_factor

    def reset_enemy_car(self):
        if random.randint(0, 1) == 0:
            self.cars.car2_rect.center = (
                self.SCREEN_WIDTH / 2 + self.SCREEN_WIDTH / 8,
                -self.cars.car2_rect.height,
            )
            self.cars.car2_lane = "R"
        else:
            self.cars.car2_rect.center = (
                self.SCREEN_WIDTH / 2 - self.SCREEN_WIDTH / 8,
                -self.cars.car2_rect.height,
            )
            self.cars.car2_lane = "L"

    def handle_collision(self):
        self.car_crash_sound.play()
        self.game_state = "GAME OVER"

    def game_over_draw(self):
        self.SCREEN.fill((200, 200, 200))
        self.message_display("GAME OVER!", (40, 40, 40), self.SCREEN_WIDTH / 2, 330)
        self.message_display("FINAL SCORE ", (80, 80, 80), self.SCREEN_WIDTH / 2 - 100, 230)
        self.message_display(self.score, (80, 80, 80), self.SCREEN_WIDTH / 2 + 100, 230)

        self.display_high_scores()

        if not self.score_manager.has_update_scores:
            self.score_manager.update_high_scores(self.score)

    def display_high_scores(self):
        self.message_display(
            "HIGH SCORES", (100, 100, 100), self.SCREEN_WIDTH / 2, 410
        )

        for idx, score in enumerate(self.score_manager.get_high_scores()):
            self.message_display(
                f"{idx + 1}. {score}",
                (100, 100, 100),
                self.SCREEN_WIDTH / 2,
                410 + ((idx + 1) * 30),
            )

        self.message_display(
            "(Space to restart)", (80, 80, 80), self.SCREEN_WIDTH / 2, 600
        )

    def restart_game(self):
        self.initialize_game_parameters()
        road_boundary_left = self.SCREEN_WIDTH / 2 - self.road.road_width / 2
        self.cars.car_rect.move_ip(road_boundary_left, self.SCREEN_HEIGHT - self.cars.car_rect.height * 0.5)
        self.reset_enemy_car()
        self.cars.car_lane = "R"
        self.cars.car2_lane = "L"
        print("Restart!")

    @staticmethod
    def quit_game():
        sys_exit()

    def message_display(self, text, text_col, x, y, center=True):
        img = self.score_font.render(str(text), True, text_col)
        img = img.convert_alpha()

        if center:
            x -= img.get_width() / 2
            y -= img.get_height() / 2

        self.SCREEN.blit(img, (x, y))


if __name__ == "__main__":
    game = CarGame()
    game.main_loop()
