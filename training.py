from pgzero.actor import Actor

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

    page 1, simple control instructions (ie. hold to set direction)
    page 2 on, the machines that can be built
    
    This is a sort-of dummy test manual. It has some things in it.
    """
    def __init__(self, game):
        self.game = game
        self.page = 1
        self.page_display = Actor('players/training_manual_test', anchor=(0,0))
        self.page_display.flip = False  # WHY is this being set???
        #print(self.page_display, self.page_display.flip, self.page_display.pos, self.page_display.scale)
        #self.page_display.x = 100
        #self.page_display.y = 100
        
    def draw(self):
        self.page_display.draw()
        
    def update(self, dt):
        pass
    
    def handle_button_down(self, button):
        if button == joybutton.ONE:  # B button
            self.game.show_training_manual = False
        pass
    
    def handle_button_up(self, button):
        pass
    
    def handle_axis(self, axis, value):
        pass