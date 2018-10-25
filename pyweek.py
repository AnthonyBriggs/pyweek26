# Write your code here :-)

import random
import sys

from player import Player
from machines import Conveyor, OreChute, LoadingDock, MachinePart
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
        self.level = 0
        self.load_level()
        self.show_training_manual = False
        # The actual manual, displayed over the top
        self.training_manual = TrainingManual(self)
        
    def load_level(self, level=None):
        if level is None:
            level = self.level
        level_name = data.level_order[level]
        this_level = data.levels[level_name]
        self.this_level = this_level
        self.level_name = level_name
        
        for number, product_name in this_level['products']:
            self.products_required[product_name] = number
        
        self.map = {}
        # entry door, training manual, etc. (fixtures)
        self.door = Actor('players/door_closedmid', pos=(0, 105), anchor=(0,70))
        self.door_top = Actor('players/door_closedtop', pos=(0, 35), anchor=(0,70))
        
        self.training_manual_kiosk = TrainingManualKiosk(self, 7, 0, anchor=(0, 70))
        self.map[(7,0)] = self.training_manual_kiosk
        
        # raw material chutes
        # TODO: ore_time in data??
        for each_input in this_level['inputs']:
            y = random.randint(2, self.GRID_HEIGHT - 2)
            while (0, y) in self.map:
                y = random.randint(2, self.GRID_HEIGHT - 2)
            self.map[(0, y)] = OreChute(self, 0, y, each_input, ore_time=7, anchor=(0,70))
        
        # loading docks
        # TODO: loading_time in data??
        x = self.GRID_WIDTH - 1
        for number, each_product in this_level['products']:
            y = random.randint(2, self.GRID_HEIGHT - 2)
            while (x, y) in self.map:
                y = random.randint(2, self.GRID_HEIGHT - 2)
            self.map[(x, y)] = LoadingDock(self, x, y, each_product, loading_time=10, anchor=(0,70))
        
        # place machines randomly
        for machine_code in this_level['machines']:
            x = random.randint(2, self.GRID_WIDTH - 2)
            y = random.randint(2, self.GRID_HEIGHT - 2)
            while (x, y) in self.map:
                x = random.randint(2, self.GRID_WIDTH - 2)
                y = random.randint(2, self.GRID_HEIGHT - 2)
            m_data = data.machines[machine_code]
            self.map[(x,y)] = MachinePart(self, x, y, m_data['number'], machine_code, parts=m_data['parts'], anchor=(0,70))
        
        # conveyors
        x = random.randint(2, self.GRID_WIDTH - 2)
        y = random.randint(2, self.GRID_HEIGHT - 2)
        for i in range(this_level['conveyors']):
            while (x,y) in self.map:
                # pick a new coordinate, maybe this one will be blank? :)
                x = random.randint(2, self.GRID_WIDTH - 2)
                y = random.randint(2, self.GRID_HEIGHT - 2)
            self.map[(x,y)] = Conveyor(self, x, y, anchor=(0,30))
    
    def draw(self):
        self.door.draw()
        self.door_top.draw()
        self.training_manual_kiosk.draw()
        
    def update(self, dt):
        # Check to see if we've produced everything
        remaining = [(p, n) for p, n in self.products_required.items() if n > 0]
        if not remaining:
            # Show win screen + time, load next level
            print ("Win!")
        else:
            # update HUD
            pass
        
    def show_help(self, thing_type, name):
        """Switch to help mode, called from the training manual square."""
        # TODO: pause?
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
        if type(machine) is Conveyor:
            machine.draw_item()
            
    # finally, highlights over the top
    for player in game.players.values():
        player.draw_highlight()
    
    # training manual
    if game.show_training_manual and game.training_manual:
        game.training_manual.draw()
        
def update(dt):
    game.update(dt)
    for player in game.players.values():
        player.update(dt)
    for machine in game.map.values():
        machine.update(dt)
    for multimachine in game.multimachines:
        multimachine.update(dt)

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
    # TODO: add keys for players 1 and 2 (split keyboard)
    if key == keys.ESCAPE:
        print("Thanks for playing!")
        sys.exit()

def on_mouse_down(pos, button):
    print("Mouse button clicked!")

def on_mouse_move(pos, rel, buttons):
    # rel = position compared to previous
    #print("Mouse moved!", pos, rel, buttons)
    pass