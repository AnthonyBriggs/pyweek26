import sys

from pgzero.actor import Actor
from items import Item


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
        
        # thing and its position
        self.item = None
        self.item_pos = 0
        self.speed = self.game.GRID_SIZE / 2     # 2 seconds end to end
        
    def __str__(self):
        return "<Conveyor, position: {}, item:{}/{}>".format(self.pos, self.item, self.item_pos)
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (0,0,255))
    
    def draw_item(self):
        if self.item:
            self.item.x = self.x + self.item_pos
            self.item.y = self.y - 11
            self.item.draw()
            self.game.point(self.item.pos, (0,255,255))
    
    def update(self, dt):
        if not self.carried:
            new_pos = self.game.convert_from_grid(self.grid_x, self.grid_y)
            self.x = new_pos[0]
            self.y = new_pos[1]
        
        if self.item:
            self.item_pos += self.speed * dt
            if self.item_pos >= self.game.GRID_SIZE:
                self.item_pos = self.game.GRID_SIZE
                # need to push off the end
                conveyor = self.game.machines.get((self.grid_x + 1, self.grid_y), None)
                if conveyor:
                    success = conveyor.push_from_left(self.item)
                    if success:
                        self.item = None
                        self.item_pos = 0
                    else:
                        #stalled
                        pass
        else:
            self.item_pos = 0
        
    # find neighbors to push to
    def push_from_left(self, item):
        """Receive an item from the left."""
        if self.item:
            return False
        self.item = item
        self.item_pos = 0
        return True


class OreChute(Actor):
    """Produces ore and raw materials of various types:
    copper, iron, organics, aluminium, glass.
    
    Ore is sent to the right, chutes can't be moved."""
    
    def __init__(self, game, grid_x, grid_y, ore_type, ore_time, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y

        self.game = game
        image_name = 'machines/ore_chute'
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        self.ore_type = ore_type
        self.ore_time = ore_time
        self.next_ore = ore_time
    
    def __str__(self):
        return "<OreChute, position: {}>".format(self.pos)
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (0,255,0))

    def update(self, dt):
        self.next_ore -= dt
        #print("Next ore in", self.next_ore)
        if self.next_ore <= 0:
            self.next_ore += self.ore_time
            self.send_ore()
            
    def send_ore(self):
        """Ore is sent to the right."""
        conveyor = self.game.machines.get((self.grid_x + 1, self.grid_y), None)
        if conveyor:
            success = conveyor.push_from_left( Item(self.ore_type, anchor=(12, 42)) )
            if not success:
                # hang onto it? Maybe have one in storage, periodically try to push,
                # create another if empty.
                # or just don't create it = backed up
                print("Ore Chute backed up!")
                pass
        else:
            # push it onto the floor? For now, do nothing
            pass
        
    