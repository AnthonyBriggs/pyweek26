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
        self.carried = False
        self.highlight = False
        
        # thing and its position
        self.item = None
        self.item_pos = 0
        self.speed = self.game.GRID_SIZE / 2     # 2 seconds end to end
        
        # which way items are going. ['north', 'east', 'south', 'west']
        self.direction = 1
        
        
    def __str__(self):
        return "<Conveyor, position: {}, item:{}/{}, direction: {}>".format(self.pos, self.item, self.item_pos, self.direction)
    
    def draw(self):
        if self.direction in (0, 2):
            self.anchor = (0, 70)
            frame = int((self.item_pos / 2) % 6 + 1)
            if self.direction == 0:
                # backwards! 123456  654321
                frame = 7 - frame
            self.image = "machines/conveyor_up_{}".format(frame)
        else:
            self.anchor = (0, 30)
            self.image = "machines/conveyor_middle"
        super().draw()
        self.game.point(self.pos, (0,0,255))
    
    def draw_item(self):
        if not self.item:
            return
        
        if self.direction == 0:
            # bottom to top
            self.item.pos = (self.x + 32, self.y - self.item_pos + 12)
        if self.direction == 1:
            # left to right
            self.item.pos = (self.x + self.item_pos, self.y - 28)
        if self.direction == 2:
            # top to bottom
            self.item.pos = (self.x + 32, self.y - self.game.GRID_SIZE + self.item_pos + 12)
        if self.direction == 3:
            # right to left
            self.item.pos = (self.x + self.game.GRID_SIZE - self.item_pos, self.y - 28)

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
                target_grid = self.get_target_grid()
                conveyor = self.game.machines.get(target_grid, None)
                if conveyor:
                    from_direction = [2, 3, 0, 1][self.direction]   # 0123 -> 2301
                    #print("Attempting to push", from_direction, "from", self, "to", conveyor)
                    success = conveyor.receive_item_push(self.item, from_direction)
                    if success:
                        self.item = None
                        self.item_pos = 0
                    else:
                        #stalled
                        pass
        else:
            self.item_pos = 0
        
    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        if self.item:
            #print (self, "Denied push from", from_direction, "(", self.direction, ")")
            return False
        if from_direction == self.direction:
            #print (self, "Denied push from", from_direction, "(", self.direction, ")")
            return False
        self.item = item
        self.item_pos = 0
        return True

    def get_target_grid(self):
        """Where is this conveyor pushing to?"""
        if self.direction == 0:
            return (self.grid_x, self.grid_y - 1)
        if self.direction == 1:
            return (self.grid_x + 1, self.grid_y)
        if self.direction == 2:
            return (self.grid_x, self.grid_y + 1)
        if self.direction == 3:
            return (self.grid_x - 1, self.grid_y)


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
            success = conveyor.receive_item_push( Item(self.ore_type, anchor=(12, 26)), from_direction=3 )
            if not success:
                # hang onto it? Maybe have one in storage, periodically try to push,
                # create another if empty.
                # or just don't create it = backed up
                print("Ore Chute backed up!")
                pass
        else:
            # push it onto the floor? For now, do nothing
            pass
        
    