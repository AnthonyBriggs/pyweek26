import random
import sys

from pgzero.actor import Actor

from items import Item
import data


class OreChute(Actor):
    """Produces ore and raw materials of various types:
    copper, iron, organics, aluminium, glass.
    
    Ore is sent to the right, chutes can't be moved."""
    
    def __init__(self, game, grid_x, grid_y, ore_type, ore_time, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.name = "ore_chute"
        self.game = game
        image_name = 'machines/ore_chute'
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        self.ore_type = ore_type
        self.ore_time = ore_time
        self.next_ore = ore_time
        
        # icon
        thing = self.ore_type
        new_scale = data.items[thing]['scale'] * 0.5
        new_anchor = data.items[thing]['anchor']
        new_anchor = (new_anchor[0] * 0.5, new_anchor[1] * 0.5)
        self.icon = Item(thing, 
            anchor=new_anchor, scale=new_scale, from_direction=1 )
        self.icon.pos = (self.x + 85, self.y - 50)
        
    def __str__(self):
        return "<OreChute, position: {}, item:{}>".format(self.pos, self.ore_type)
    __repr__ = __str__
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (0,255,0))
        self.icon.draw()
        
    def update(self, dt):
        self.next_ore -= dt
        #print("Next ore in", self.next_ore)
        if self.next_ore <= 0:
            self.next_ore += self.ore_time
            self.send_ore()
            
    def send_ore(self):
        """Ore is sent to the right."""
        conveyor = self.game.map.get((self.grid_x + 1, self.grid_y), None)
        if conveyor:
            success = conveyor.receive_item_push(
                Item(self.ore_type,
                     anchor=data.items[self.ore_type]['anchor'],
                     scale=data.items[self.ore_type]['scale']),
                     from_direction=3 )
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
        self.name = "loading_dock"
        self.game = game
        image_name = 'machines/loading_dock'
        super().__init__(image_name, *args, **kwargs)
        self.x, self.y = game.convert_from_grid(grid_x, grid_y)
        self.item_type = item_type
        self.loading_time = loading_time
        self.next_load = loading_time
        self.number_loaded = 0
    
        # icon
        thing = self.item_type
        new_scale = data.items[thing]['scale'] * 0.5
        new_anchor = data.items[thing]['anchor']
        new_anchor = (new_anchor[0] * 0.5, new_anchor[1] * 0.5)
        self.icon = Item(thing, 
            anchor=new_anchor, scale=new_scale, from_direction=1 )
        self.icon.pos = (self.x + 25, self.y - 45)
        
    def __str__(self):
        return "<Loading Dock, position: {}, item_type: {}>".format(self.pos, self.item_type)
    __repr__ = __str__
    
    def draw(self):
        super().draw()
        self.game.point(self.pos, (255,255,0))
        self.icon.draw()
        self.game.text(str(self.number_loaded), (self.x + 5, self.y - 60))
        
    def update(self, dt):
        self.next_load -= dt
        #print("Next load in", self.next_load)
        if self.next_load <= 0:
            self.next_load = 0

    def receive_item_push(self, item, from_direction):
        """Receive an item from another machine, or return False."""
        #print(item.name, item, self.next_load)
        if item.name == self.item_type and self.next_load <= 0:
            self.number_loaded += 1
            self.next_load = self.loading_time
            self.game.products_required[self.item_type] -= 1
            print("{} loaded a {} - {} more to go".format(
                        self, item.name, self.game.products_required[item.name]))
            return True
        else:
            return False


class MachinePart(Actor):
    """A visible part of a MultiMachine. Will consist of a box + some parts,
    the parts will animate somehow when the machine is working."""
    
    # based on bottom left? pos + scale
    part_positions = {
        'topleft': ((10,25), 0.4),
        'topright': ((33,25), 0.4),
        'bottomleft': ((10,0), 0.4),
        'bottomright': ((33,0), 0.4),
        'verytop': ((17, 70), 0.5),
        'verytopwide': ((0, 70), 1.0),
        'hazard': ((0,35), 1.0),
    }
    
    def __init__(self, game, grid_x, grid_y, number, code, parts={}, *args, **kwargs):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.game = game
        self.number = number
        self.code = code
        self.name = 'machine_{}{}'.format(self.number, self.code)
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
        self.icon = None
        
        # Used for timing and animation progress
        self.manuf_time = 0
        self.current_manuf = 0

        # init subparts
        # eg. Red light top left, computer bottom right, saw_blade left?
        #       {'topleft': <red_light part>, ...}
        self._sub_parts = {}        
        for position, part_name in parts.items():
            pos, scale = self.part_positions[position]
            #print("Adding part", part_name, "at", pos, "scale:", scale)
            self._sub_parts[position] = MachineSubPart(self.game, part_name, pos, scale)
    
    def __str__(self):
        return "<Machine Part {}{}, position: ({}, {}), item: {}, item_types: {} -> {}>".format(
                    self.number, self.code, self.grid_x, self.grid_y, 
                    self.item, self.item_input or self.item_output,
                    self.input_direction or self.output_direction)
    __repr__ = __str__
    
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
            conveyor = self.game.map.get(target_grid, None)
            if conveyor and hasattr(conveyor, 'receive_item_push'):
                from_direction = [2, 3, 0, 1][self.output_direction]   # 0123 -> 2301
                print("Attempting to push", self.direction, "from", self, "to", conveyor)
                success = conveyor.receive_item_push(self.item, from_direction)
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
        print("Checking machine", str(self.number)+self.code, "for matches.")
        potential = [(k, v) for k, v in data.multimachines.items()
                        if str(self.code) in v['machines']]
        print(len(potential), "matches found")
        print([(k, v['machines']) for k, v in potential])
        
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
                #print("  ", layout['input'])
                for direction, item_type in layout['input']:
                    index, dir_ = direction  # 1L
                    index = int(index)
                    machine = machines[index]
                    if machine is not None:
                        machine.input_direction = dir_lookup.index(dir_)
                        machine.item_input = item_type
                        print("  added input to {}{}: {} {}".format(
                            machine.number, machine.code, 
                            machine.input_direction, machine.item_input))
                
                # only one output
                # TODO: Needs updating to multiple outputs?
                direction, item_type = layout['output']
                #print("  ", layout['output'])
                index, dir_ = direction  # 1L
                index = int(index)
                machine = machines[index]
                if machine is not None:
                    machine.output_direction = dir_lookup.index(dir_)
                    machine.item_output = item_type
                    print("  added output to {}{}: {} {}".format(
                        machine.number, machine.code, 
                        machine.output_direction, machine.item_output))
                
                # Add input and output chutes as visual cues
                for machine in machines:
                    if machine is None:
                        continue
                    #print(machine)
                    if machine.input_direction is not None:
                        dir_ = machine.input_direction
                    else:
                        dir_ = machine.output_direction
                    if dir_ is None:
                        continue
                    # These rotation values are a chute-specific hack.
                    # TODO: maybe sticking the anchor in the center would work better?
                    if dir_ == 0:
                        pos = (0, 70)
                        rotate = 0
                    if dir_ == 1:
                        pos = (140, 0)
                        rotate = 90
                    if dir_ == 2:
                        pos = (70, 0)
                        rotate = 180
                    if dir_ == 3:
                        pos = (-70, 70)
                        rotate = 270
                    #print(dir_, pos, rotate)
                    machine._sub_parts['io'] = MachineSubPart(self.game, 'io', pos, 1.0, anchor=(0,70))
                    machine._sub_parts['io'].angle = rotate
                    #print(machine._sub_parts)
                
                    # also add icon of input / output items
                    icon_offsets = [(35, 80), (90, 25), (35, -30), (-20, 25)]
                    thing = machine.item_input or machine.item_output
                    new_scale = data.items[thing]['scale'] * 0.5
                    new_anchor = data.items[thing]['anchor']
                    new_anchor = (new_anchor[0] * 0.5, new_anchor[1] * 0.5)
                    machine._sub_parts['icon'] = Item(thing,
                         anchor=new_anchor,scale=new_scale, from_direction=1 )
                    machine._sub_parts['icon'].position = icon_offsets[dir_]
                    
                return
    
    def check_layout(self, machine_type, layout):
        print("Checking for machine type '{}' ('{}')".format(machine_type, layout['layout']))
        coord = layout['layout'].index(self.code)
        x = coord % 3
        y = coord // 3
        #print(coord, x, y)
        top_left = (self.grid_x - x, self.grid_y - y)
        machines = [None, None, None, None, None, None]
        
        #debug - very useful, shows pattern from submachine's PoV
        if 1:
            for y in (0, 1):
                output = ""
                for x in (0, 1, 2):
                    coords = (top_left[0]+x, top_left[1]+y)
                    machine = self.game.map.get(coords, None)
                    if machine:
                        output += getattr(machine, 'code', '-')
                    else:
                        output += '.'
                print(output)
            print()
        
        for y in (0, 1):
            for x in (0, 1, 2):
                coords = (top_left[0]+x, top_left[1]+y)
                machine = self.game.map.get(coords, None)
                that_machine = layout['layout'][x+y*3]
                print("Checking {} ({}) vs. {} {}".format(that_machine, x+y*3, machine, coords))
                if that_machine == ' ' and machine is None:
                    # blanks match up
                    #print(".")
                    continue
                if that_machine == ' ' and getattr(machine, 'code', False):
                    # machine where there should be a space?
                    # TODO: False might cause trouble / be counterintuitive
                    # May also match multiple machines at once + flip/flop :D
                    #print(2, ":", getattr(machine, 'code', False))
                    return False
                if (that_machine != ' ' and 
                    getattr(machine, 'code', '.') != that_machine):
                    # Not the right machine type
                    #print(3, ":", getattr(machine, 'code', '.'), that_machine)
                    return False
                
                #print(4, ":", getattr(machine, 'code', '.'), that_machine)

                if getattr(machine, 'code', '.') in data.machines.keys():
                    machines[x+y*3] = machine
                #print("ok")
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
                    self.name, self.pos, self.scale)
    __repr__ = __str__
    
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
    __repr__ = __str__
    
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
        #print(self)
        self.update_input_outputs()
        
    def update_input_outputs(self):
        """check production - do we have all our inputs?"""
        self.input_machines = [m for m in self.machines if m.item_input]
        self.output_machines = [m for m in self.machines if m.item_output]
        empty_inputs = [m for m in self.input_machines if m.item is None]
        full_outputs = [m for m in self.output_machines if m.item]
        if empty_inputs:
            # don't start production without all the parts
            self.time = self.production_time
            return
        if full_outputs:
            # don't start production without room to put the product
            self.time = self.production_time
            return
        if self.time < 0:
            print("MM", self.name, "is producing...")
            print("  input:", [m.item for m in self.input_machines])
            #print("  output:", [m.item for m in self.output_machines])
            #print("0>", self.machines)
            #print("A>", self.input_machines, self.output_machines)
            #print ("B>", empty_inputs, full_outputs, self.time)
            
            # can make a thing!
            for m in self.input_machines:
                m.item = None
            for m in self.output_machines:
                m.item = Item(m.item_output,
                              anchor=data.items[m.item_output]['anchor'],
                              scale=data.items[m.item_output]['scale'])
                # the output machine part handles pushing
            print("  output:", [m.item for m in self.output_machines])

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