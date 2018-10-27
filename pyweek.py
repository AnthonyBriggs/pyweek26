# Write your code here :-)

import random
import sys
import time

from player import Player
from conveyors import Conveyor, ConveyorCross, Turntable
from machines import OreChute, LoadingDock, MachinePart
from items import Item
from training import TrainingManualKiosk, TrainingManual
import data


# Work this out from the size of the screen + go fullscreen?
HEIGHT = 10 * 70
WIDTH = 12 * 70

# TODO (wishlist): more alien types (8?)

class Game(object):
    "Simple class, used to pass globals around :>"
    
    def __init__(self, HEIGHT, WIDTH):
        # TODO: fullscreen + center integral grid in the window
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        
        # conveyor images are 70 x 70, so that's our grid
        self.GRID_SIZE = 70
        self.GRID_WIDTH = int(WIDTH / self.GRID_SIZE)
        self.GRID_HEIGHT = int(HEIGHT / self.GRID_SIZE)
        
        # dict of Player objects, indexed by joystick number
        # might need to map joystick number to player instead, and
        # start with player 1, etc. - or disable the GCN adapter?
        self.players = {}
        self.multimachines = []
        self.products_required = {}
        
        self.show_training_manual = False
        # The actual manual, displayed over the top
        self.training_manual = TrainingManual(self)
        
        self.start_time = time.time()
        self.level_start_time = None
        self.level_finish_time = None
        
        self.level = 0
        self.load_level()
        
    def load_level(self, level=None):
        if level is None:
            level = self.level
        level_name = data.level_order[level]
        this_level = data.levels[level_name]
        self.this_level = this_level
        self.level_name = level_name
        
        print("Loading products required...")
        for number, product_name in this_level['products']:
            self.products_required[product_name] = number
        
        print("Initialising map...")
        self.map = {}
        # entry door, training manual, etc. (fixtures)
        self.door = Actor('players/door_closedmid', pos=(0, 105), anchor=(0,70))
        self.door.flip = False
        self.door_top = Actor('players/door_closedtop', pos=(0, 35), anchor=(0,70))
        self.door_top.flip = False
        
        self.training_manual_kiosk = TrainingManualKiosk(
                self, 7, 0, anchor=(0, 70))
        self.training_manual_kiosk.flip = False
        self.map[(7,0)] = self.training_manual_kiosk
        
        print("Ore chutes...")
        # raw material chutes
        # TODO: ore_time in data??
        for each_input in this_level['inputs']:
            print("  adding", each_input)
            y = random.randint(2, self.GRID_HEIGHT - 2)
            while (0, y) in self.map:
                y = random.randint(2, self.GRID_HEIGHT - 2)
            self.map[(0, y)] = OreChute(
                self, 0, y, each_input, ore_time=5, anchor=(0,70))
        
        print("Loading docks...")
        # loading docks
        # TODO: loading_time in data??
        x = self.GRID_WIDTH - 1
        for number, each_product in this_level['products']:
            y = random.randint(2, self.GRID_HEIGHT - 2)
            while (x, y) in self.map:
                y = random.randint(2, self.GRID_HEIGHT - 2)
            self.map[(x, y)] = LoadingDock(
                self, x, y, each_product, loading_time=5, anchor=(0,70))
        
        print("Adding machines...")
        # place machines randomly
        for machine_code in this_level['machines']:
            if machine_code == ' ':
                continue
            x = random.randint(1, self.GRID_WIDTH - 2)
            y = random.randint(1, self.GRID_HEIGHT - 2)
            while (x, y) in self.map:
                x = random.randint(2, self.GRID_WIDTH - 2)
                y = random.randint(2, self.GRID_HEIGHT - 2)
            m_data = data.machines[machine_code]
            self.map[(x,y)] = MachinePart(
                self, x, y, m_data['number'], machine_code, 
                parts=m_data['parts'], anchor=(0,70))
        
        print("Conveyor belts...")
        # conveyors
        x = random.randint(2, self.GRID_WIDTH - 1)
        y = random.randint(1, self.GRID_HEIGHT - 1)
        for i in range(this_level['conveyors']):
            while (x,y) in self.map:
                # pick a new coordinate, maybe this one will be blank? :)
                x = random.randint(2, self.GRID_WIDTH - 1)
                y = random.randint(1, self.GRID_HEIGHT - 1)
            self.map[(x,y)] = Conveyor(self, x, y, anchor=(0,30))
        
        print("Crossover conveyors...")
        x = random.randint(2, self.GRID_WIDTH - 1)
        y = random.randint(1, self.GRID_HEIGHT - 1)
        for i in range(this_level['conveyor_crosses']):
            while (x,y) in self.map:
                # pick a new coordinate, maybe this one will be blank? :)
                x = random.randint(2, self.GRID_WIDTH - 1)
                y = random.randint(1, self.GRID_HEIGHT - 1)
            self.map[(x,y)] = ConveyorCross(self, x, y, anchor=(0,70))
        
        print("Turntables...")
        x = random.randint(2, self.GRID_WIDTH - 1)
        y = random.randint(1, self.GRID_HEIGHT - 1)
        for i in range(this_level['turntables']):
            while (x,y) in self.map:
                # pick a new coordinate, maybe this one will be blank? :)
                x = random.randint(2, self.GRID_WIDTH - 1)
                y = random.randint(1, self.GRID_HEIGHT - 1)
            self.map[(x,y)] = Turntable(self, x, y, anchor=(0,70))
            
        print("Level loading complete.")
        self.level_start_time = time.time()
        print("Started timer:", self.level_start_time)
        
    def draw(self):
        self.door.draw()
        self.door_top.draw()
        self.training_manual_kiosk.draw()
        
    def update(self, dt):
        #print(time.time(), self.level_start_time, self.level_finish_time)
        
        # Check to see if we've produced everything
        remaining = [(p, n) for p, n in self.products_required.items() if n > 0]
        if not remaining:
            self.level_finish_time = time.time()
            
            # Show win screen + time, load next level
            self.show_training_manual = True
            self.training_manual.level_end = True
            self.training_manual.level_end_text = [
                ('title', 'Well done, employee!'),
                ('subtitle', 'further promotions await'),
                ('paragraph', 175, 'Production this level:'), ]
            
            line_count = 1
            for number, product_name in self.this_level['products']:
                actual = number - self.products_required[product_name]
                text = "{}   {}".format(actual, product_name)
                self.training_manual.level_end_text.append(
                    ('paragraph',
                     175 + 30 * line_count, 
                     '    {}  >>  {}'.format(product_name.replace('_', ' '), number)))
                line_count += 1
            
            self.training_manual.level_end_text.append(
                    ('paragraph', 500, "Level time: {0:.2f} seconds".format(
                        self.level_finish_time - self.level_start_time)))
            self.training_manual.level_end_text.append(
                    ('paragraph', 550, "Total time: {0:.2f} seconds".format(
                        self.level_finish_time - self.start_time)))
            
            if self.level < len(data.level_order) - 1:
                print("Switching to level", self.level + 1)
                self.level += 1
                print("Loading next level...")
                self.load_level()
            else:
                print("Ran out of levels, so I guess you won the game! :D")
                # TODO: show a 'you win the game screen'
        else:
            # update HUD
            #print("Remaining products:", remaining)
            pass
    
    def point(self, pos, color=(255,0,0)):
        screen.draw.circle(pos, 5, color)
    
    # grid (0,0) is actually (0,70)
    
    def convert_to_grid(self, x, y):
        return (int(x / self.GRID_SIZE),
                int(y / self.GRID_SIZE) - 1)

    def convert_from_grid(self, grid_x, grid_y):
        return ((grid_x) * self.GRID_SIZE,
                (grid_y+1) * self.GRID_SIZE)
    
    def blit(self, image, pos):
        screen.blit(image, pos)
    
    def text(self, text, pos, *args, **kwargs):
        # topright=(840, 20), color="orange", fontname="Boogaloo", fontsize=60
        # width=180, lineheight=1.5
        # https://pygame-zero.readthedocs.io/en/stable/ptext.html
        screen.draw.text(text, pos, *args, **kwargs)

game = Game(HEIGHT, WIDTH)
print("Game initialised")


def draw():
    screen.clear()
    
    # draw a grid so we can tell what's going on with positioning
    for i in range(0, game.WIDTH, game.GRID_SIZE):
        screen.draw.line((i,0), (i, game.HEIGHT), (66,33,33))
    for j in range(0, game.HEIGHT, game.GRID_SIZE):
        screen.draw.line((0,j), (game.WIDTH, j), (33,66,33))
    game.draw()
    
    # TODO: draw according to grid depth/height in the factory
    for player in game.players.values():
        player.draw()
    for machine in game.map.values():
        machine.draw()
    for machine in game.map.values():
        for part in getattr(machine, '_sub_parts', {}).values():
            part.draw()

    # we draw items second, otherwise there's some visible overlap
    # when moving from one conveyor to the next
    for machine in game.map.values():
        if type(machine) in (Conveyor, ConveyorCross, Turntable):
            machine.draw_item()
            
    # finally, highlights over the top
    for player in game.players.values():
        player.draw_highlight()
    
    # training manual
    if game.show_training_manual and game.training_manual:
        game.training_manual.draw()
    
    elapsed_time = time.time() - game.level_start_time
    if elapsed_time >= 60:
        elapsed_text = str(int(elapsed_time // 60)) + ":{0:.1f}".format(elapsed_time % 60)
    else:
        elapsed_text = "{0:.1f}".format(elapsed_time % 60)
    screen.draw.text(elapsed_text, (70*8 + 20, 10))
    
def update(dt):
    game.update(dt)
    for player in game.players.values():
        player.update(dt)
    for machine in game.map.values():
        machine.update(dt)
    for multimachine in game.multimachines:
        multimachine.update(dt)
    if game.show_training_manual and game.training_manual:
        game.training_manual.update(dt)
    
def on_joy_button_down(joy, button):
    #print("Mu button down:", joy, button)
    # hack to get around GCN adapter
    player_no = int(joy) - 4 + 1
    
    if game.show_training_manual:
        # send buttons and axis to the training manual instead
        game.training_manual.handle_button_down(button)
        return
        
    # TODO: hardcoded buttons - will change per controller
    if button in (joybutton.SIX, joybutton.SEVEN):
        if player_no not in game.players:
            #spawn a new player
            game.players[player_no] = Player(game, player_no)
        else:
            # remove 'em, but handle the press first, to give us
            # a chance to do things before they're removed
            game.players[player_no].handle_button(button)
            del game.players[player_no]
    
    if player_no in game.players:
        game.players[player_no].handle_button_down(button)
        
def on_joy_button_up(joy, button):
    #print("Mu button down:", joy, button)
    # hack to get around GCN adapter
    player_no = int(joy) - 4 + 1
    
    if game.show_training_manual:
        # send buttons and axis to the training manual instead
        game.training_manual.handle_button_up(button)
        return
    
    if player_no in game.players:
        game.players[player_no].handle_button_up(button)

def sanitise_axis(value):
    # make a small 'dead spot' in the middle or we'll drift
    if -0.05 < value < 0.05:
        return 0
    else:
        return value

def on_joy_axis_motion(joy, axis, value):
    #print("Mu joystick move:", joy, axis, value)

    if game.show_training_manual:
        # send buttons and axis to the training manual instead
        game.training_manual.handle_axis(axis, sanitise_axis(value))
        return
    
    # hack to get around GCN adapter
    player_no = int(joy) - 4 + 1
    if player_no in game.players:
        game.players[player_no].handle_axis(axis, sanitise_axis(value))


def on_key_down(key):
    print(key)
    
    if key == keys.ESCAPE:
        if game.show_training_manual:
            # Accidentally pushed this a few times while reading :)
            game.show_training_manual = False
        else:
            print("Thanks for playing!")
            sys.exit()

    # debug / testing stuff
    numbers = [keys.K_1, keys.K_2, keys.K_3, keys.K_4, keys.K_5,
               keys.K_6, keys.K_7, keys.K_8, keys.K_9, keys.K_0]
    if key in numbers:
        # change level
        new_level = numbers.index(key)
        if new_level < len(data.level_order):
            game.level = new_level
            game.load_level()
    
    if key == keys.F1:
        # show the first machine page
        game.training_manual.page = 2
        game.show_training_manual = True
        
    if key == keys.F5:
        # finish level immediately
        for k in game.products_required:
            game.products_required[k] = 0
    
    if key == keys.F4:
        # Add extra products to required items
        for k in game.products_required:
            game.products_required[k] += 1

    if key == keys.F3:
        # Subtract products from required items
        for k in game.products_required:
            game.products_required[k] -= 1

    # TODO: add keys for players 1 and 2 (split keyboard)
    # P1: WASD + space/alt,
    # P2: arrows + left shift/enter

def on_mouse_down(pos, button):
    print("Mouse button clicked!")

def on_mouse_move(pos, rel, buttons):
    # rel = position compared to previous
    #print("Mouse moved!", pos, rel, buttons)
    pass