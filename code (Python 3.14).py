import random
import logging
import collections
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), "logs.txt"), filemode="a", level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import pygame
    import pygame_gui
except ImportError as e:
    logging.critical(f"Missing library: {e}")
    logging.info("Install with: pip install pygame-ce pygame-gui")
    sys.exit(1)

pygame.init()

fps = 30
max_making_speed = 1600
ui_size = 200
width, height = 33, 33
tile_size = 20
max_walls = width * height // 1.75

screen_width = width * tile_size + ui_size
screen_height = height * tile_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Maze game on Python.")

difficulties = {"Easy": 1, "Normal": 0.85, "Hard": 0.75}
difficulty = "Normal"

clock = pygame.time.Clock()
manager = pygame_gui.UIManager((screen_width, screen_height), (resource_path("assets/theme.json"))  )


class Maze:
    def __init__(self, screen_, ui_man, wall_texture=None, floor_texture=None, player_texture=None, exit_texture=None,
                 ui_bg_texture=None, wall_texture2=None, floor_texture2=None, player_texture2=None, exit_texture2=None,
                 ui_bg_texture2=None, wall_texture3=None, floor_texture3=None, player_texture3=None, exit_texture3=None,
                 ui_bg_texture3=None, wall_texture4=None, floor_texture4=None, player_texture4=None, exit_texture4=None,
                 ui_bg_texture4=None, width_=11, height_=11):

        self.screen = screen_
        self.speed = 5
        self.maze = None
        self.ui_manager = ui_man
        self.darkness = False
        self.timer = 0
        self.making_speed = max_making_speed

        self.generating = False
        self.gen_progress = 0

        self.width = width_
        self.height = height_
        self.player_pos = [1, 1]
        self.pixel_pos = (self.player_pos[0] * tile_size, self.player_pos[1] * tile_size)
        self.new_pos = self.player_pos
        self.exit_pos = (self.width - 2, self.height - 2)
        self.victory = False

        def _check_texture(path, color):
            try:
                tex = pygame.image.load(path)
            except:
                tex = pygame.Surface((tile_size, tile_size))
                tex.fill(color)
                logging.error(f"File {path} not found!")
            return tex

        self.wall_textures = [pygame.transform.scale(_check_texture(wall_texture, (50, 50, 50)), (self.width*tile_size, self.height*tile_size)), pygame.transform.scale(_check_texture(wall_texture2, (80, 80, 80)), (self.width*tile_size, self.height*tile_size)), pygame.transform.scale(_check_texture(wall_texture3, (110, 110, 110)), (self.width*tile_size, self.height*tile_size)), pygame.transform.scale(_check_texture(wall_texture4, (140, 140, 140)), (self.width*tile_size, self.height*tile_size))]
        self.ui_bg_textures = [pygame.transform.scale(_check_texture(ui_bg_texture, (0, 0, 0)), (ui_size, self.height*tile_size)), pygame.transform.scale(_check_texture(ui_bg_texture2, (30, 30, 30)), (ui_size, self.height*tile_size)), pygame.transform.scale(_check_texture(ui_bg_texture3, (60, 60, 60)), (ui_size, self.height*tile_size)), pygame.transform.scale(_check_texture(ui_bg_texture4, (90, 90, 90)), (ui_size, self.height*tile_size))]
        self.floor_textures = [pygame.transform.scale(_check_texture(floor_texture, (150, 150, 150)), (tile_size, tile_size)), pygame.transform.scale(_check_texture(floor_texture2, (240, 240, 240)), (tile_size, tile_size)), pygame.transform.scale(_check_texture(floor_texture3, (210, 210, 210)), (tile_size, tile_size)), pygame.transform.scale(_check_texture(floor_texture4, (240, 240, 240)), (tile_size, tile_size))]
        self.player_textures = [pygame.transform.scale(_check_texture(player_texture, (200, 0, 0)), (tile_size, tile_size)), pygame.transform.scale(_check_texture(player_texture2, (255, 0, 0)), (tile_size, tile_size)), pygame.transform.scale(_check_texture(player_texture3, (255, 128, 128)), (tile_size, tile_size)), pygame.transform.scale(_check_texture(player_texture4,(255 ,192 ,192)) , (tile_size , tile_size))]
        self.exit_textures = [pygame.transform.scale(_check_texture(exit_texture,(0 ,200 ,0)) , (tile_size , tile_size)) , pygame.transform.scale(_check_texture(exit_texture2,(0 ,255 ,0)) , (tile_size , tile_size)) , pygame.transform.scale(_check_texture(exit_texture3,(173 ,255 ,47)) ,(tile_size,tile_size)) , pygame.transform.scale(_check_texture(exit_texture4,(34 ,139 ,34)) ,(tile_size,tile_size))]

        self.texture_pack = 0

        pygame_gui.elements.UIButton(pygame.Rect((screen_width - ui_size, 5), (ui_size, 40)), "New easy maze",
                                     self.ui_manager)
        pygame_gui.elements.UIButton(pygame.Rect((screen_width - ui_size, 50), (ui_size, 40)), "New normal maze",
                                     self.ui_manager)
        pygame_gui.elements.UIButton(pygame.Rect((screen_width - ui_size, 95), (ui_size, 40)), "New hard maze",
                                     self.ui_manager)
        pygame_gui.elements.UIButton(pygame.Rect((screen_width - ui_size, 140), (ui_size, 40)), "Darkness",
                                     self.ui_manager)
        pygame_gui.elements.UIButton(pygame.Rect((screen_width - ui_size, 185), (ui_size, 40)), "Texture pack",
                                     self.ui_manager)
        pygame_gui.elements.UIButton(pygame.Rect((screen_width - ui_size, 230), (ui_size, 40)), "Solve maze",
                                     self.ui_manager)
        pygame_gui.elements.UIHorizontalSlider(pygame.Rect((screen_width - ui_size, 275), (ui_size, 40)), max_making_speed, [1, max_making_speed],self.ui_manager)

        logging.info("Initializing maze")

        self.set_new_maze()

        logging.info("Maze initialized")
    def _add_path_gen(self, x, y):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2

            if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                if self.maze[ny][nx] == 1:
                    self.maze[ny][nx] = 0
                    self.maze[y + dy][x + dx] = 0
                    self.exit_pos = (ny, nx)

                    yield

                    if random.random() < difficulties[difficulty]:
                        yield from self._add_path_gen(nx, ny)
    def _create_new(self):
        self.generating = False
        self.gen = None

        self.maze = [[1]*self.width for _ in range(self.height)]
        self.maze[1][1] = 0

        self.gen = self._add_path_gen(1, 1)
        self.generating = True
        self.gen_progress = 0
    def set_new_maze(self):
        self.victory = False
        self.timer = 0
        self.player_pos = [1, 1]
        self.new_pos = self.player_pos

        logging.info("Creating new maze")

        self._create_new()
    def _solve(self):
            queue = collections.deque([((self.player_pos[1], self.player_pos[0]),)])
            visited = set()
            rows = len(self.maze)
            cols = len(self.maze[0])

            while queue:
                current_path = queue.popleft()
                current_node = current_path[-1]
                
                if current_node == self.exit_pos:
                    return current_path

                if current_node in visited:
                    continue
                visited.add(current_node)

                x, y = current_node
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

                for dx, dy in directions:
                    next_x, next_y = x + dx, y + dy

                    if 0 <= next_x < rows and 0 <= next_y < cols and not self.maze[next_x][next_y]:
                        if (next_x, next_y) not in visited:
                            new_path = list(current_path)
                            new_path.append((next_x, next_y))
                            queue.append(new_path)
            return None
    def draw(self):
        self.screen.blit(self.wall_textures[self.texture_pack], (0, 0))
        self.screen.blit(self.ui_bg_textures[self.texture_pack], (self.width*tile_size, 0))
        for y in range(self.height):
            for x in range(self.width):
                if not self.maze[y][x]:
                    self.screen.blit(self.floor_textures[self.texture_pack], (x * tile_size, y * tile_size))

        px, py = self.pixel_pos
        nx, ny = self.new_pos[0]*tile_size, self.new_pos[1]*tile_size
        if px < nx:
            px = min(px + self.speed, nx)
        elif px > nx:
            px = max(px - self.speed, nx)
        if py < ny:
            py = min(py + self.speed, ny)
        elif py > ny:
            py = max(py - self.speed, ny)
        self.pixel_pos = [px, py]
        if self.pixel_pos == [nx, ny]:
            self.player_pos = self.new_pos

        self.screen.blit(self.player_textures[self.texture_pack], (px, py))

        ey, ex = self.exit_pos
        self.screen.blit(self.exit_textures[self.texture_pack], (ex * tile_size, ey * tile_size))

        if self.timer > 0:
            solved = self._solve()
            if solved:
                for pos in solved:
                    pygame.draw.rect(self.screen, (0, 255, 255), (pos[1] * tile_size, pos[0] * tile_size, tile_size, tile_size), 3)
            self.timer -= 1
        if self.darkness:
            width_px = self.width * tile_size
            height_px = self.height * tile_size

            dark_surface = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0))

            center_x = self.pixel_pos[0] + tile_size // 2
            center_y = self.pixel_pos[1] + tile_size // 2

            max_radius = 60

            for r in range(max_radius, 0, -5):
                alpha = int(230 * (r / max_radius))
                pygame.draw.circle(
                    dark_surface,
                    (0, 0, 0, alpha),
                    (center_x, center_y),
                    r
                )

            self.screen.blit(dark_surface, (0, 0))
        if self.victory:
            font = pygame.font.SysFont(None, 48)
            text = font.render("VICTORY!", True, (255, 255, 0))
            bg = pygame.Surface((160, 32))
            bg.fill("red")
            self.screen.blit(bg, (self.screen.get_width() // 2 - 81 - ui_size // 2, self.screen.get_height() // 2 - 25))
            self.screen.blit(text, (self.screen.get_width() // 2 - 80 - ui_size // 2, self.screen.get_height() // 2 - 24))

        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()
    def move(self, direction):
        if self.victory:
            return
        x, y = self.player_pos
        nx, ny = x, y

        if direction == "up":
            ny -= 1
        if direction == "down":
            ny += 1
        if direction == "left":
            nx -= 1
        if direction == "right":
            nx += 1

        if 0 <= nx < self.width and 0 <= ny < self.height:
            if not self.maze[ny][nx]:
                self.new_pos = [nx, ny]
                if (ny, nx) == self.exit_pos:
                    self.victory = True
                    print("Victory!")
    def check_maze_validity(self):
        wall_count = sum(row.count(1) for row in self.maze)
        is_valid = self._solve() is not None
        wall_count_legal = wall_count <= max_walls
        if not wall_count_legal:
            logging.warning(f"Maze has too many walls: {wall_count} (max {max_walls})")
            return False
        if not is_valid:
            logging.warning("Maze is unsolvable!")
            return False
        if is_valid and wall_count_legal:
            logging.info(f"Maze generated successfully with {wall_count} walls.")
            return True


maze = Maze(screen, manager, resource_path("assets/wall.png"), resource_path("assets/floor.png"),
             resource_path("assets/player.png"), resource_path("assets/exit.png"),
               resource_path("assets/ui_background.png"), resource_path("assets/wall2.png"),
                 resource_path("assets/floor2.png"), resource_path("assets/player2.png"),
                   resource_path("assets/exit2.png"), resource_path("assets/ui_background2.png"),
                     resource_path("assets/wall3.png"), resource_path("assets/floor3.png"),
                       resource_path("assets/player3.png"), resource_path("assets/exit3.png"),
                         resource_path("assets/ui_background3.png"),resource_path("assets/wall4.png"),
                           resource_path("assets/floor4.png"), resource_path("assets/player4.png"),
                             resource_path("assets/exit4.png"), resource_path("assets/ui_background4.png"),
                     width, height)

while True:

    time_delta = clock.tick(fps) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            logging.info("Closing program")
            sys.exit(0)
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "New easy maze":
                logging.debug("Creating new Easy maze")
                difficulty = "Easy"
                maze.set_new_maze()
            elif event.ui_element.text == "New normal maze":
                logging.debug("Creating new Normal maze")
                difficulty = "Normal"
                maze.set_new_maze()
            elif event.ui_element.text == "New hard maze":
                logging.debug("Creating new Hard maze")
                difficulty = "Hard"
                maze.set_new_maze()
            elif event.ui_element.text == "Darkness":
                maze.darkness = not maze.darkness
            elif event.ui_element.text == "Texture pack":
                maze.texture_pack = (maze.texture_pack + 1) % 4
            elif event.ui_element.text == "Solve maze":
                maze.timer = 3 * fps
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            maze.making_speed = int(event.value)
            logging.debug(f"Making speed set to {maze.making_speed}")
        manager.process_events(event)

    manager.update(time_delta)
    
    if maze.generating:
        maze.gen_progress += maze.making_speed * time_delta

        try:
            while maze.gen_progress >= 1:
                next(maze.gen)
                maze.gen_progress -= 1
        except StopIteration:
            maze.generating = False
            if not maze.check_maze_validity():
                logging.error("Generated maze is invalid!")
                logging.info("Regenerating maze")
                maze.set_new_maze()
            elif sum(maze.exit_pos) < maze.width:
                logging.warning("Exit is too close to the start, settingdefault exit position")
                maze.exit_pos = (maze.height - 2, maze.width - 2)
                if not maze.check_maze_validity():
                    logging.error("Maze with default exit is invalid, regenerating maze")
                    maze.set_new_maze()
                else:
                    logging.info("Maze with default exit is valid.")
            else:
                logging.info("Maze generation completed successfully.")
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            maze.move("up")
        elif keys[pygame.K_DOWN]:
            maze.move("down")
        if keys[pygame.K_LEFT]:
            maze.move("left")
        elif keys[pygame.K_RIGHT]:
            maze.move("right")
    maze.draw()
