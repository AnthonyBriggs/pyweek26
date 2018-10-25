import pygame
from pgzero.actor import Actor

import data

class TrainingManualKiosk(Actor):
    
    def __init__(self, game, grid_x, grid_y, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.game = game
        self.name = 'training_manual_kiosk'
        image_name = 'players/training_manual_kiosk'.format()
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        
    def draw(self):
        super().draw()
    
    def update(self, dt):
        pass


class TrainingManual(object):
    """The actual manual, displayed when the player activates the kiosk.

    page 1, control instructions (ie. hold to set direction)
    page 2 on, the machines that can be built
    """
    def __init__(self, game):
        self.game = game
        self.page = 1
        self.timer = 0.0
        self.x_move = 0
        
        # UI images used to build the screens
        self.corner = images.players.display_corner
        self.edge = images.players.display_edge
        self.center = images.players.display_center
        self.right = images.players.direction_1
        self.left = images.players.direction_3
        
    def draw(self):
        self.draw_background()
        if self.page == 1:
            self.show_help_page()
        else:
            self.show_machine_page()
    
    def draw_background(self):
        """Draws the basic screen used when showing the manual."""
        # top corner is 70,70, then 10 across and 8 down
        # corners
        for pos in [(700,70), (700,560), (70,560), (70,70)]:
            self.game.blit(self.corner, pos)
            self.corner = pygame.transform.rotate(self.corner, -90)
        
        # edges
        xrange = list(range(140, 700, 70))
        yrange = list(range(140, 560, 70))
        #print(xrange, yrange)
        
        # top
        for x in xrange:
            self.game.blit(self.edge, (x, 70))
        self.edge = pygame.transform.rotate(self.edge, -90)
        for y in yrange:
            self.game.blit(self.edge, (700, y))
        self.edge = pygame.transform.rotate(self.edge, -90)
        for x in xrange:
            self.game.blit(self.edge, (x, 560))
        self.edge = pygame.transform.rotate(self.edge, -90)
        for y in yrange:
            self.game.blit(self.edge, (70, y))
        self.edge = pygame.transform.rotate(self.edge, -90)
        
        # middle
        for x in xrange:
            for y in yrange:
                self.game.blit(self.center, (x,y))
    
    def show_left_arrow(self):
        self.game.blit(self.left, (50, 300))

    def show_right_arrow(self):
        self.game.blit(self.right, (750, 300))
    
    def title(self, text):
        self.game.text(text,
            pos=(100,100), width=650, color="white",
            fontname="kenney space", fontsize=16)

    def subtitle(self, text):
        self.game.text(text,
            pos=(100,130), width=650, color="white",
            fontname="kenney space", fontsize=14)

    def paragraph(self, y, text):
        self.game.text(text,
            pos=(100,y), width=650, color="white",
            fontname="kenney space", fontsize=13, lineheight=1.2)
            
    def show_help_page(self):
        self.title("Arcturus Corporation Toy Factory ")
        self.subtitle("Employee training manual")
        self.paragraph(175, "This toy factory is a fully automated "
            "production line requiring minimal maintenance and "
            "intervention once initially set up.")
        self.paragraph(290, "The Arcturus production system utilizes "
            "conveyors to deliver goods and raw materials around the factory. "
            "Place units with the button function within your suit. "
            "Longer depress times will activate the conveyor's holographic "
            "directional guide.")
        self.paragraph(480, "Modular machine production units have "
            "been delivered, but may required some assembly. Relevant "
            " MMPU user guides are available on further pages.")
        self.paragraph(585, "(B) or (space) to return to your duties.")
        self.show_right_arrow()
    
    def show_machine_page(self):
        # which machine are we showing? Only show ones we've unlocked
        #machine_name = self.game.this_level['help'][self.page - 1]
        # debug - show more machines than we've unlocked at the start.
        halp = ['circuit_board', 'book', 'axe', 'bowl', 'coffee']
        machine_name = halp[self.page - 1]
        
        # build temp machine
        mm = data.multimachines[machine_name]
        
        # display it
        self.title(machine_name)

        # arrows
        self.show_left_arrow()
        #if self.page < len(game.this_level.help):
        #    self.show_right_arrow()
        # debug
        halp = ['circuit_board', 'book', 'axe', 'bowl', 'coffee']
        if self.page < len(halp):
            self.show_right_arrow()

    def update(self, dt):
        self.timer -= dt
        if self.timer < 0:
            self.timer = 0
        
        # we only move if the timer has counted down,
        # to prevent the manual moving too fast
        if self.x_move and self.timer == 0:
            if self.x_move < 0:
                self.page -= 1
                self.timer = 1
                print("left")
            else:
                self.page += 1
                self.timer = 1
                print("right")
            print("moving?", self.x_move, self.timer, "page:", self.page)
        
        # constrain to legit pages
        if self.page < 1:
            self.page = 1
        #if self.page > len(game.this_level.help):
        #    self.page = len(game.this_level.help)
        # debug
        halp = ['circuit_board', 'book', 'axe', 'bowl', 'coffee']
        if self.page > len(halp):
            self.page = len(halp)
    
    
    def handle_button_down(self, button):
        if button == joybutton.ONE:  # B button
            self.game.show_training_manual = False
        pass
    
    def handle_button_up(self, button):
        pass
    
    def handle_axis(self, axis, value):
        if axis == axis.X:
            if value == 0:
                # reset the timer so that players
                # can click rapidly through if necessary
                self.timer = 0
                self.x_move = 0
            else:
                self.x_move = value
            print(axis, value, self.x_move)

    
    # TODO: will need to handle keys