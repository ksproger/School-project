import pygame
import random


CHUNK_SIZE = 10
TILE_SIZE = 25
SCREEN_SIZE = CHUNK_SIZE * TILE_SIZE * 3

class Chunk:
    def __init__(self, size, exits_down = set(), exits_up = set(), exits_left = set(), exits_right = set()):
        self.size = size
        self.exits_down = exits_down
        self.exits_up = exits_up
        self.exits_left = exits_left
        self.exits_right = exits_right
        self.matrix = [[1 for _ in range(size)] for _ in range(size)]
    def generate_from_exits(self):
        def carve_path(x, y):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2
                if nx < 0:
                    if len(self.exits_left) < 2 and not (y in self.exits_left) and random.random() < 0.5:
                        self.exits_left.add(y)
                    continue
                elif nx >= self.size:
                    if len(self.exits_right) < 2 and not (y in self.exits_right) and random.random() < 0.5:
                        self.exits_right.add(y)
                        self.matrix[self.size - 1][y] = 0
                    continue
                elif ny < 0:
                    if len(self.exits_up) < 2 and not (x in self.exits_up) and random.random() < 0.5:
                        self.exits_up.add(x)
                    continue
                elif ny >= self.size:
                    if len(self.exits_down) < 2 and not (x in self.exits_down) and random.random() < 0.5:
                        self.exits_down.add(x)
                        self.matrix[x][self.size - 1] = 0
                    continue
                if self.matrix[nx][ny] == 1:
                    self.matrix[nx][ny] = 0
                    self.matrix[x + dx][y + dy] = 0
                    carve_path(nx, ny)
        if self.exits_down:
            self.matrix[random.choice(list(self.exits_down))][self.size - 1] = 0
            carve_path(random.choice(list(self.exits_down)), self.size - 1)
        elif self.exits_up:
            self.matrix[random.choice(list(self.exits_up))][0] = 0
            carve_path(random.choice(list(self.exits_up)), 0)
        elif self.exits_left:
            self.matrix[0][random.choice(list(self.exits_left))] = 0
            carve_path(0, random.choice(list(self.exits_left)))
        elif self.exits_right:
            self.matrix[self.size - 1][random.choice(list(self.exits_right))] = 0
            carve_path(self.size - 1, random.choice(list(self.exits_right)))
        else:
            self.matrix[0][0] = 0
            carve_path(0, 0)
        if not self.exits_down:
            self.exits_down.add(random.randint(0, self.size - 1)// 2 * 2)
        if not self.exits_up:
            self.exits_up.add(random.randint(0, self.size - 1)// 2 * 2)
        if not self.exits_left:
            self.exits_left.add(random.randint(0, self.size - 1)// 2 * 2)
        if not self.exits_right:
            self.exits_right.add(random.randint(0, self.size - 1)// 2 * 2)
        for exit_x in self.exits_down:
            self.matrix[exit_x][self.size - 1] = 0
        for exit_x in self.exits_up:
            self.matrix[exit_x][0] = 0
        for exit_y in self.exits_left:
            self.matrix[0][exit_y] = 0
        for exit_y in self.exits_right:
            self.matrix[self.size - 1][exit_y] = 0


class InfiniteMaze:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.chunks = {}
        # 0:0
        self.chunks[(0, 0)] = Chunk(chunk_size)
        self.chunks[(0, 0)].generate_from_exits()
        # 0:1
        self.chunks[(0, 1)] = Chunk(chunk_size, exits_up=self.chunks[(0, 0)].exits_down)
        self.chunks[(0, 1)].generate_from_exits()
        # 1:0
        self.chunks[(1, 0)] = Chunk(chunk_size, exits_left=self.chunks[(0, 0)].exits_right)
        self.chunks[(1, 0)].generate_from_exits()
        # 1:1
        self.chunks[(1, 1)] = Chunk(chunk_size, exits_up=self.chunks[(1, 0)].exits_down, exits_left=self.chunks[(0, 1)].exits_right)
        self.chunks[(1, 1)].generate_from_exits()
        # 0:-1
        self.chunks[(0, -1)] = Chunk(chunk_size, exits_down=self.chunks[(0, 0)].exits_up)
        self.chunks[(0, -1)].generate_from_exits()
        # -1:0
        self.chunks[(-1, 0)] = Chunk(chunk_size, exits_right=self.chunks[(0, 0)].exits_left)
        self.chunks[(-1, 0)].generate_from_exits()
        # -1:-1
        self.chunks[(-1, -1)] = Chunk(chunk_size, exits_down=self.chunks[(-1, 0)].exits_up, exits_right=self.chunks[(0, -1)].exits_left)
        self.chunks[(-1, -1)].generate_from_exits()
        # -1:1
        self.chunks[(-1, 1)] = Chunk(chunk_size, exits_up=self.chunks[(-1, 0)].exits_down, exits_right=self.chunks[(0, 1)].exits_left)
        self.chunks[(-1, 1)].generate_from_exits()
        # 1:-1
        self.chunks[(1, -1)] = Chunk(chunk_size, exits_down=self.chunks[(1, 0)].exits_up, exits_left=self.chunks[(0, -1)].exits_right)
        self.chunks[(1, -1)].generate_from_exits()

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

maze = InfiniteMaze(CHUNK_SIZE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill((0, 0, 0))
    for chunk_coords, chunk in maze.chunks.items():
        chunk_x, chunk_y = chunk_coords
        offset_x = chunk_x * CHUNK_SIZE * TILE_SIZE + SCREEN_SIZE // 3
        offset_y = chunk_y * CHUNK_SIZE * TILE_SIZE + SCREEN_SIZE // 3
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                color = (255, 255, 255) if chunk.matrix[x][y] == 0 else (0, 0, 0)
                pygame.draw.rect(screen, color, (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()