import pygame
import random
import json


CHUNK_SIZE = 10
TILE_SIZE = 25
SCREEN_SIZE = CHUNK_SIZE * TILE_SIZE * 3

STRUCTURES_DIR = 'structures.json'

with open(STRUCTURES_DIR, 'r') as f:
    structures_json = json.load(f)

class Chunk:
    def __init__(self, size, structures_json=None, exits_down = set(), exits_up = set(), exits_left = set(), exits_right = set()):
        self.size = size
        self.structures_json = structures_json
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
                    if len(self.exits_left) < 2 and not (y in self.exits_left) and random.random() < 0.25:
                        self.exits_left.add(y)
                    continue
                elif nx >= self.size:
                    if len(self.exits_right) < 2 and not (y in self.exits_right) and random.random() < 0.25:
                        self.exits_right.add(y)
                        self.matrix[self.size - 1][y] = 0
                    continue
                elif ny < 0:
                    if len(self.exits_up) < 2 and not (x in self.exits_up) and random.random() < 0.25:
                        self.exits_up.add(x)
                    continue
                elif ny >= self.size:
                    if len(self.exits_down) < 2 and not (x in self.exits_down) and random.random() < 0.25:
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
        exits_counter = len(self.exits_down) + len(self.exits_up) + len(self.exits_left) + len(self.exits_right)
        need = random.randint(2, 8)
        if not self.exits_down and exits_counter < need:
            self.exits_down.add(random.randint(0, self.size - 1)// 2 * 2)
            exits_counter += 1
        if not self.exits_up and exits_counter < need:
            self.exits_up.add(random.randint(0, self.size - 1)// 2 * 2)
            exits_counter += 1
        if not self.exits_left and exits_counter < need:
            self.exits_left.add(random.randint(0, self.size - 1)// 2 * 2)
            exits_counter += 1
        if not self.exits_right and exits_counter < need:
            self.exits_right.add(random.randint(0, self.size - 1)// 2 * 2)
            exits_counter += 1
        for exit_x in self.exits_down:
            self.matrix[exit_x][self.size - 1] = 0
        for exit_x in self.exits_up:
            self.matrix[exit_x][0] = 0
        for exit_y in self.exits_left:
            self.matrix[0][exit_y] = 0
        for exit_y in self.exits_right:
            self.matrix[self.size - 1][exit_y] = 0

    def load_from_structure(self, structure_name):
        self.matrix = self.structures_json[structure_name]
        self.exits_down = {x for x in range(self.size) if self.matrix[x][self.size - 1] == 0}
        self.exits_up = {x for x in range(self.size) if self.matrix[x][0] == 0}
        self.exits_left = {y for y in range(self.size) if self.matrix[0][y] == 0}
        self.exits_right = {y for y in range(self.size) if self.matrix[self.size - 1][y] == 0}


class InfiniteMaze:
    def __init__(self, chunk_size, structure_spawn_chance=0.02):
        self.chunk_size = chunk_size
        self.structure_spawn_chance = structure_spawn_chance
        self.chunks = {}
        # 0:0
        self.chunks[(0, 0)] = Chunk(chunk_size)
        self.chunks[(0, 0)].generate_from_exits()
        # 0:1
        self.chunks[(0, 1)] = Chunk(chunk_size, exits_up=self.chunks[(0, 0)].exits_down.copy())
        self.chunks[(0, 1)].generate_from_exits()
        # 1:0
        self.chunks[(1, 0)] = Chunk(chunk_size, exits_left=self.chunks[(0, 0)].exits_right.copy())
        self.chunks[(1, 0)].generate_from_exits()
        # 1:1
        self.chunks[(1, 1)] = Chunk(chunk_size, exits_up=self.chunks[(1, 0)].exits_down.copy(), exits_left=self.chunks[(0, 1)].exits_right.copy())
        self.chunks[(1, 1)].generate_from_exits()
        # 0:-1
        self.chunks[(0, -1)] = Chunk(chunk_size, exits_down=self.chunks[(0, 0)].exits_up.copy())
        self.chunks[(0, -1)].generate_from_exits()
        # -1:0
        self.chunks[(-1, 0)] = Chunk(chunk_size, exits_right=self.chunks[(0, 0)].exits_left.copy())
        self.chunks[(-1, 0)].generate_from_exits()
        # -1:-1
        self.chunks[(-1, -1)] = Chunk(chunk_size, exits_down=self.chunks[(-1, 0)].exits_up.copy(), exits_right=self.chunks[(0, -1)].exits_left.copy())
        self.chunks[(-1, -1)].generate_from_exits()
        # -1:1
        self.chunks[(-1, 1)] = Chunk(chunk_size, exits_up=self.chunks[(-1, 0)].exits_down.copy(), exits_right=self.chunks[(0, 1)].exits_left.copy())
        self.chunks[(-1, 1)].generate_from_exits()
        # 1:-1
        self.chunks[(1, -1)] = Chunk(chunk_size, exits_down=self.chunks[(1, 0)].exits_up.copy(), exits_left=self.chunks[(0, -1)].exits_right.copy())
        self.chunks[(1, -1)].generate_from_exits()

    def left_shift(self):
        self.chunks[(-1, 0)] = self.chunks[(0, 0)]
        self.chunks[(-1, -1)] = self.chunks[(0, -1)]
        self.chunks[(-1, 1)] = self.chunks[(0, 1)]
        self.chunks[(0, 0)] = self.chunks[(1, 0)]
        self.chunks[(0, -1)] = self.chunks[(1, -1)]
        self.chunks[(0, 1)] = self.chunks[(1, 1)]
        self.chunks[(1, 0)] = Chunk(self.chunk_size, exits_left=self.chunks[(0, 0)].exits_right.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(1, 0)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(1, 0)].generate_from_exits()
        self.chunks[(1, -1)] = Chunk(self.chunk_size, exits_down=self.chunks[(1, 0)].exits_up.copy(), exits_left=self.chunks[(0, -1)].exits_right.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(1, -1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(1, -1)].generate_from_exits()
        self.chunks[(1, 1)] = Chunk(self.chunk_size, exits_up=self.chunks[(1, 0)].exits_down.copy(), exits_left=self.chunks[(0, 1)].exits_right.copy(), structures_json=structures_json)
        self.chunks[(1, 1)].generate_from_exits()

    def right_shift(self):
        self.chunks[(1, 0)] = self.chunks[(0, 0)]
        self.chunks[(1, -1)] = self.chunks[(0, -1)]
        self.chunks[(1, 1)] = self.chunks[(0, 1)]
        self.chunks[(0, 0)] = self.chunks[(-1, 0)]
        self.chunks[(0, -1)] = self.chunks[(-1, -1)]
        self.chunks[(0, 1)] = self.chunks[(-1, 1)]
        self.chunks[(-1, 0)] = Chunk(self.chunk_size, exits_right=self.chunks[(0, 0)].exits_left.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(-1, 0)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(-1, 0)].generate_from_exits()
        self.chunks[(-1, -1)] = Chunk(self.chunk_size, exits_down=self.chunks[(-1, 0)].exits_up.copy(), exits_right=self.chunks[(0, -1)].exits_left.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(-1, -1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(-1, -1)].generate_from_exits()
        self.chunks[(-1, 1)] = Chunk(self.chunk_size, exits_up=self.chunks[(-1, 0)].exits_down.copy(), exits_right=self.chunks[(0, 1)].exits_left.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(-1, 1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(-1, 1)].generate_from_exits()

    def up_shift(self):
        self.chunks[(0, -1)] = self.chunks[(0, 0)]
        self.chunks[(-1, -1)] = self.chunks[(-1, 0)]
        self.chunks[(1, -1)] = self.chunks[(1, 0)]
        self.chunks[(0, 0)] = self.chunks[(0, 1)]
        self.chunks[(-1, 0)] = self.chunks[(-1, 1)]
        self.chunks[(1, 0)] = self.chunks[(1, 1)]
        self.chunks[(0, 1)] = Chunk(self.chunk_size, exits_down=self.chunks[(0, 0)].exits_up.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(0, 1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(0, 1)].generate_from_exits()
        self.chunks[(-1, 1)] = Chunk(self.chunk_size, exits_down=self.chunks[(-1, 0)].exits_up.copy(), exits_right=self.chunks[(0, 1)].exits_left.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(-1, 1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(-1, 1)].generate_from_exits()
        self.chunks[(1, 1)] = Chunk(self.chunk_size, exits_down=self.chunks[(1, 0)].exits_up.copy(), exits_left=self.chunks[(0, 1)].exits_right.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(1, 1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(1, 1)].generate_from_exits()

    def down_shift(self):
        self.chunks[(0, 1)] = self.chunks[(0, 0)]
        self.chunks[(-1, 1)] = self.chunks[(-1, 0)]
        self.chunks[(1, 1)] = self.chunks[(1, 0)]
        self.chunks[(0, 0)] = self.chunks[(0, -1)]
        self.chunks[(-1, 0)] = self.chunks[(-1, -1)]
        self.chunks[(1, 0)] = self.chunks[(1, -1)]
        self.chunks[(0, -1)] = Chunk(self.chunk_size, exits_up=self.chunks[(0, 0)].exits_down.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(0, -1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(0, -1)].generate_from_exits()
        self.chunks[(-1, -1)] = Chunk(self.chunk_size, exits_up=self.chunks[(-1, 0)].exits_down.copy(), exits_right=self.chunks[(0, -1)].exits_left.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(-1, -1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(-1, -1)].generate_from_exits()
        self.chunks[(1, -1)] = Chunk(self.chunk_size, exits_up=self.chunks[(1, 0)].exits_down.copy(), exits_left=self.chunks[(0, -1)].exits_right.copy(), structures_json=structures_json)
        if random.random() < self.structure_spawn_chance:
            self.chunks[(1, -1)].load_from_structure(random.choice(list(structures_json.keys())))
        else:
            self.chunks[(1, -1)].generate_from_exits()

pygame.init()

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

maze = InfiniteMaze(CHUNK_SIZE)

player_x, player_y = 0, 0

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        """
        #for debug
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                maze.up_shift()
        """
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        if player_x > 0:
            if maze.chunks[(0, 0)].matrix[player_x - 1][player_y] == 0:
                player_x -= 1
        else:
            if maze.chunks[(-1, 0)].matrix[CHUNK_SIZE - 1][player_y] == 0:
                player_x = CHUNK_SIZE - 1
                maze.right_shift()
    elif keys[pygame.K_RIGHT]:
        if player_x < CHUNK_SIZE - 1:
            if maze.chunks[(0, 0)].matrix[player_x + 1][player_y] == 0:
                player_x += 1
        else:
            if maze.chunks[(1, 0)].matrix[0][player_y] == 0:
                player_x = 0
                maze.left_shift()
    elif keys[pygame.K_UP]:
        if player_y > 0:
            if maze.chunks[(0, 0)].matrix[player_x][player_y - 1] == 0:
                player_y -= 1
        else:
            if maze.chunks[(0, -1)].matrix[player_x][CHUNK_SIZE - 1] == 0:
                player_y = CHUNK_SIZE - 1
                maze.down_shift()
    elif keys[pygame.K_DOWN]:
        if player_y < CHUNK_SIZE - 1:
            if maze.chunks[(0, 0)].matrix[player_x][player_y + 1] == 0:
                player_y += 1
        else:
            if maze.chunks[(0, 1)].matrix[player_x][0] == 0:
                player_y = 0
                maze.up_shift()

    screen.fill((0, 0, 0))
    for chunk_coords, chunk in maze.chunks.items():
        chunk_x, chunk_y = chunk_coords
        offset_x = chunk_x * CHUNK_SIZE * TILE_SIZE + SCREEN_SIZE // 3
        offset_y = chunk_y * CHUNK_SIZE * TILE_SIZE + SCREEN_SIZE // 3
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                color = (255, 255, 255) if chunk.matrix[x][y] == 0 else (0, 0, 0)
                pygame.draw.rect(screen, color, (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE))
        pygame.draw.circle(screen, (255, 0, 0), (player_x * TILE_SIZE + SCREEN_SIZE // 3 + TILE_SIZE // 2, player_y * TILE_SIZE + SCREEN_SIZE // 3 + TILE_SIZE // 2), TILE_SIZE // 2)

    pygame.display.flip()
    clock.tick(10)
