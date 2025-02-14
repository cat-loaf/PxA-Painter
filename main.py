import pygame, math, os, numpy as np, tkinter as tk
from tkinter import filedialog
from pygame.locals import *
from dataclasses import dataclass
from skimage.segmentation import flood_fill as ff

#TODO Saving/Loading to *specific* file
#TODO Contiguous/non-contiguous fill
#TODO Clean code 

@dataclass
class Object:
    rep: pygame.Surface
    pos : list[int, int]
    col : tuple[int, int, int] = None
    active : bool = True
    collision: ... = None
    
    def __post_init__(self):
        if not self.collision:
            self.collision = lambda : self.rep.get_rect(topleft=self.pos).collidepoint
        
        if self.col is not None:
            self.rep.fill(self.col)
        
    def change_color(self, col:tuple[int, int, int]):
        self.col = col
        self.rep.fill(self.col)
        
    def get_color(self):
        return self.col
        
@dataclass
class Camera:
    pos : list[int, int]
    scale : int
    speed : int = 1
    
    def behaviour(self, keys):
        self.pos[0] += (-keys[K_LEFT] + keys[K_RIGHT]) * self.speed
        self.pos[1] += (-keys[K_UP] + keys[K_DOWN]) * self.speed
        
    def set_pos(self, x, y=None):
        if isinstance(x, tuple) or isinstance(x, list):
            self.pos = x
        else:
            self.pos = [x,y]
    
@dataclass  
class Grid:
    size : list[int, int]
    cell_size : int = 10
    padding : int = 0
    
    def __post_init__(self):
        self.data = [
            [ Object(
                pygame.Surface((self.cell_size, self.cell_size)), 
                (0,0), 
                (255,255,255)) 
            for _ in range(self.size[0]) ] 
        for _ in range(self.size[1])]
        
        for iy, row in enumerate(self.data):
            for ix, obj in enumerate(row):
                obj.pos = [(self.cell_size*ix)+(self.padding*ix), (self.cell_size*iy)+(self.padding*iy)]
                
    def fill(self, colors: list[list[list[int]]]):
        i = 0
        for row in self.data:
            for obj in row:
                try:
                    obj.change_color(colors[i])
                    i+=1
                except Exception as e:
                    print(e)
                    
    def as_color(self, color_palette) -> list[list[int]]:
        color_def = []
        for row in color_palette.data:
            for obj in row:
                color_def.append(obj.col)

        col_grid = []
        cur_row = []
        for row in self.data:
            for obj in row:
                cur_row.append(color_def.index(obj.col))
            col_grid.append(cur_row)
            cur_row = []
        
        return col_grid
    
    def get_color_int(self, color_palette, color) -> list[list[int]]:
        color_def = []
        for row in color_palette.data:
            for obj in row:
                color_def.append(obj.col)
                
        try:
            return color_def.index(color)
        except ValueError:
            return None
    
    def fill_color(self, color_palette, colors):
        color_def = []
        i=0
        for row in color_palette.data:
            for obj in row:
                color_def.append(obj.col)
                i += 1
                
        for iy, row in enumerate(colors):
            for ix, color in enumerate(row):
                self.data[iy][ix].change_color(color_def[color])
    
    def set_pos(self, pos):
        for iy, row in enumerate(self.data):
            for ix, obj in enumerate(row):
                obj.pos = [(self.cell_size*ix)+(self.padding*ix)+pos[0], (self.cell_size*iy)+(self.padding*iy)+pos[1]]

def clamped(value, min, max):
        if value <= min:
            return min
        if value >= max:
            return max
        else:
            return value

def generate_color_palette(filepath) -> Grid:
    with open(filepath, "r") as f:
        mode = f.readline().lstrip("[").rstrip("]\n")
        txt_colors = [a.split(",") for a in f.read().split("\n")]
        colors=[]
        cur=[]
        if mode == "RGB":
            for col in txt_colors:
                for val in col:
                    try:
                        cur.append(int(val))
                    except:
                        pass
                colors.append(cur)
                cur = []
        colors = [x for x in colors if x]
        if int(math.sqrt(len(colors)))**2 == len(colors):
            size = int(math.sqrt(len(colors)))
        else: 
            size = int(round(math.sqrt(len(colors)))+1)
        tmp = Grid((size,size), 10, 2)
        i=0
        for row in tmp.data:
            for obj in row:
                try:
                    obj.change_color(colors[i])
                    i += 1
                except:
                    obj.active = False
        return tmp
                
def load_file() -> Grid:
    filename = filedialog.askopenfilename(filetypes=[("PxA Painter", ".pxa")], initialdir="data/saves/")
    
    if filename != "":
        with open(filename, "r") as f:
            size = [int(i) for i in f.readline().replace("|", "").replace("\n","").replace(" ", "").split(",")]
            
            colors = []
            cont = f.read().replace("\n",";").split(";")
            for col in cont:
                sp = col.replace("(","").replace(")","").split(",")
                try:
                    colors.append([int(sp[0]),int(sp[1]),int(sp[2])])
                except Exception as e:
                    log(f"load_file(\"{filename}\") - {e}")
        
        tmp = Grid(size, 20, 1)
        tmp.fill(colors)
            
        return tmp
    return None
        
def save_file(g : Grid):
    output = f"|{g.size[0]},{g.size[1]}|\n"
    for row in g.data:
        for obj in row:
            output += str(obj.col)+";"
        
        output = output.rstrip(";")
        output += "\n"
            
    output = output.rstrip(",\n").replace("[", "(").replace("]",")")
    
    win = tk.Tk()
    win.withdraw()
    file = filedialog.asksaveasfile(defaultextension=".pxa", mode="w", filetypes=[("PxA Painter", ".pxa")], initialdir="data/saves/")
    if file:
        file.write(output)
        file.close()
        
def log(str):
    with open(r"data/logs", "w") as f:
        f.write(str)

def invert_surface(surface, screen, surface_pos):
    """Inverts the colors of the given surface."""
    surface = surface.copy()
    # Get the subsection of the screen to invert
    subsection = screen.subsurface(pygame.Rect(surface_pos, surface.get_size())).copy()
    
    # Lock the surface for pixel access
    subsection.lock()
    
    # Invert the colors of the subsection
    for x in range(subsection.get_width()):
        for y in range(subsection.get_height()):
            r, g, b, a = subsection.get_at((x, y))
            subsection.set_at((x, y), (255 - r, 255 - g, 255 - b, a))
    
    # Unlock the surface
    subsection.unlock()
    
    # Blit the inverted subsection back onto the surface
    for x in range(subsection.get_width()):
        for y in range(subsection.get_height()):
            r, g, b, a = surface.get_at((x, y))
            ir, ig, ib, ia = subsection.get_at((x, y))
            surface.set_at((x, y), (r & ir, g & ig, b & ib, a & ia))
    # surface.blit(subsection, (0, 0))
    return surface
 
class Program:
    def __init__(self, resolution:tuple, fps:int=60):
        # Hide the system mouse cursor
        # Set all relevant variables
        self.res = resolution
        
        self.fps = fps
        self.clock = pygame.time.Clock()
        
        self.running = True
        
        self.data = {}
        self.grid = Grid((10,10), 20, 1)
        
        self.color_palette = generate_color_palette(r"data/palettes/main.pal")
        self.tool_bar = Object(pygame.Surface((500,56)), [0,0], (47, 48, 49))
        self.selected_color_bar = Object(pygame.Surface((12,12)), [0,0] , (255, 255, 255))
        
        self.drag_data = None
        
        self.tools = {
            "move":   Object(pygame.image.load(os.path.abspath(r"icons/normal/move.png")), (84,10)),
            "paint":  Object(pygame.image.load(os.path.abspath(r"icons/normal/paint.png")), (84,10)),
            "eraser": Object(pygame.image.load(os.path.abspath(r"icons/normal/eraser.png")), (84,10)),
            "fill":   Object(pygame.image.load(os.path.abspath(r"icons/normal/fill.png")), (84, 10)),
            "clear":  Object(pygame.image.load(os.path.abspath(r"icons/normal/clear.png")), (84, 10)),
        }
        

        self.cursor_images = {
            "move":   pygame.image.load(os.path.abspath(r"icons/cursor/move_cursor.png")),
            "paint":  pygame.image.load(os.path.abspath(r"icons/cursor/paint_cursor.png")),
            "eraser": pygame.image.load(os.path.abspath(r"icons/cursor/eraser_cursor.png")),
            "fill":   pygame.image.load(os.path.abspath(r"icons/cursor/fill_cursor.png")),
            "clear":  pygame.image.load(os.path.abspath(r"icons/cursor/clear_cursor.png")),
        }
        self.cursor_pressed_images = {
            "move":   pygame.image.load(os.path.abspath(r"icons/cursor/move_cursor_pressed.png")),
            "paint":  pygame.image.load(os.path.abspath(r"icons/cursor/paint_cursor.png")),
            "eraser": pygame.image.load(os.path.abspath(r"icons/cursor/eraser_cursor_pressed.png")),
            "fill":   pygame.image.load(os.path.abspath(r"icons/cursor/fill_cursor.png")),
            "clear":  pygame.image.load(os.path.abspath(r"icons/cursor/clear_cursor.png")),
        }
                
        for i, obj in enumerate(self.tools.values()):
            obj.pos = (obj.pos[0]+(i*40), obj.pos[1])
        
        self.save_load = {
            "save": Object(pygame.image.load(os.path.abspath(r"icons/normal/save.png")), (460,10)),
            "load": Object(pygame.image.load(os.path.abspath(r"icons/normal/load.png")), (460,10))
        }
        
        for i, obj in enumerate(self.save_load.values()):
            obj.pos = (obj.pos[0]+(-i*40), obj.pos[1])
        
        for tool, obj in {**self.tools, **self.save_load}.items():
            obj.rep = pygame.transform.scale(obj.rep, (32,32))
            obj.normal_image = pygame.transform.scale(pygame.image.load(os.path.abspath(fr"icons/normal/{tool}.png")), (32,32))
            obj.clicked_image = pygame.transform.scale(pygame.image.load(os.path.abspath(fr"icons/clicked/{tool}_clicked.png")), (32,32))
        
        self.current_color = self.color_palette.data[0][0].col
        self.tool = "paint"
        self.camera = Camera([0,0], 1, 2)
        self.cursor_surface = pygame.Surface((32,32), pygame.SRCALPHA)
        self.cursor_surface.fill((255, 255, 255, 0))
        
        # Start pygame window
        self.initialise_pygame()
        
        # Do pre-game stuff
        self.pre_game()
        
        
    def initialise_pygame(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption("PxA Painter")
        pygame.display.set_icon(pygame.image.load(os.path.abspath(r"icons/clicked/paint_clicked.png")))
        self.screen = pygame.display.set_mode(self.res)
        
    def pre_game(self):
        self.camera.set_pos(self.res[0]/4+5, self.res[1]/4+5)
        self.color_palette.set_pos((5,5))
        self.selected_color_bar.pos = [
            self.color_palette.data[0][0].pos[0]-1, 
            self.color_palette.data[0][0].pos[1]-1
        ]
        self.grid.fill_color(self.color_palette, [[1 for _ in range(0, self.grid.size[0])] for _ in range(self.grid.size[1])])
        
    def main(self):
        while self.running:
            # Regulate FPS
            self.clock.tick(self.fps)
            
            mouse_pos = pygame.mouse.get_pos()

            mouse_offset = [mouse_pos[0]-self.camera.pos[0], mouse_pos[1]-self.camera.pos[1]] 
            mouse_pressed = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()
        
            self.camera.behaviour(keys)
            
            #region Events
            
            if not mouse_pressed[0]:
                self.drag_data = None
            if mouse_pressed[0]:
                # Pixel Grid events
                if not (self.tool_bar.rep.get_rect(topleft=self.tool_bar.pos).collidepoint(mouse_pos)):
                    if self.tool == "move":
                        if self.drag_data is None:
                            self.drag_data = [mouse_pos[0], mouse_pos[1]]
                        else:
                            self.camera.pos[0] += mouse_pos[0] - self.drag_data[0]
                            self.camera.pos[1] += mouse_pos[1] - self.drag_data[1]
                            self.drag_data = [mouse_pos[0], mouse_pos[1]]                
                    elif self.tool != "move":
                        self.drag_data = None  
                    
                for iy, row in enumerate(self.grid.data):
                    for ix, obj in enumerate(row):
                        
                        obj.collision = lambda: obj.rep.get_rect(topleft=[obj.pos[0] * self.camera.scale, obj.pos[1] * self.camera.scale]).collidepoint
                        if obj.collision()(mouse_offset):
                                match self.tool:
                                    case "paint":
                                        obj.change_color(self.current_color)
                                    case "eraser":
                                        obj.change_color((255, 255, 255))
                                    case "clear":
                                        self.grid.fill([self.current_color for _ in range(0, self.grid.size[0]*self.grid.size[1])])
                                    case "fill":
                                        self.grid.fill_color(self.color_palette, ff(
                                            np.array(self.grid.as_color(self.color_palette)), 
                                            (iy,ix), 
                                            self.grid.get_color_int(self.color_palette, self.current_color),
                                            connectivity=1))
                                    case "move":
                                        pass
                                    case _:
                                        print(f"{self.tool} was used")
            # Color palette events
                for iy, row in enumerate(self.color_palette.data):
                        for ix, obj in enumerate(row):
                            if obj.active is True and obj.collision()(mouse_pos):
                                    self.current_color = obj.col
                                    self.selected_color_bar.pos = [
                                        self.color_palette.data[iy][ix].pos[0]-1, 
                                        self.color_palette.data[iy][ix].pos[1]-1
                                    ]
            # Tool bar events
                for tool,obj in self.tools.items():
                    if obj.collision()(mouse_pos):
                        self.tool = tool
                        
                            
                for tool,obj in self.save_load.items():
                    if obj.collision()(mouse_pos):
                        if tool == "save":
                            self.save_load["save"].rep = self.save_load["save"].clicked_image
                            save_file(self.grid)
                        elif tool == "load":
                            self.save_load["load"].rep = self.save_load["load"].clicked_image
                            loaded_grid = load_file()
                            if loaded_grid:
                                self.grid = loaded_grid
                            else:
                                continue
                        
            else:
                self.save_load["save"].rep = self.save_load["save"].normal_image
                self.save_load["load"].rep = self.save_load["load"].normal_image
                
            
            # Other events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        self.tool = "move"
                        
                elif event.type == pygame.KEYUP:
                    if event.key == K_SPACE:
                        self.tool = "paint"
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        self.camera.scale = min(self.camera.scale + 0.1, 10)
                    elif event.button == 5:  # Scroll down
                        self.camera.scale = max(self.camera.scale - 0.1, 0.1)
            #endregion
            
            #region Drawing
            self.screen.fill((40, 40, 40))
            
            # Draw pixel grid
            for row in self.grid.data:
                for obj in row:
                    obj_scaled = pygame.transform.scale(obj.rep, (self.camera.scale * self.grid.cell_size, self.camera.scale * self.grid.cell_size))
                    self.screen.blit(obj_scaled, [obj.pos[0] * self.camera.scale + self.camera.pos[0], obj.pos[1] * self.camera.scale + self.camera.pos[1]])
                    # self.screen.blit(obj.rep, [obj.pos[0]+self.camera.pos[0], obj.pos[1]+self.camera.pos[1]])
                    
            # Switch tools 
            self.tools[self.tool].rep = self.tools[self.tool].clicked_image
            for tool, obj in self.tools.items():
                if tool == self.tool:
                    continue
                else:
                    obj.rep = obj.normal_image
                            
            # Draw tool bar backing
            self.screen.blit(self.tool_bar.rep, self.tool_bar.pos)
            # Draw tools
            for obj in self.tools.values():
                self.screen.blit(obj.rep, obj.pos)
            for obj in self.save_load.values():
                self.screen.blit(obj.rep, obj.pos)
                
            # Draw color palette
            self.screen.blit(self.selected_color_bar.rep, self.selected_color_bar.pos)
            for row in self.color_palette.data:
                for obj in row:
                    if obj.active:
                        self.screen.blit(obj.rep, obj.pos)
                        
            # Draw cursor
            # Invert the color of the pixel under the cursor    
            if mouse_pressed[0]:
                self.cursor_surface = self.cursor_pressed_images[self.tool]
            else:
                self.cursor_surface = self.cursor_images[self.tool]
            try:
                self.screen.blit(invert_surface(self.cursor_surface, self.screen, mouse_pos), mouse_pos)
            except:
                self.screen.blit(self.cursor_surface, (mouse_pos[0]+2, mouse_pos[1]+2))
            pygame.display.flip()
            #endregion
            
            # Clear events after use
            pygame.event.pump()
            
        pygame.quit()   
    
            
if (__name__ == '__main__'):
    Program((500,500)).main()