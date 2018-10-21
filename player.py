import sys

from pgzero.actor import Actor

class Player(Actor):
    
    def __init__(self, number, screen, *args, **kwargs):
        self.number = number
        self.screen = screen
        image_name = 'players/p{}/p{}_stand'.format(self.number, self.number)
        super().__init__(image_name, *args, **kwargs)
        self.speed = [0, 0]
        self.facing_left = False
        self.move_distance = 0
        self.spawn()
    
    def __str__(self):
        return "<Player {}, position: {}>".format(self.number, self.pos)
    
    def set_image(self, image_name):
        self.image = 'players/p{}/p{}_{}'.format(self.number, self.number, image_name)
        
    def spawn(self):
        # TODO: find a blank spot on the screen to spawn into? 
        #       Or just have a spawn spot in the top left (clock on?)
        self.pos = 100, 100
    
    def draw(self):
        if self.speed == [0,0]:
            self.set_image('stand')
        else:
            step = int( (self.move_distance / 12 ) % 11 + 1 )
            self.set_image('walk{:0>2d}'.format(step))
        super().draw()
        
    def update(self):
        #print ("updating player", self.number)
        self.x += self.speed[0]
        self.y += self.speed[1]
        if self.speed == [0,0]:
            self.move_distance = 0     # stopped; reset walk distance
        else:
            self.move_distance += abs(self.speed[0]) + abs(self.speed[1])
        
        if self.speed[0] < 0:
            self.facing_left = True
        elif self.speed[0] > 0:
            self.facing_left = False
        self.flip = self.facing_left
        
        if self.right > self.screen.width:
            self.right = self.screen.width
        if self.left < 0:
            self.left = 0
        if self.top < 0:
            self.top = 0
        if self.bottom > self.screen.height:
            self.bottom = self.screen.height
            
    def handle_button(self, button):
        print("Player {} pushed button {}".format(self, button))
        
    def handle_axis(self, axis, value):
        print("Player {} moved axis {}: {}".format(self, axis, value))
        if axis == axis.X:
            self.speed[0] = value * 10
        if axis == axis.Y:
            self.speed[1] = value * 10