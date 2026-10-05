import pygame
import random


SIZE = 10
TILE_SIZE = 30
SCREEN_SIZE = SIZE * TILE_SIZE * 3

chunks = {}
player_x = SIZE // 2
player_y = SIZE // 2

def left_shift(chunks):
    # Центральный ряд
    chunks[(-1, 0)] = chunks[(0, 0)]
    chunks[(0, 0)] = chunks[(1, 0)]
    # Берём выход справа (индекс 1) у нового центрального чанка
    right_exit = chunks[(0, 0)][1][1]  # (exit_right)
    chunks[(1, 0)] = generate_chunk(0, right_exit[1], True)  # start_x=0, start_y=right_exit

    # Верхний ряд
    chunks[(-1, -1)] = chunks[(0, -1)]
    chunks[(0, -1)] = chunks[(1, -1)]
    right_exit = chunks[(0, -1)][1][1]
    chunks[(1, -1)] = generate_chunk(0, right_exit[1], True)  # start_x=0, start_y=right_exit

    # Нижний ряд
    chunks[(-1, 1)] = chunks[(0, 1)]
    chunks[(0, 1)] = chunks[(1, 1)]
    right_exit = chunks[(0, 1)][1][1]
    chunks[(1, 1)] = generate_chunk(0, right_exit[1], True)  # start_x=0, start_y=right_exit

def right_shift(chunks):
    chunks[(1, 0)] = chunks[(0, 0)]
    chunks[(0, 0)] = chunks[(-1, 0)]
    left_exit = chunks[(0, 0)][1][3]  # (exit_left)
    chunks[(-1, 0)] = generate_chunk(SIZE - 1, left_exit[1], True)  # start_x=SIZE-1, start_y=left_exit
    chunks[(1, -1)] = chunks[(0, -1)]
    chunks[(0, -1)] = chunks[(-1, -1)]
    left_exit = chunks[(0, -1)][1][3]
    chunks[(-1, -1)] = generate_chunk(SIZE - 1, left_exit[1], True)
    chunks[(1, 1)] = chunks[(0, 1)]
    chunks[(0, 1)] = chunks[(-1, 1)]
    left_exit = chunks[(0, 1)][1][3]
    chunks[(-1, 1)] = generate_chunk(SIZE - 1, left_exit[1], True)

def up_shift(chunks):
    chunks[(0, -1)] = chunks[(0, 0)]
    chunks[(0, 0)] = chunks[(0, 1)]
    bottom_exit = chunks[(0, 0)][1][2]  # exit_down
    chunks[(0, 1)] = generate_chunk(bottom_exit[1], 0, True)  # вход сверху

    chunks[(-1, -1)] = chunks[(-1, 0)]
    chunks[(-1, 0)] = chunks[(-1, 1)]
    bottom_exit = chunks[(-1, 0)][1][2]
    chunks[(-1, 1)] = generate_chunk(bottom_exit[1], 0, True)

    chunks[(1, -1)] = chunks[(1, 0)]
    chunks[(1, 0)] = chunks[(1, 1)]
    bottom_exit = chunks[(1, 0)][1][2]
    chunks[(1, 1)] = generate_chunk(bottom_exit[1], 0, True)

def down_shift(chunks):
    chunks[(0, 1)] = chunks[(0, 0)]
    chunks[(0, 0)] = chunks[(0, -1)]
    top_exit = chunks[(0, 0)][1][0]  # exit_up
    chunks[(0, -1)] = generate_chunk(top_exit[1], SIZE - 1, True)  # вход снизу

    chunks[(-1, 1)] = chunks[(-1, 0)]
    chunks[(-1, 0)] = chunks[(-1, -1)]
    top_exit = chunks[(-1, 0)][1][0]
    chunks[(-1, -1)] = generate_chunk(top_exit[1], SIZE - 1, True)

    chunks[(1, 1)] = chunks[(1, 0)]
    chunks[(1, 0)] = chunks[(1, -1)]
    top_exit = chunks[(1, 0)][1][0]
    chunks[(1, -1)] = generate_chunk(top_exit[1], SIZE - 1, True)

def generate_chunk(start_x: int, start_y: int, is_from_other_chunk=False):
    chunk = [[1 for _ in range(SIZE)] for _ in range(SIZE)]

    entrance_side = None
    entrance_x = None
    entrance_y = None

    if is_from_other_chunk:

        if start_x == 0:
            # Пришли слева
            entrance_side = "left"
            entrance_x = 0
            entrance_y = start_y

            start_x = 1

        elif start_x == SIZE - 1:
            # Пришли справа
            entrance_side = "right"
            entrance_x = SIZE - 1
            entrance_y = start_y

            start_x = SIZE - 2

        elif start_y == 0:
            # Пришли сверху
            entrance_side = "up"
            entrance_x = start_x
            entrance_y = 0

            start_y = 1

        elif start_y == SIZE - 1:
            # Пришли снизу
            entrance_side = "down"
            entrance_x = start_x
            entrance_y = SIZE - 2

            start_y = SIZE - 1

    chunk[start_y][start_x] = 0

    if entrance_side == "left":
        chunk[entrance_y][0] = 0

    elif entrance_side == "right":
        chunk[entrance_y][SIZE - 1] = 0

    elif entrance_side == "up":
        chunk[0][entrance_x] = 0

    elif entrance_side == "down":
        chunk[SIZE - 1][entrance_x] = 0

    # =================================================
    # 3. Генерация лабиринта
    # =================================================

    def carve(x, y):
        directions = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0)
        ]

        random.shuffle(directions)

        for dx, dy in directions:
            nx = x + dx * 2
            ny = y + dy * 2

            if 0 < nx < SIZE - 1 and 0 < ny < SIZE - 1:
                if chunk[ny][nx] == 1:
                    chunk[y + dy][x + dx] = 0
                    chunk[ny][nx] = 0 if random.random() < 0.999 else 2

                    carve(nx, ny)

    carve(start_x, start_y)

    # =================================================
    # 4. Функция создания выхода
    # =================================================

    def make_exit(side, position, length=None):
        if length is None:
            length = random.randint(2, 3)

        if side == "left":
            x, y = 0, position
            dx, dy = 1, 0

        elif side == "right":
            x, y = SIZE - 1, position
            dx, dy = -1, 0

        elif side == "up":
            x, y = position, 0
            dx, dy = 0, 1

        else:  # down
            x, y = position, SIZE - 1
            dx, dy = 0, -1

        # Выход
        chunk[y][x] = 0

        # Небольшой туннель
        for _ in range(length):
            x += dx
            y += dy

            if 0 <= x < SIZE and 0 <= y < SIZE:
                chunk[y][x] = 0

    # =================================================
    # 5. Обязательный вход
    # =================================================

    possible = [1, 3, 5, 7, 9]

    if entrance_side == "left":
        left_y = entrance_y
    else:
        left_y = random.choice(possible)

    if entrance_side == "right":
        right_y = entrance_y
    else:
        right_y = random.choice(possible)

    if entrance_side == "up":
        up_x = entrance_x
    else:
        up_x = random.choice(possible)

    if entrance_side == "down":
        down_x = entrance_x
    else:
        down_x = random.choice(possible)

    # =================================================
    # 6. Создаём основные выходы
    # =================================================

    make_exit("left", left_y)
    make_exit("right", right_y)
    make_exit("up", up_x)
    make_exit("down", down_x)

    # =================================================
    # 7. ДОПОЛНИТЕЛЬНЫЕ ТУННЕЛИ
    #
    # Они не зависят от стороны входа.
    # =================================================

    extra_connections = random.randint(0, 2)

    sides = ["left", "right", "up", "down"]
    random.shuffle(sides)

    for side in sides[:extra_connections]:

        # Не создаём второй выход в той же точке
        if side == "left":
            position = random.choice(possible)

            # Если это обязательный вход — пропускаем
            if entrance_side == "left" and position == entrance_y:
                continue

            make_exit(side, position)

        elif side == "right":
            position = random.choice(possible)

            if entrance_side == "right" and position == entrance_y:
                continue

            make_exit(side, position)

        elif side == "up":
            position = random.choice(possible)

            if entrance_side == "up" and position == entrance_x:
                continue

            make_exit(side, position)

        elif side == "down":
            position = random.choice(possible)

            if entrance_side == "down" and position == entrance_x:
                continue

            make_exit(side, position)

    # =================================================
    # 8. Выходы
    # =================================================

    exits = (
        (0, up_x),
        (right_y, SIZE - 1),
        (SIZE - 1, down_x),
        (left_y, 0)
    )

    return chunk, exits

# ===============================
# 4. ИНИЦИАЛИЗАЦИЯ PYGAME
# ===============================
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
clock = pygame.time.Clock()

# ===== ИНИЦИАЛИЗАЦИЯ ЧАНКОВ (3-2-3) =====

# 1. Центральный чанк
chunks[(0, 0)] = generate_chunk(SIZE//2, SIZE//2, False)

# 2. Центральный ряд (соседи по горизонтали)
# Чанк слева (-1, 0) — вход справа
start_y = chunks[(0, 0)][1][3][0]  # exit_left — (y, 0), берём y
chunks[(-1, 0)] = generate_chunk(SIZE - 1, start_y, True)

# Чанк справа (1, 0) — вход слева
start_y = chunks[(0, 0)][1][1][0]  # exit_right — (y, SIZE-1), берём y
chunks[(1, 0)] = generate_chunk(0, start_y, True)

# 3. Вертикальный ряд (соседи по вертикали)
# Чанк сверху (0, -1) — вход снизу
start_x = chunks[(0, 0)][1][2][1]  # exit_down — (SIZE-1, x), берём x
chunks[(0, -1)] = generate_chunk(start_x, 0, True)

# Чанк снизу (0, 1) — вход сверху
start_x = chunks[(0, 0)][1][0][1]  # exit_up — (0, x), берём x
chunks[(0, 1)] = generate_chunk(start_x, SIZE - 1, True)

# 4. Углы (на основе уже созданных чанков)
# Верхний левый (-1, -1) — вход справа из верхнего чанка (0, -1)
start_y = chunks[(0, -1)][1][3][0]  # exit_left от верхнего
chunks[(-1, -1)] = generate_chunk(SIZE - 1, start_y, True)

# Верхний правый (1, -1) — вход слева из верхнего чанка (0, -1)
start_y = chunks[(0, -1)][1][1][0]  # exit_right от верхнего
chunks[(1, -1)] = generate_chunk(0, start_y, True)

# Нижний левый (-1, 1) — вход справа из нижнего чанка (0, 1)
start_y = chunks[(0, 1)][1][3][0]  # exit_left от нижнего
chunks[(-1, 1)] = generate_chunk(SIZE - 1, start_y, True)

# Нижний правый (1, 1) — вход слева из нижнего чанка (0, 1)
start_y = chunks[(0, 1)][1][1][0]  # exit_right от нижнего
chunks[(1, 1)] = generate_chunk(0, start_y, True)
# ===============================
# 5. ГЛАВНЫЙ ЦИКЛ
# ===============================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        if player_x-1 < 0:
            if chunks[(-1, 0)][0][player_y][SIZE-1] == 0:
                right_shift(chunks)   # сдвигаем мир вправо (игрок уходит влево)
                player_x = SIZE - 1   # перебрасываем в правый край нового чанка
            elif chunks[(-1, 0)][0][player_y][SIZE-1] == 2:
                pygame.quit()
                exit("Game Over: You win!")
        else:
            if chunks[(0, 0)][0][player_y][player_x-1] == 0:  # Проверяем, что игрок может двигаться влево
                player_x -= 1
            elif chunks[(0, 0)][0][player_y][player_x-1] == 2:
                pygame.quit()
                exit("Game Over: You win!")
    
    if keys[pygame.K_RIGHT]:
        if player_x+1 >= SIZE:
            if chunks[(1, 0)][0][player_y][0] == 0:
                left_shift(chunks)    # сдвигаем мир влево (игрок уходит вправо)
                player_x = 0
            elif chunks[(1, 0)][0][player_y][0] == 2:
                pygame.quit()
                exit("Game Over: You win!")
        else:
            if chunks[(0, 0)][0][player_y][player_x+1] == 0:  # Проверяем, что игрок может двигаться вправо
                player_x += 1
            elif chunks[(0, 0)][0][player_y][player_x+1] == 2:
                pygame.quit()
                exit("Game Over: You win!")

    if keys[pygame.K_UP]:
        if player_y-1 < 0:
            if chunks[(0, -1)][0][SIZE-1][player_x] == 0:
                down_shift(chunks)    # сдвигаем мир вниз (игрок уходит вверх)
                player_y = SIZE - 1   # перебрасываем в нижний край нового чанка
            elif chunks[(0, -1)][0][SIZE-1][player_x] == 2:
                pygame.quit()
                exit("Game Over: You win!")
        else:
            if chunks[(0, 0)][0][player_y-1][player_x] == 0:  # Проверяем, что игрок может двигаться вверх
                player_y -= 1
            elif chunks[(0, 0)][0][player_y-1][player_x] == 2:
                pygame.quit()
                exit("Game Over: You win!")
    
    if keys[pygame.K_DOWN]:
        if player_y+1 >= SIZE:
            if chunks[(0, 1)][0][0][player_x] == 0:
                up_shift(chunks)      # сдвигаем мир вверх (игрок уходит вниз)
                player_y = 0          # перебрасываем в верхний край нового чанка
            elif chunks[(0, 1)][0][0][player_x] == 2:
                pygame.quit()
                exit("Game Over: You win!")
        else:
            if chunks[(0, 0)][0][player_y+1][player_x] == 0:  # Проверяем, что игрок может двигаться вниз
                player_y += 1
            elif chunks[(0, 0)][0][player_y+1][player_x] == 2:
                pygame.quit()
                exit("Game Over: You win!")

    # --- ОТРИСОВКА ---
    screen.fill((0, 0, 0))

    for (cx, cy), chunk_data in chunks.items():
        chunk = chunk_data[0]  # Извлекаем сам чанк из кортежа

        offset_x = (cx + 1) * SIZE * TILE_SIZE
        offset_y = (cy + 1) * SIZE * TILE_SIZE

        for y in range(SIZE):
            for x in range(SIZE):
                color = (255, 255, 255) if chunk[y][x] == 0 else (0, 0, 0) if chunk[y][x] == 1 else (0, 255, 0)
                pygame.draw.rect(
                    screen,
                    color,
                    (offset_x + x * TILE_SIZE,
                     offset_y + y * TILE_SIZE,
                     TILE_SIZE,
                     TILE_SIZE)
                )

    # Игрок
    pygame.draw.rect(
        screen,
        (255, 0, 0),
        ((player_x + SIZE) * TILE_SIZE,
         (player_y + SIZE) * TILE_SIZE,
         TILE_SIZE,
         TILE_SIZE)
    )

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
