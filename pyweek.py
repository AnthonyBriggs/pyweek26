# Write your code here :-)

import random
import sys

from player import Player
from machines import Conveyor, OreChute, LoadingDock, StampyThing

HEIGHT = 10 * 70
WIDTH = 12 * 70


class Game(object):
    "Simple class, used to pass globals around :>"
    
    def __init__(self, HEIGHT, WIDTH):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
    
        # dict of Player objects, indexed by joystick number
        # might need to map joystick number to player instead, and
        # start with player 1, etc. - or disable the GCN adapter?
        self.players = {}
        self.machines = {}
        
        self.GRID_SIZE = 70
        self.GRID_WIDTH = int(WIDTH / self.GRID_SIZE)
        self.GRID_HEIGHT = int(HEIGHT / self.GRID_SIZE)

        # random scattering of conveyors for now, to test pick up + put down
        # indexed by position in the grid, (x,y)
        # conveyor images are 70 x 70, so that's our grid
        for i in range(18):
            x = random.randint(1, self.GRID_WIDTH)
            y = random.randint(1, self.GRID_HEIGHT)
            self.machines[(x,y)] = Conveyor(self, x, y, anchor=(0,30))
    
        self.machines[(0,5)] = OreChute(self, 0, 5, "copper_ingot", 10, anchor=(0, 70))
        self.machines[(self.GRID_WIDTH-1,5)] = LoadingDock(self, self.GRID_WIDTH-1, 5, "circuit_board", 8, anchor=(0, 70))
        self.machines[(5,5)] = StampyThing(self, 5, 5, 
                                    item_input="copper_ingot", item_output="circuit_board", stamping_time=8,
                                    anchor=(0, 70))

    def point(self, pos, color=(255,0,0)):
        screen.draw.circle(pos, 5, color)
        
    def convert_to_grid(self, x, y):
        return (int(x / self.GRID_SIZE),
                int(y / self.GRID_SIZE))

    def convert_from_grid(self, grid_x, grid_y):
        return (grid_x * self.GRID_SIZE,
                grid_y * self.GRID_SIZE)

game = Game(HEIGHT, WIDTH)
print("Game initialised")

print(game.convert_from_grid(1,1))

def draw():
    screen.clear()
    
    # draw a grid so we can tell what's going on with positioning
    for i in range(0, game.WIDTH, game.GRID_SIZE):
        screen.draw.line((i,0), (i, game.HEIGHT), (66,33,33))
    for j in range(0, game.HEIGHT, game.GRID_SIZE):
        screen.draw.line((0,j), (game.WIDTH, j), (33,66,33))
    
    # TODO: draw according to grid depth/height in the factory
    for player in game.players.values():
        player.draw()
    for machine in game.machines.values():
        machine.draw()
    # we draw items second, otherwise there's some visible overlap
    # when moving from one conveyor to the next
    for machine in game.machines.values():
        if type(machine) is Conveyor:
            machine.draw_item()

def update(dt):
    for player in game.players.values():
        player.update(dt)
    for machine in game.machines.values():
        machine.update(dt)


def on_joy_button_down(joy, button):
    #print("Mu button down:", joy, button)
    # hack to get around GCN adapter
    player_no = int(joy) - 4 + 1
    # TODO: hardcoded buttons - will change per controller
    if button in (joybutton.SIX, joybutton.SEVEN):
        if player_no not in game.players:
            #spawn a new player
            game.players[player_no] = Player(game, player_no, anchor=(0,70))
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