from pgzero.actor import Actor


class Player(Actor):
    def __init__(self, game, number, *args, **kwargs):
        self.number = number
        self.game = game
        image_name = 'players/p{}/p{}_stand'.format(self.number, self.number)
        super().__init__(image_name, *args, **kwargs)
        self.speed = [0, 0]
        self.facing_left = False
        self.last_x = self.last_y = 0
        self.move_distance = 0
        self.carrying = False
        self.putting_down = False
        self.spawn()
        self.highlight = Actor('players/highlight', anchor=(0, 70))
        self.direction = Actor('players/direction_1', anchor=(0, 70))
        
    def __str__(self):
        return "<Player {}, position: {}>".format(self.number, self.pos)
    
    def set_image(self, image_name):
        self.image = 'players/p{}/p{}_{}'.format(self.number, self.number, image_name)
    
    def spawn(self):
        # TODO: find a blank spot on the screen to spawn into? 
        #       Or just have a spawn spot in the top left (clock on?)
        self.pos = 10,10
    
    def draw(self):
        if self.speed == [0,0]:
            self.set_image('stand')
        else:
            step = int( (self.move_distance / 12 ) % 11 + 1 )
            self.set_image('walk{:0>2d}'.format(step))
        super().draw()
        
        if self.carrying:
            self.carrying.draw()
            for part in getattr(self.carrying, '_sub_parts', {}).values():
                part.draw()
        
        #self.game.point(self.pos)
        #self.game.point((self.x, self.y))
    
    def draw_highlight(self):
        my_grid = self.pick_up_space()
        pos = self.game.convert_from_grid(*my_grid)
        machine = self.game.map.get(my_grid, None)
        if self.putting_down and not machine:
            # show a direction arrow
            
            # This fixes an utterly bizarre bug where left and right images
            # are swapped, despite looking fine in the folder.
            direction = self.player_facing()
            if direction == 1: direction = 3
            elif direction == 3: direction = 1
            
            self.direction.image = 'players/direction_{}'.format(direction)
            #print(self.direction.image, self.player_facing(), pos)
            self.direction.pos = pos
            self.direction.draw()
        elif self.carrying or machine:
            self.highlight.pos = pos
            self.highlight.draw()
        
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
        
        if not self.putting_down:
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
            self.carrying.update(dt)
            self.carrying.y = self.y + 30
            if self.putting_down:
                self.carrying.direction = self.player_facing()
                self.carrying.pos = self.game.convert_from_grid(*self.putting_down)
            else:
                # The anchor on the conveyor is on the left, 
                # so subtract a grid size if we're facing that way
                if self.facing_left:
                    self.carrying.x = self.x - self.game.GRID_SIZE * 1.5
                else:
                    self.carrying.x = self.x + self.game.GRID_SIZE * 0.5
                
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
        return 1
    
    def pick_up_space(self):
        """Which space are we currently able to pick up?"""
        me = self.game.convert_to_grid(self.x, self.y)
        if self.putting_down:
            # grid is fixed, only direction will change,
            # based on the joystick direction
            return self.putting_down
                    
        # Otherwise, just base it on grid squares to the left or right
        # For some reason, we need to add one to the y value? Not sure where this is coming from...
        if self.facing_left:
            return (me[0] - 1, me[1] + 1)
        else:
            return (me[0] + 1, me[1] + 1)
    
    def pick_up(self):
        if self.carrying:
            # prepare to put down: display a highlight where it'll go,
            # and put it down when the button is released
            self.putting_down = self.pick_up_space()
            return
            
        # try to pick up
        my_grid = self.pick_up_space()
        machine = self.game.map.get(my_grid, None)
        if machine is None:
            # nope, nothing there
            return
        elif (machine.name == 'ore_chute' or
            machine.name == 'loading_dock'):
            pass # no pick up
        elif machine and machine.name == 'training_manual_kiosk':
            print("Training Manual!")
            self.game.show_training_manual = True
        else:
            #print("Picking up", machine)
            machine.carried = True
            self.carrying = machine
            if getattr(machine, 'multimachine', None):
                # need to disable the multimachine
                mm = machine.multimachine
                mm.switch_off()
                self.game.multimachines.remove(mm)
                del mm
            del self.game.map[my_grid]   # dangerous! 
    
    def put_down(self):
        my_grid = self.pick_up_space()
        machine = self.game.map.get(my_grid, None)
        if machine:
            # nope, there's something there
            self.putting_down = False
            pass
        else:
            # Check which direction the player / player's joystick is facing,
            # and make the conveyor face that way.
            my_machine = self.carrying
            self.game.map[my_grid] = my_machine
            my_machine.grid_x = my_grid[0]
            my_machine.grid_y = my_grid[1]
            my_machine.x, my_machine.y = self.game.convert_from_grid(*my_grid)
            my_machine.carried = False
            my_machine.direction = self.player_facing()
            if hasattr(my_machine, 'on_put_down'):
                my_machine.on_put_down()
            #print("Putting down", my_machine, "at", my_grid, "facing", my_machine.direction)
            self.carrying = False
            self.putting_down = False
    
    def do_a_debug(self):
        # debug the conveyors
        my_grid = self.pick_up_space()
        machine = self.game.map.get(my_grid, None)
        if machine:
            print(machine)
        mm = getattr(machine, 'multimachine', None)
        if mm:
            print(mm)
            print("  Production:", mm.input_machines, mm.output_machines)
        print ("Multimachines in game: ", self.game.multimachines)
    
    
    def handle_button_down(self, button):
        #print("Player {} pushed button {}".format(self, button))
        if button == joybutton.ZERO:
            self.pick_up()
            
        if button == joybutton.TWO:
            self.do_a_debug()
            
    def handle_button_up(self, button):
        if button == joybutton.ZERO and self.carrying and self.putting_down:
            self.put_down()
    
    def handle_axis(self, axis, value):
        #print("Player {} moved axis {}: {}".format(self, axis, value))
        if axis == axis.X:
            self.speed[0] = value * 7
            self.last_x = value
        if axis == axis.Y:
            self.speed[1] = value * 7
            self.last_y = value
    
    
    def handle_key_down(self, key):
        if key in (keys.SPACE, keys.RSHIFT):
            # button zero
            self.pick_up()
        
        if key in (keys.RETURN, keys.LALT):
            self.do_a_debug()
        
        if key in (keys.W, keys.UP):
            self.speed[1] = -7
            self.last_y = -7
        
        if key in (keys.S, keys.DOWN):
            self.speed[1] = 7
            self.last_y = 7
            
        if key in (keys.A, keys.LEFT):
            self.speed[0] = -7
            self.last_x = -7
        
        if key in (keys.D, keys.RIGHT):
            self.speed[0] = 7
            self.last_x = 7

    def handle_key_up(self, key):
        if key in (keys.SPACE, keys.RSHIFT) and self.carrying and self.putting_down:
            # button zero
            self.put_down()
        
        if key in (keys.W, keys.UP):
            self.speed[1] = 0
            self.last_y = 0
        
        if key in (keys.S, keys.DOWN):
            self.speed[1] = 0
            self.last_y = 0
            
        if key in (keys.A, keys.LEFT):
            self.speed[0] = 0
            self.last_x = 0
        
        if key in (keys.D, keys.RIGHT):
            self.speed[0] = 0
            self.last_x = 0