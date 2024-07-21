import pygame
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = (x, y))

shape = [
"  xxxxxxx",
" xxxxxxxxx",
"xxxxxxxxxxx",
"xxxxxxxxxxx",
"xxxxxxxxxxx",
"xxxx   xxxx",
"xxx     xxx"
]