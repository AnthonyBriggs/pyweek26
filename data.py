
""" - ingots (copper, iron, carbon?, aluminium, biological?, glass)
        -> plates, wires, cogs
        -> widgets (boxes? larger parts, anyway)
        -> TVs, chainsaws, toys, robots"""

# image, name, anchor, size?, components (ie. build into)?
# name can be the image name
# size should be down to 35-40px square?
# TODO: calculate anchor + scale
# anchor worked out from bottom-most point in paint.
# scale is target size / image size
# anchor is from top left, I think :)

# anchor for a 70x70 square item
item_70 = (35*40/70, 70*40/70)
items = {
    'copper_ingot': {'anchor': (34, 53), 'scale': 1.0, },
    'silver_ingot': {'anchor': (34, 53), 'scale': 1.0, },
    'gold_ingot': {'anchor': (34, 53), 'scale': 1.0, },
    'glass': {'anchor': item_70, 'scale': 40/70, },
    'organic': {'anchor': item_70, 'scale': 40/70, },
    'brown_organic': {'anchor': item_70, 'scale': 40/70, },
    'metal': {'anchor': item_70, 'scale': 40/70, },
    
    # intermediate
    'circuit_board': {'anchor': (50*40/112, 77*40/112), 'scale': 40/112, },
    'paper': {'anchor': (75*40/145, 147*40/145), 'scale': 40/145, },
    'motherboard': {'anchor': (67*40/134, 122*40/134), 'scale': 40/134, },
    'graphics_card': {'anchor': (82*40/163, 81*40/163), 'scale': 40/163, },
    
    # need:
    'lens': {'anchor': item_70, 'scale': 40/70, },
    'bowl': {'anchor': (43*40/86, 86*40/86), 'scale': 40/86, },
    'motor': {'anchor': item_70, 'scale': 40/70, },
    'case': {'anchor': (36*65/40, 65*65/40), 'scale': 65/40, },
    
    # final
    'book': {'anchor': (55*40/124, 124*40/124), 'scale': 40/124, },
    'coffee': {'anchor': (57, 111), 'scale': 40/111, },
    'axe': {'anchor': (42*40/128, 128*40/128), 'scale': 40/128, },
    'camera': {'anchor': (56*40/112, 80*40/112), 'scale': 40/112, },
    'computer': {'anchor': (), 'scale': 1.0, },
    'tv': {'anchor': (45*40/128, 128*40/128), 'scale': 40/128, },
    'phone': {'anchor': (65*40/141, 68*40/141), 'scale': 40/141, },
    'blender': {'anchor': (58*40/108, 108*40/108), 'scale': 40/108, },
}

# parts of multimachines - just need to be individually identifiable
# sub parts are same size, so can use the same scale
machines = {
    'A': {'number': 1, 'parts': {'topleft': 'blue_window',}, },
    'B': {'number': 2, 'parts': {'verytop': 'red_light',}, },
    'C': {'number': 3, 'parts': {'topright': 'screen',}, },
    'D': {'number': 4, 'parts': {'bottomright': 'green_sign',}, },
    'E': {'number': 2, 'parts': {'topleft': 'red_window',}, },
    'F': {'number': 3, 'parts': {'bottomleft': 'red_window', 'topright': 'blue_window',}, },
    'G': {'number': 4, 'parts': {'hazard': 'hazard_1',}, },
    'H': {'number': 5, 'parts': {'verytop': 'yellow_light' , 'topleft': 'screen', }, },
    'I': {'number': 2, 'parts': {'topleft': 'screen' , 'bottomright': 'green_sign', }, },
    'J': {'number': 1, 'parts': {'topleft': 'blue_window', 'bottomright': 'red_sign',}, },
    'K': {'number': 5, 'parts': {'verytop': 'saw_blade', 'bottomleft': 'red_sign',}, },
}

multimachines = {
    # intermediate
    'circuit_board': {
        'name': 'circuit_board',
        'machines': 'ABC',
        'layout': 'AB  C ',
        'input': [('0T', 'copper_ingot')],
        'output': ('4B', 'circuit_board'),
        'time': 7, },
    'paper': {
        'name': 'paper',
        'machines': 'BD',
        'layout': 'BD    ',
        'input': [('0L', 'brown_organic')],
        'output': ('1B', 'paper'),
        'time': 4, },
    'motherboard': {
        'name': 'motherboard',
        'machines': 'DFGI',
        'layout': 'D  FGI',
        'input': [('0L', 'circuit_board'), ('3B', 'gold_ingot')],
        'output': ('5R', 'motherboard'),
        'time': 10, },
    'graphics_card': {
        'name': 'graphics_card',
        'machines': 'BCD',
        'layout': 'CB D  ',
        'input': [('0L', 'circuit_board'), ('1T', 'copper_ingot')],
        'output': ('3R', 'motherboard'),
        'time': 9, },
    'lens': {
        'name': 'lens',
        'machines': 'HIJ',
        'layout': 'H  IJ ',
        'input': [('0T', 'glass'), ('3L', 'glass')],
        'output': ('4R', 'lens'),
        'time': 12, },
    'case': {
        'name': 'case',
        'machines': 'AGJ',
        'layout': 'AG  J ',
        'input': [('0L', 'metal'), ('3L', 'metal')],
        'output': ('4R', 'case'),
        'time': 5, },
    'bowl': {
        'name': 'bowl',
        'machines': 'DE',
        'layout': 'DE    ',
        'input': [('0L', 'glass'), ],
        'output': ('1R', 'bowl'),
        'time': 5, },
    'motor': {
        'name': 'motor',
        'machines': 'EFI',
        'layout': 'EF I  ',
        'input': [('0T', 'copper_ingot'), ('3L', 'metal')],
        'output': ('1T', 'motherboard'),
        'time': 7, },
    
    # final
    'book': {
        'name': 'book',
        'machines': 'ABDE',
        'layout': 'BAD E ',
        'input': [('0T', 'paper'), ('1T', 'paper'), ('2T', 'brown_organic')],
        'output': ('4R', 'book'),
        'time': 8, },
    'coffee': {
        'name': 'coffee',
        'machines': 'ACEG',
        'layout': 'A  CEG',
        'input': [('0L', 'organic'), ('3B', 'bowl'), ('4B', 'metal')],
        'output': ('5B', 'coffee'),
        'time': 7, },
    'axe': {
        'name': 'axe',
        'machines': 'BDF',
        'layout': 'DBF   ',
        'input': [('0L', 'metal'), ('1T', 'brown_organic')],
        'output': ('2B', 'axe'),
        'time': 8, },
    'blender': {
        'name': 'blender',
        'machines': 'FGJI',
        'layout': 'GFJ  I',
        'input': [('0T', 'motor'), ('1T', 'bowl'), ('2R', 'copper_ingot')],
        'output': ('5R', 'blender'),
        'time': 7, },
    'camera': {
        'name': 'camera',
        'machines': 'DEFIK',
        'layout': 'DIF KE',
        'input': [('0T', 'lens'), ('1T', 'case'), ('2T', 'circuit_board')],
        'output': ('4L', 'camera'),
        'time': 12, },
    'phone': {
        'name': 'phone',
        'machines': 'JHFAB',
        'layout': 'JHFA B',
        'input': [('3L', 'glass'), ('0T', 'circuit_board'), ('2T', 'gold_ingot')],
        'output': ('5R', 'phone'),
        'time': 10, },
    'tv': {
        'name': 'tv',
        'machines': 'KIGE',
        'layout': '  KIGE',
        'input': [('2T', 'glass'), ('3L', 'case'), ('4B', 'circuit_board')],
        'output': ('5T', 'tv'),
        'time': 12, },
    'computer': {
        'name': 'computer',
        'machines': 'FGHIJK',
        'layout': 'FHGKJI',
        'input': [('0L', 'case'), ('1T', 'motherboard'), ('2R', 'graphics_card')],
        'output': ('3B', 'computer'),
        'time': 15, },
}

def sanity_check_machines():
    """Development tool to make sure the machine data is correct."""
    for mm in multimachines.values():
        assert len(mm['layout']) == 6

    # multimachines can't have the same subsequences, or a collision will occur
    # (eg. BD and BDA, BDA and 'BDA F '
    chars = machines.keys()
    # these are layout indexes
    neighbors = [(0, 1), (1, 2), (3, 4), (4, 5), # horizontal
                 (0, 3), (1, 4), (4, 5)]
    combo_lookup = {}
    for mm in multimachines.values():
        for x, y in neighbors:
            combo = mm['layout'][x] + mm['layout'][y]
            if ' ' in combo:
                continue
            if (combo in combo_lookup and 
                mm['name'] != combo_lookup[combo]['name']):
                print("Machines {} and {} have the same {} combo ({})".format(
                    mm['name'], combo_lookup[combo]['name'], combo, (x,y)))
            else:
                combo_lookup[combo] = mm

#sanity_check_machines()
    
# machines, number of conveyors, time limit, products needed
# for now, assume we're placing elements at random.
level_order = [
    'Training day',
    'Probation',
    'Chop chop!',
    'eat, work, sleep, repeat',
    'Cake day',
    "Don't forget to call your mother!",
    'Watch me get a promotion',
    'Employee of the month', ]

levels = {
    # circuit?
    'Training day': {
        'conveyors': 18,
        'inputs': ['copper_ingot'],
        'machines': "ABC",
        'products': [(10, 'circuit_board'),],
        'help': ['circuit_board'],
    },
    
    # book
    'Probation': {
        'conveyors': 22,
        'inputs': ['brown_organic'],    # no paper needed
        'machines': "ABCDEBDF",
        'products': [(12, 'book'),],
        'help': ['circuit_board', 'book'],
    },

    # axe
    'Chop chop!': {
        'conveyors': 18,
        'inputs': ['metal', 'brown_organic'],
        'machines': "ABDEF",
        'products': [(8, 'axe'),],
        'help': ['circuit_board', 'book', 'axe'],
    },
    
    # coffee
    'eat, work, sleep, repeat': {
        'conveyors': 21,
        'inputs': ['organic', 'glass', 'metal'],
        'machines': "ACDEEGF",
        'products': [(10, 'coffee'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee'],
    },
    
    # blender
    'Cake day': {
        'conveyors': 22,
        'inputs': ['glass', 'copper_ingot', 'metal'],
        'machines': "ABDEFGJI",
        'products': [(15, 'blender'), (15, 'bowl'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                 'motor', 'blender'],
    },
    
    # phone
    "Don't forget to call your mother!": {
        'conveyors': 25,
        'inputs': ['glass', 'copper_ingot', 'metal', 'gold_ingot'],
        'machines': "JHFAB ABCD I",
        'products': [(10, 'phone'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                'motor', 'blender', 'case', 'tv', 'phone'],
    },
    
    # tv
    'Watch me get a promotion': {
        'conveyors': 27,
        'inputs': ['glass', 'copper_ingot', 'metal'],
        'machines': "KIGE AGJ ABCD",
        'products': [(10, 'tv'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                'motor', 'blender', 'case', 'tv'],
    },
    
    # computer
    'Employee of the month': {
        'conveyors': 30,
        'inputs': ['metal', 'copper_ingot', 'gold_ingot', 'copper_ingot'],
        'machines': "FGHIJK AGJ DFG BC", # missing second D, muahaha
        'products': [(5, 'computer'), (10, 'graphics card'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                 'motor', 'blender', 'case', 'tv', 'motherboard', 'computer'],
    },
}