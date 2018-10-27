import pygame
from pgzero.actor import Actor

import data
from machines import MachinePart


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
        self.level_end = False
        self.level_end_text = []
        
        # UI images used to build the screens
        self.corner = images.players.display_corner
        self.edge = images.players.display_edge
        self.center = images.players.display_center
        self.right = images.players.direction_1
        self.left = images.players.direction_3
        
        self.dummy_game = None
    
    def draw(self):
        self.draw_background()
        if self.level_end:
            self.show_level_end_page()
        elif self.page == 1:
            self.show_help_page()
        else:
            self.show_machine_page()
    
    def draw_background(self, height=8, width=10):
        """Draws the basic screen used when showing the manual."""
        # top corner is 70,70, then 10 across and 8 down
        # corners
        grid = self.game.GRID_SIZE
        width_1 = self.game.GRID_SIZE
        width_p = width * self.game.GRID_SIZE       # default 700
        height_1 = self.game.GRID_SIZE
        height_p = height * self.game.GRID_SIZE     # default 560
        
        # starts top right
        for pos in [(width_p,height_1), (width_p,height_p), (width_1,height_p), (width_1, height_1)]:
            self.game.blit(self.corner, pos)
            self.corner = pygame.transform.rotate(self.corner, -90)
        
        # edges
        xrange = list(range(width_1 + grid, width_p, grid))
        yrange = list(range(height_1 + grid, height_p, grid))
        #print(xrange, yrange)
        
        # top
        for x in xrange:
            self.game.blit(self.edge, (x, height_1))
        self.edge = pygame.transform.rotate(self.edge, -90)
        for y in yrange:
            self.game.blit(self.edge, (width_p, y))
        self.edge = pygame.transform.rotate(self.edge, -90)
        for x in xrange:
            self.game.blit(self.edge, (x, height_p))
        self.edge = pygame.transform.rotate(self.edge, -90)
        for y in yrange:
            self.game.blit(self.edge, (width_1, y))
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
        if not self.dummy_game:
            self.dummy_game = self.build_new_machine()
        #print(self.dummy_game)
        
        # Draw cached machine
        # display it
        machine_name = self.game.this_level['help'][self.page - 2]
        
        inputs = []
        outputs = []
        for machine in self.dummy_game.map.values():
            machine.draw()
            for part in machine._sub_parts.values():
                part.x = machine.x + part.position[0]
                part.y = machine.y - part.position[1]
                part.draw()
            #print(machine)
            
            if machine.item_input:
                inputs.append(machine.item_input.replace("_", " "))
            if machine.item_output:
                outputs.append(machine.item_output.replace("_", " "))
            
        self.title(machine_name)
        self.paragraph(150, "Requires: {}".format(", ".join(inputs)))
        self.paragraph(200, "Produces: {}".format(", ".join(outputs)))
        
        # arrows
        self.show_left_arrow()
        if self.page < len(self.game.this_level['help']) + 1:
            self.show_right_arrow()
            
    def build_new_machine(self):
        # which machine are we showing? Only show ones we've unlocked
        #print(self.game.this_level['help'], self.page, self.page - 2)
        machine_name = self.game.this_level['help'][self.page - 2]
        
        # build temp machine and game
        mm = data.multimachines[machine_name]
        dummy_game = DummyGame()
        
        # add machines to the map, and call their on_put_down
        for index, machine_code in enumerate(mm['layout']):
            if machine_code == ' ':
                continue
            x = index % 3 + 5
            y = index // 3 + 5
            m_data = data.machines[machine_code]
            machine = MachinePart(dummy_game, x, y, 
                m_data['number'], machine_code, 
                parts=m_data['parts'], anchor=(0,70))
            dummy_game.map[(x,y)] = machine
            
            # call on_put_down to build the other inputs
            machine.on_put_down()
            
            # items?
        
        return dummy_game

    def show_level_end_page(self):
        for text_info in self.level_end_text:
            #print(text_info)
            f = getattr(self, text_info[0])
            if len(text_info) == 2:
                f(text=text_info[1])
            else:
                f(y=text_info[1], text=text_info[2])
        
    def update(self, dt):
        self.timer -= dt
        if self.timer < 0:
            self.timer = 0
        
        # we only move if the timer has counted down,
        # to prevent the manual moving too fast
        if self.x_move and self.timer == 0:
            if self.x_move < 0 and self.page > 1:
                self.page -= 1
                self.timer = 1
                self.dummy_game = None
                print("left")
            elif self.page < len(self.game.this_level['help']) + 1:
                self.page += 1
                self.timer = 1
                self.dummy_game = None
                print("right")
            #print("moving?", self.x_move, self.timer, "page:", self.page)
        
        # constrain to legit pages
        if self.page < 1:
            assert False, "page left too far"
        elif self.page > len(self.game.this_level['help']) + 1:
            assert False, "page right too far"
    
    def handle_button_down(self, button):
        if button == joybutton.ONE:  # B button
            self.game.show_training_manual = False
            self.level_end = False
            self.level_end_text = []
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
            #print(axis, value, self.x_move)

    # TODO: will need to handle keys

class DummyGame(object):
    
    def __init__(self):
        self.map = {}
        self.multimachines = []
        self.GRID_SIZE = 70
    
    def convert_to_grid(self, x, y):
        return (int(x / self.GRID_SIZE),
                int(y / self.GRID_SIZE) - 1)

    def convert_from_grid(self, grid_x, grid_y):
        return ((grid_x) * self.GRID_SIZE,
                (grid_y+1) * self.GRID_SIZE)
    
    def point(self, *args, **kwargs):
        pass