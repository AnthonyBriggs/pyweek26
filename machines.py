import sys

from pgzero.actor import Actor

class Conveyor(Actor):
    
    def __init__(self, game, grid_x, grid_y, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.game = game
        image_name = 'machines/conveyor_middle'.format()
        super().__init__(image_name, *args, **kwargs)
        self.facing_left = False
        self.carried = False
        self.highlight = False
    
    def __str__(self):
        return "<Conveyor, position: {}>".format(self.pos)
    
    def draw(self):
        super().draw()
    
    def update(self):
        if not self.carried:
            new_pos = self.game.convert_from_grid(self.grid_x, self.grid_y)
            self.x = new_pos[0]
            self.y = new_pos[1]
        pass
        
    # find neighbors to push to