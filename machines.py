import random
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
        return "<Conveyor, position: {}, item:{}/{}, direction: {}>".format(
                    self.pos, self.item, self.item_pos, self.direction)
    
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
            self.item.pos = (self.x + 32, 
                             self.y - self.game.GRID_SIZE + self.item_pos + 12)
        if self.direction == 3:
            # right to left
            self.item.pos = (self.x + self.game.GRID_SIZE - self.item_pos, 
                             self.y - 28)

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
                #print("Ore Chute backed up!")
                pass
        else:
            # push it onto the floor? For now, do nothing
            pass


class LoadingDock(Actor):
    """Accepts packaged goods for delivery to customers."""
    
    def __init__(self, game, grid_x, grid_y, item_type, loading_time, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y

        self.game = game
        image_name = 'machines/loading_dock'
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        self.item_type = item_type
        self.loading_time = loading_time
        self.next_load = loading_time
        self.number_loaded = 0
    
    def __str__(self):
        return "<Loading Dock, position: {}, item_type: {}>".format(self.pos, self.item_type)
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (255,255,0))

    def update(self, dt):
        self.next_load -= dt
        #print("Next load in", self.next_load)
        if self.next_load <= 0:
            self.next_load = 0

    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        #print(item.name, item, self.next_load)
        if item.name == self.item_type and self.next_load <= 0:
            # TODO: increment score or quota
            self.number_loaded += 1
            self.next_load = self.loading_time
            return True
        else:
            return False
            
class StampyThing(Actor):
    """Stamps ore into circuit boards."""
    
    def __init__(self, game, grid_x, grid_y, item_input, item_output, stamping_time, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.game = game
        image_name = 'machines/machine_1'
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        self.item = None
        self.item_input = item_input
        self.item_output = item_output
        self.stamping_time = stamping_time
        self.next_stamp = stamping_time
        
    def __str__(self):
        return "<Stampy Thing, position: {}, item_types: {} -> {}>".format(
                    self.pos, self.item_input, self.item_output)
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (255,255,0))

    def update(self, dt):
        self.next_stamp -= dt
        #print("Next stamp in", self.next_stamp)
        if self.next_stamp <= 0:
            self.next_stamp = 0
            if self.item:
                if self.item.name == self.item_input:
                    # Stamp it!
                    self.item = Item(self.item_output, scale=0.5, anchor=(35, 40))
                # push it out the bottom side
                conveyor = self.game.machines.get((self.grid_x, self.grid_y+1), None)
                if conveyor:
                    success = conveyor.receive_item_push( self.item, from_direction=0 )
                    if success:
                        self.item = None
    
    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        #print(item.name, item, self.next_stamp)
        if self.item:
            return False
        if item.name != self.item_input:
            return False
        if from_direction != 0:
            return False
        
        # ok, we'll accept an item, but won't necessarily stamp it yet
        self.item = item
        return True
        
class MachinePart(Actor):
    """A visible part of a MultiMachine. Will consist of a box + some parts,
    the parts will animate somehow when the machine is working."""
    
    # based on bottom left? pos + scale
    part_positions = {
        'topleft': ((10,25), 0.4),
        'topright': ((27,23), 0.4),
        'bottomleft': ((10,10), 0.4),
        'bottomright': ((25,10), 0.4),
        'verytop': ((17, 70), 0.5),
        'verytopwide': ((0, 70), 1.0),
        'hazard': ((0,0), 1.0),
    }
    
    def __init__(self, game, grid_x, grid_y, number, parts={}, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.game = game
        self.number = number
        image_name = 'machines/machine_{}'.format(self.number)
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        
        # These will be set by the MultiMachine
        self.item = None
        self.item_input = None
        self.input_direction = None
        self.item_output = None
        self.output_direction = None
        self.multimachine = None
        
        # Used for timing and animation progress
        self.manuf_time = 0
        self.current_manuf = 0

        # init subparts here??
        # eg. Red light top left, computer bottom right, saw_blade left?
        #       {'topleft': <red_light part>, ...}
        self._sub_parts = {}        
        for position, part_name in parts.items():
            pos, scale = self.part_positions[position]
            print("Adding part", part_name, "at", pos, "scale:", scale)
            self._sub_parts[position] = MachineSubPart(self.game, part_name, pos, scale)
    
    def __str__(self):
        return "<Machine Part {}, position: {}, item: {}, item_types: {} -> {}>".format(
                    self.number, self.pos, self.item, self.item_input, self.item_output)
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (255,0,255))
                
    def update(self, dt):
        for part in self._sub_parts.values():
            # update position based on location (eg. topleft)
            part.x = self.x + part.position[0]
            part.y = self.y - part.position[1]
        
        if self.item and self.item_output:
            # try and push out
            target_grid = self.get_target_grid()
            print(self, "pushing to", target_grid)
            conveyor = self.game.machines.get(target_grid, None)
            if conveyor and hasattr(conveyor, 'receive_item_push'):
                #from_direction = [2, 3, 0, 1][self.direction]   # 0123 -> 2301
                print("Attempting to push", self.direction, "from", self, "to", conveyor)
                success = conveyor.receive_item_push(self.item, self.direction)
                if success:
                    self.item = None
                    self.item_pos = 0
                else:
                    #stalled
                    pass
    
    def get_target_grid(self):
        """Where is this conveyor pushing to?"""
        if self.output_direction == 0:
            return (self.grid_x, self.grid_y - 1)
        if self.output_direction == 1:
            return (self.grid_x + 1, self.grid_y)
        if self.output_direction == 2:
            return (self.grid_x, self.grid_y + 1)
        if self.output_direction == 3:
            return (self.grid_x - 1, self.grid_y)
    
    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        if self.item:
            return False
        if item.name != self.item_input:
            return False
        if from_direction != self.input_direction:
            return False
        
        # ok, we'll accept an item. Processing is handled by the parent MultiMachine.
        self.item = item
        return True
        
    def on_put_down(self):
        """Check to see if there's a complete MultiMachine."""
        print("Checking machine", self.number, "for matches.")
        potential = [(k,v) for k, v in self.game.multimachine_configs.items()
                        if str(self.number) in v['machines']]
        # find ourselves in the layout
        for machine_type, layout in potential:
            machines = self.check_layout(machine_type, layout)
            if machines:
                print("Multimachine '{}' detected!".format(machine_type))
                mm = MultiMachine(self.game, machine_type, machines, layout['time'])
                self.game.multimachines.append(mm)
                print("Multimachine created! ({} machines)".format(len(mm.machines)))
                
                # add inputs and outputs
                # Input/output is [1-6][LRTB] for blocks 1-6 and left/right/top/bottom
                dir_lookup = "TRBL"
                print("  ", layout['input'])
                for direction, item_type in layout['input']:
                    index, dir_ = direction  # 1L
                    index = int(index)
                    machine = machines[index]
                    if machine is not None:
                        machine.input_direction = dir_lookup.index(dir_)
                        machine.item_input = item_type
                        print("  added input", machine.input_direction, machine.item_input)
                
                # only one output
                direction, item_type = layout['output']
                print("  ", layout['output'])
                index, dir_ = direction  # 1L
                index = int(index)
                machine = machines[index]
                if machine is not None:
                    machine.output_direction = dir_lookup.index(dir_)
                    machine.item_output = item_type
                    print("  added output", machine.input_direction, machine.item_output)
                
                # Add input and output chutes as visual cues
                for machine in machines:
                    if machine is None:
                        continue
                    print(machine)
                    dir_ = machine.input_direction or machine.output_direction
                    if dir_ is None:
                        continue
                    if dir_ == 0:
                        pos = (0, 70)
                        rotate = 0
                    if dir_ == 1:
                        pos = (140, 0)
                        rotate = 90
                    if dir_ == 2:
                        pos = (0, -70)
                        rotate = 180
                    if dir_ == 3:
                        pos = (-70, 70)
                        rotate = 270
                    print(dir_, pos, rotate)
                    machine._sub_parts['io'] = MachineSubPart(self.game, 'io', pos, 1.0, anchor=(0,70))
                    machine._sub_parts['io'].angle = rotate
                    print(machine._sub_parts)
                return
    
    def check_layout(self, machine_type, layout):
        print("Checking machine type", machine_type, layout['layout'])
        coord = layout['layout'].index(str(self.number))
        x = coord % 3
        y = coord // 3
        top_left = (self.grid_x - x, self.grid_y - y)
        machines = [None, None, None, None, None, None]
        
        for y in (0, 1):
            for x in (0, 1, 2):
                machine = self.game.machines.get((top_left[0]+x, top_left[1]+y), None)
                print("Checking", x+y*3, 'vs.', machine)
                that_machine = layout['layout'][x+y*3]
                if that_machine == ' ' and machine is None:
                    # blanks match up
                    print("ok")
                    continue
                if that_machine == ' ' and getattr(machine, 'number', False):
                    # machine where there should be a space?
                    # False might cause trouble / be counterintuitive
                    # May also match multiple machines at once + flip/flop :D
                    return False
                if (that_machine != ' ' and 
                    getattr(machine, 'number', '-1') != int(that_machine)):
                    # Not the right machine type
                    return False
                
                if getattr(machine, 'number', -1) > 0:
                    machines[x+y*3] = machine
                print("ok")
        return machines
        
        
class MachineSubPart(Actor):
    """Part of a machine, like a light or a screen. 
    Mainly used to identify bits of a larger one."""
    
    def __init__(self, game, name, position, scale, *args, **kwargs):
        self.game = game
        self.name = name
        self.position = position  # (x,y) relative to the main machine
        image_name = 'machines/machine_part_{}'.format(self.name)
        super().__init__(image_name, *args, **kwargs)
        self.scale = scale
        if 'anchor' not in kwargs:
            self.anchor = (0, 35)
        
    def __str__(self):
        return "<Machine Sub Part {}, position: {}, scale: {}>".format(
                    self.number, self.pos, self.scale)

    def draw(self):
        super().draw()
        self.game.point(self.pos, (255,255,0))

    def update(self, dt):
        pass


class MultiMachine(object):
    """A meta-machine, consisting of multiple parts. When the parts are 
    put together in the right way, it gives a visible indication of
    activation and starts producing stuff.
    
    Needs to store some configuration like >121> or >13
                                                     12> """
    def __init__(self, game, name, machines, production_time):
        self.game = game
        self.name = name
        self.production_time = production_time
        self.time = production_time
        self.machines = [m for m in machines if m is not None]
        for machine in self.machines:
            machine.multimachine = self
        self.update_input_outputs()
        self.next_wiggle = 0.1

    def __str__(self):
        return "<MultiMachine {}, machines: {}, next production: {}/{}>".format(
                    self.name, len(self.machines), self.time, self.production_time)

    def update(self, dt):
        self.next_wiggle -= dt
        if self.next_wiggle < 0:
            # wiggle the machines around so it looks active
            wiggle = (-2, -1, -1, 0, 0, 0, 1, 1, 2)
            for machine in self.machines:
                machine.x, machine.y = self.game.convert_from_grid(machine.grid_x, machine.grid_y)
                machine.x += random.choice(wiggle)
                machine.y += random.choice(wiggle)
                machine.update(dt)
            self.next_wiggle = 0.1
        self.time -= dt
        print(self)
        self.update_input_outputs()
        
    def update_input_outputs(self):
        """check production - do we have all our inputs?"""
        self.input_machines = [m for m in self.machines if m.input_direction]
        self.output_machines = [m for m in self.machines if m.output_direction]
        empty_inputs = [m for m in self.input_machines if not m.item]
        full_outputs = [m for m in self.output_machines if m.item]
        if empty_inputs:
            # don't start production without all the parts
            self.time = self.production_time
        if not empty_inputs and not full_outputs and self.time < 0:
            # can make a thing!
            for m in self.input_machines:
                m.item = None
            for m in self.output_machines:
                # TODO: Items should know what their scale + anchors are
                m.item = Item(m.item_output, scale=0.5, anchor=(35, 40))
                # the output machine part handles pushing
            self.time = self.production_time
    
    def switch_off(self):
        """Restore our parts back to their original independent machines."""
        for machine in self.machines:
            machine.x, machine.y = self.game.convert_from_grid(machine.grid_x, machine.grid_y)
            machine.input_direction = None
            machine.item_input = None
            machine.output_direction = None
            machine.item_output = None
            #machine.item = None    # probably too harsh :)
            machine.multimachine = None
            
            # remove input/output chutes
            if 'io' in machine._sub_parts:
                del machine._sub_parts['io']
            
        self.machines = []
    
    def produce(self):
        """If our components have items, and we can push our output somewhere, 
        then we can produce our output."""
        