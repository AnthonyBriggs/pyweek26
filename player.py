import sys

from pgzero.actor import Actor

class Player(Actor):
    def __init__(self, game, number, *args, **kwargs):
        self.number = number
        self.game = game
        image_name = 'players/p{}/p{}_stand'.format(self.number, self.number)
        super().__init__(image_name, *args, **kwargs)
        self.speed = [0, 0]
        self.facing_left = False
        self.move_distance = 0
        self.carrying = False
        self.putting_down = False
        self.spawn()
        self.highlight = Actor('players/highlight', anchor=(0, 70))
        
    def __str__(self):
        return "<Player {}, position: {}>".format(self.number, self.pos)
    
    def set_image(self, image_name):
        self.image = 'players/p{}/p{}_{}'.format(self.number, self.number, image_name)
    
    def spawn(self):
        # TODO: find a blank spot on the screen to spawn into? 
        #       Or just have a spawn spot in the top left (clock on?)
        self.pos = 100, 100
    
    def draw(self):
        if self.carrying:
            machine, my_grid = self.find_space()
        else:
            machine, my_grid = self.find_machine()
        if self.carrying or machine:
            if self.putting_down:

                pos = self.game.convert_from_grid(*my_grid)
                direction = self.player_facing()
                if direction == 0:
                    self.highlight.pos = (pos[0], pos[1] - self.game.GRID_SIZE)
                elif direction == 2:
                    self.highlight.pos = (pos[0], pos[1] + self.game.GRID_SIZE)
                else:
                    self.highlight.pos = self.game.convert_from_grid(*my_grid)
                print("putting down at", my_grid, "->", self.highlight.pos)
            else:
                self.highlight.pos = self.game.convert_from_grid(*my_grid)
            self.highlight.draw()
        
        if self.speed == [0,0]:
            self.set_image('stand')
        else:
            step = int( (self.move_distance / 12 ) % 11 + 1 )
            self.set_image('walk{:0>2d}'.format(step))
        super().draw()
        
        if self.carrying:
            self.carrying.draw()
        
        self.game.point(self.pos)
        
    def update(self, dt):
        #print ("updating player", self.number)
        if not self.putting_down:
            # don't move if we're putting something down.
            self.x += self.speed[0]
            self.y += self.speed[1]
        if self.speed == [0,0] or self.putting_down:
            self.move_distance = 0     # stopped; reset walk distance
        else:
            self.move_distance += abs(self.speed[0]) + abs(self.speed[1])
        
        if self.speed[0] < 0:
            self.facing_left = True
        elif self.speed[0] > 0:
            self.facing_left = False
        self.flip = self.facing_left
        
        if self.right > self.game.WIDTH:
            self.right = self.game.WIDTH
        if self.left < 0:
            self.left = 0
        if self.top < 0:
            self.top = 0
        if self.bottom > self.game.HEIGHT:
            self.bottom = self.game.HEIGHT
    
        if self.carrying:
            self.carrying.y = self.y + 20
            if self.putting_down:
                direction = self.player_facing()
                self.carrying.direction = direction
                if direction == 0:
                    self.carrying.y -= self.game.GRID_SIZE
                elif direction == 2:
                    self.carrying.y += self.game.GRID_SIZE

            # The anchor on the conveyor is on the left, 
            # so subtract a grid size if we're facing that way
            if self.facing_left:
                self.carrying.x = self.x - self.game.GRID_SIZE
            else:
                self.carrying.x = self.x + self.game.GRID_SIZE
                
    
    def calc_grid(self):
        grid_size = self.game.GRID_SIZE
        if self.facing_left:
            fudge = -grid_size * 0.9
        else:
            fudge = grid_size * 0.9
        return (int((self.x + fudge) / self.game.GRID_SIZE),
                int((self.y + grid_size * 0.5) / self.game.GRID_SIZE))
    
    def find_machine(self):
        """Return the most reasonable machine from the player's position,
        or None if there aren't any"""
        my_grid = self.calc_grid()
        checks = (0, -1) if self.facing_left else (0, 1)
        for i in checks:
            the_grid = (my_grid[0]+i, my_grid[1])
            machine = self.game.machines.get(the_grid, None)
            if machine:
                return (machine, the_grid)
        return (machine, the_grid)
    
    def find_space(self):
        """Return a reasonable blank space."""
        #my_grid = self.calc_grid()
        my_grid = self.game.convert_to_grid(
                    self.carrying.pos[0],
                    self.carrying.pos[1] + self.game.GRID_SIZE * 0.5)
        checks = (0, -1) if self.facing_left else (0, 1)
        for i in checks:
            the_grid = (my_grid[0]+i, my_grid[1])
            machine = self.game.machines.get(the_grid, None)
            if not machine:
                return (machine, the_grid)
        return (machine, the_grid)
        
    def handle_button_down(self, button):
        print("Player {} pushed button {}".format(self, button))
        
        if button == joybutton.ZERO:
            # pick up/put down the thing
            if self.carrying:
                # prepare to put down: display a highlight where it'll go,
                # and put it down when the button is released
                self.putting_down = True
            else:
                # try to pick up
                machine, my_grid = self.find_machine()
                if machine:
                    print("Picking up", machine)
                    machine.carried = True
                    self.carrying = machine
                    del self.game.machines[my_grid]     # dangerous! 
                else:
                    # nope, there's nothing there
                    pass
    
    def handle_button_up(self, button):
        if button == joybutton.ZERO and self.carrying and self.putting_down:
            machine, my_grid = self.find_space()
            if machine:
                # nope, there's something there
                pass
            else:
                # Check which direction the player / player's joystick is facing,
                # and make the conveyor face that way.
                
                my_machine = self.carrying
                self.game.machines[my_grid] = my_machine
                my_machine.grid_x = my_grid[0]
                my_machine.grid_y = my_grid[1]
                my_machine.carried = False
                my_machine.direction = self.player_facing()
                print("Putting down", my_machine, "at", my_grid, "facing", my_machine.direction)
                self.carrying = False
                self.putting_down = False
    
    def player_facing(self):
        if (self.last_x, self.last_y) == (0, 0):
            if self.facing_left:
                return 3
            else:
                return 1
        if abs(self.last_x) > abs(self.last_y):
            # pointing mostly left/right
            if self.last_x < 0:
                return 3
            else:
                return 1
        else:
            # pointing mostly up/down
            if self.last_y < 0:
                return 0
            else:
                return 2
    
    def handle_axis(self, axis, value):
        print("Player {} moved axis {}: {}".format(self, axis, value))
        if axis == axis.X:
            self.speed[0] = value * 7
            self.last_x = value
        if axis == axis.Y:
            self.speed[1] = value * 7
            self.last_y = value