import pygame, sys
from Player import Player
import Obstacle
from Alien import Alien, Extra
from Laser import Laser
from random import choice, randint
import os

# Импорт файла (изменяет каталог на место, где сохранен файл)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class CRT:
    def __init__(self):
        self.tv = pygame.image.load("../Graphics/TV.png").convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screen_width, screen_height))
        self.crt_lines = self.create_crt_lines()

    def create_crt_lines(self):
        crt_surface = self.tv.copy()
        line_height = 4
        line_amount = int(screen_height / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(crt_surface, "Black", (0, y_pos), (screen_width, y_pos), 1)
        return crt_surface

    def draw(self):
        self.tv.set_alpha(randint(75, 90))
        screen.blit(self.crt_lines, (0, 0))

def authenticate(screen, font):
    correct_password = "test"  # Пароль для аутентификации
    input_box = pygame.Rect(200, 300, 240, 37)
    color_inactive = pygame.Color('green')
    color_active = pygame.Color('white')
    color = color_inactive
    active = False
    text = ''
    done = False
    attempts = 3

    cursor_visible = True
    cursor_timer = 0

    # Создание CRT эффекта
    crt = CRT()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Если пользователь нажал на прямоугольник input_box.
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                # Изменение текущего цвета поля ввода.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text == correct_password:
                            print("Аутентификация успешна.")
                            return True
                        else:
                            attempts -= 1
                            print(f"Неверный пароль. Осталось попыток: {attempts}")
                            text = ''
                            if attempts <= 0:
                                print("Аутентификация не удалась.")
                                return False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        crt.draw()  # Рисование CRT эффекта

        # Отображение текста ввода
        txt_surface = font.render(text, True, color)
        screen.blit(txt_surface, (input_box.x + 9, input_box.y - 15))
        pygame.draw.rect(screen, color, input_box, 2)

        # Заголовок окна
        pygame.display.set_caption("Аутентификация")
        pygame_icon = pygame.image.load("../Graphics/Key.png")
        pygame.display.set_icon(pygame_icon)

        # Сообщение "Введите пароль"
        message_surface = font.render("Введите пароль:", True, pygame.Color('#ffffff'))
        screen.blit(message_surface, (180, 250))

        # Отображение оставшихся попыток
        attempts_message = f"Осталось попыток: {attempts}/3"
        attempts_surface = font.render(attempts_message, True, pygame.Color('#ffffff'))
        screen.blit(attempts_surface, (128, 320))  # Позиционирование текста попыток

        # Обработка мигающего курсора
        cursor_timer += 1
        if cursor_timer >= 20:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        if cursor_visible and active:
            cursor = font.render('|', True, color)
            cursor_x = input_box.x + txt_surface.get_width() + 10
            cursor_y = input_box.y - 13
            screen.blit(cursor, (cursor_x, cursor_y))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

class Game:
    def __init__(self):
        # интерфейс
        pygame.display.set_caption("Звёздное нашествие")
        pygame_icon = pygame.image.load("../Graphics/Red.png")
        pygame.display.set_icon(pygame_icon)

        player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        self.lives = 3
        self.live_surf = pygame.image.load("../Graphics/Player.png").convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font("../Font/Pixeled.ttf", 20)

        self.shape = Obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)

        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1

        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)

        music = pygame.mixer.Sound("../Audio/Music.wav")
        music.set_volume(0.5)
        music.play(loops = -1)
        self.laser_sound = pygame.mixer.Sound('../Audio/Laser.wav')
        self.laser_sound.set_volume(0.2)
        self.explosion_sound = pygame.mixer.Sound('../Audio/Explosion.wav')
        self.explosion_sound.set_volume(0.5)

        self.end_game = False  # Флаг для завершения игры

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = Obstacle.Block(self.block_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance = 60, y_distance = 48, x_offset = 70, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0: alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2: alien_sprite = Alien('green', x, y)
                else: alien_sprite = Alien('red', x, y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites() and not self.end_game:
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left']), screen_width))
            self.extra_spawn_time = randint(400, 800)

    def collision_checks(self):
        if self.end_game:
            return  # Не проверять столкновения, если игра окончена

        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += 500
                    laser.kill()

        if self.alien_lasers:
            for laser in self.alien_lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'Очки: {self.score}', False, '#ffffff')
        score_rect = score_surf.get_rect(topleft = (10, -10))
        screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites() or self.end_game:
            victory_surf = self.font.render('Ты победил!', False, '#ffffff')
            victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)

    def run(self):
        if self.end_game:
            # Оставляем игрока и ограды на экране
            self.player.update()
            self.blocks.draw(screen)
            self.player.draw(screen)
            self.display_lives()
            self.display_score()
            self.victory_message()
            return

        self.player.update()
        self.alien_lasers.update()
        self.extra.update()
        self.aliens.update(self.alien_direction)
        self.alien_position_checker()
        self.extra_alien_timer()
        self.collision_checks()
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.victory_message()

if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    font = pygame.font.Font("../Font/Pixeled.ttf", 20)
    pygame_icon = pygame.image.load("../Graphics/Key.png")
    pygame.display.set_icon(pygame_icon)

    if authenticate(screen, font):
        game = Game()
        crt = CRT()

        ALIENLASER = pygame.USEREVENT + 1
        pygame.time.set_timer(ALIENLASER, 800)

        input_text = ''

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == ALIENLASER:
                    game.alien_shoot()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip().upper() == 'END':
                            game.end_game = True
                        input_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            screen.fill((30, 30, 30))
            game.run()
            crt.draw()

            pygame.display.flip()
            clock.tick(60)