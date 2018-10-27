from pgzero.actor import Actor


class Conveyor(Actor):
    def __init__(self, game, grid_x, grid_y, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.name = "conveyor_belt"
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
        return "<Conveyor, position: {}, item:{}/{}, direction: {}>".format(
                    self.pos, self.item, self.item_pos, self.direction)
    __repr__ = __str__
    
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
        #self.game.point(self.pos, (0,0,255))
    
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
            self.item.pos = (self.x + 32, 
                             self.y - self.game.GRID_SIZE + self.item_pos + 12)
        if self.direction == 3:
            # right to left
            self.item.pos = (self.x + self.game.GRID_SIZE - self.item_pos, 
                             self.y - 28)

        self.item.draw()
        #self.game.point(self.item.pos, (0,255,255))
    
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
                conveyor = self.game.map.get(target_grid, None)
                if conveyor and hasattr(conveyor, 'receive_item_push'):
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


class ConveyorCross(Actor):
    """Two conveyor belts that cross at right angles."""
    
    def __init__(self, game, grid_x, grid_y, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.name = "conveyor_cross"
        self.game = game
        image_name = 'machines/conveyor_cross_1'.format()
        super().__init__(image_name, *args, **kwargs)
        self.carried = False
        self.highlight = False
        
        # things and their positions
        self.item = None
        self.item_pos = 0
        self.item2 = None
        self.item2_pos = 0
        self.speed = self.game.GRID_SIZE / 2     # 2 seconds end to end
        
        # which way items are going on belt 1 (self.item).
        # ['north', 'east', 'south', 'west']
        self.direction = 1
        
    def __str__(self):
        return "<Conveyor Crossover, position: {}, items:{}/{} and {}/{}, direction: {}>".format(
                    self.pos, self.item, self.item_pos, 
                    self.item2, self.item2_pos, self.direction)
    __repr__ = __str__
    
    def draw(self):
        super().draw()
        #self.game.point(self.pos, (0,0,255))
    
    def draw_item(self):
        for index, item, pos in [
                        (0, self.item, self.item_pos),
                        (1, self.item2, self.item2_pos)]:
            if item is None:
                continue
            #print("drawing", item, pos)
            direction = (self.direction + index) % 4
            if direction == 0:
                # bottom to top
                item.pos = (self.x + 32, self.y - pos + 12)
            if direction == 1:
                # left to right
                item.pos = (self.x + pos, self.y - 28)
            if direction == 2:
                # top to bottom
                item.pos = (self.x + 32, 
                            self.y - self.game.GRID_SIZE + pos + 12)
            if direction == 3:
                # right to left
                item.pos = (self.x + self.game.GRID_SIZE - pos, 
                            self.y - 28)
            item.draw()
            #self.game.point(item.pos, (0,255,255))

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
                conveyor = self.game.map.get(target_grid, None)
                if conveyor and hasattr(conveyor, 'receive_item_push'):
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
        
        if self.item2:
            # UUUgly :D
            self.item2_pos += self.speed * dt
            if self.item2_pos >= self.game.GRID_SIZE:
                self.item2_pos = self.game.GRID_SIZE
                # need to push off the end
                target_grid = self.get_target_grid(direction = (self.direction + 1) % 4)
                conveyor = self.game.map.get(target_grid, None)
                if conveyor and hasattr(conveyor, 'receive_item_push'):
                    from_direction = [2, 3, 0, 1][self.direction]   # 0123 -> 2301
                    #print("Attempting to push", from_direction, "from", self, "to", conveyor)
                    success = conveyor.receive_item_push(self.item2, from_direction)
                    if success:
                        self.item2 = None
                        self.item2_pos = 0
                    else:
                        #stalled
                        pass
        else:
            self.item2_pos = 0
    
    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        # which belt?
        #print(self, "received push request:", item, from_direction)
        if from_direction in (self.direction, (self.direction + 1) % 4):
            #print("Denied, since it's incoming")
            return False
        elif from_direction == ((self.direction + 2) % 4):
            # belt 1, probably
            if self.item:
                return False
            else:
                #print("received on belt 1")
                self.item = item
                self.item_pos = 0
                return True
        else:
            # belt 2
            if self.item2:
                return False
            else:
                #print("received on belt 2")
                self.item2 = item
                self.item2_pos = 0
                return True

    def get_target_grid(self, direction=None):
        """Where is this conveyor pushing to?"""
        if direction is None:
            direction = self.direction
        if direction == 0:
            return (self.grid_x, self.grid_y - 1)
        if direction == 1:
            return (self.grid_x + 1, self.grid_y)
        if direction == 2:
            return (self.grid_x, self.grid_y + 1)
        if direction == 3:
            return (self.grid_x - 1, self.grid_y)


class Turntable(Actor):
    """Essentially a round conveyor belt. Will accept pushing
    from any angle, and will turn 90 degrees every so often,
    pushing to the first available neighbor."""
    
    def __init__(self, game, grid_x, grid_y, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.name = "turntable"
        self.game = game
        image_name = 'machines/turntable'.format()
        super().__init__(image_name, *args, **kwargs)
        self.carried = False
        
        # things and their positions
        self.item = None
        #self.item_pos = 0
        #self.speed = self.game.GRID_SIZE / 2     # 2 seconds end to end
        self.next_turn = 1.0
        
        # which way we're "facing".
        # ['north', 'east', 'south', 'west']
        self.direction = 1
        
    def __str__(self):
        return "<Turntable, items:{}, direction: {}>".format(
                    self.item, self.direction)
    __repr__ = __str__
    
    def draw(self):
        super().draw()
        #self.game.point(self.pos, (0,0,255))

    def draw_item(self):
        # just draw it in the middle for now...
        if self.item:
            self.item.draw()
    
    def update(self, dt):
        if not self.carried:
            new_pos = self.game.convert_from_grid(self.grid_x, self.grid_y)
            self.x = new_pos[0]
            self.y = new_pos[1]
        
        # turn every second?
        self.next_turn -= dt
        if self.next_turn <= 0:
            self.direction = (self.direction + 1 ) % 4
            self.next_turn = 1.0
            #print("Turn, turn")
        
        if self.item:
            self.item.pos = (self.x + 35, self.y - 10) # center?
            target_grid = self.get_target_grid()
            conveyor = self.game.map.get(target_grid, None)
            if conveyor and hasattr(conveyor, 'receive_item_push'):
                from_direction = [2, 3, 0, 1][self.direction]   # 0123 -> 2301
                #print("Turntable attempting to push", from_direction, "from", self, "to", conveyor)
                success = conveyor.receive_item_push(self.item, from_direction)
                if success:
                    self.item = None
                    #self.item_pos = 0
                else:
                    #stalled
                    pass
    
    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        if self.item:
            #print (self, "Denied push from", from_direction, "(", self.direction, ")")
            return False
        if from_direction == self.direction:
            #print (self, "Denied push from", from_direction, "(", self.direction, ")")
            return False
        self.item = item
        #self.item_pos = 0
        return True

    def get_target_grid(self, direction=None):
        """Where is this conveyor pushing to?"""
        if direction is None:
            direction = self.direction
        if direction == 0:
            return (self.grid_x, self.grid_y - 1)
        if direction == 1:
            return (self.grid_x + 1, self.grid_y)
        if direction == 2:
            return (self.grid_x, self.grid_y + 1)
        if direction == 3:
            return (self.grid_x - 1, self.grid_y)