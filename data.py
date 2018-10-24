
""" - ingots (copper, iron, carbon?, aluminium, biological?, glass)
        -> plates, wires, cogs
        -> widgets (boxes? larger parts, anyway)
        -> TVs, chainsaws, toys, robots"""

# image, name, anchor, size?, components (ie. build into)?
# name can be the image name
# size should be down to 35-40px square?
items = {
    'copper_ingot': {'anchor': (), scale: 1.0, },
    'silver_ingot': {'anchor': (), scale: 1.0, },
    'gold_ingot': {'anchor': (), scale: 1.0, },
    'glass': {'anchor': (), scale: 1.0, },
    'organic': {'anchor': (), scale: 1.0, },
    'brown_organic': {'anchor': (), scale: 1.0, },
    'metal': {'anchor': (), scale: 1.0, },
    
    # intermediate
    'circuit_board': {'anchor': (), scale: 1.0, },
    'paper': {'anchor': (), scale: 1.0, },
    'motherboard': {'anchor': (), scale: 1.0, },
    'graphics_card': {'anchor': (), scale: 1.0, },
    
    # need:
    'lens': {'anchor': (), scale: 1.0, },
    'bowl': {'anchor': (), scale: 1.0, },
    'motor': {'anchor': (), scale: 1.0, },
    'case': {'anchor': (), scale: 1.0, },
    
    # final
    'book': {'anchor': (), scale: 1.0, },
    'coffee': {'anchor': (), scale: 1.0, },
    'axe': {'anchor': (), scale: 1.0, },
    'camera': {'anchor': (), scale: 1.0, },
    'computer': {'anchor': (), scale: 1.0, },
    'tv': {'anchor': (), scale: 1.0, },
    'phone': {'anchor': (), scale: 1.0, },
    'blender': {'anchor': (), scale: 1.0, },
}

# parts of multimachines - just need to be individually identifiable
# sub parts are same size, so can use the same scale
machines = {
    'A': {'number': 1, 'parts': {'blue_window': 'topleft'}, },
    'B': {'number': 2, 'parts': {'red_light': 'verytop'}, },
    'C': {'number': 3, 'parts': {'screen': 'topright'}, },
    'D': {'number': 4, 'parts': {'green_sign': 'bottomright'}, },
    'E': {'number': 2, 'parts': {'red_window': 'topleft'}, },
    'F': {'number': 3, 'parts': {'red_window': 'topleft', 'blue_window': 'topright'}, },
    'G': {'number': 4, 'parts': {'hazard': 'hazard'}, },
    'H': {'number': 5, 'parts': {'yellow_light': 'verytop', 'screen': 'topleft', }, },
    'I': {'number': 2, 'parts': {'screen': 'topleft', 'green_sign': 'bottomright', }, },
    'J': {'number': 1, 'parts': {'blue_window': 'topleft', 'red_sign': 'bottomright'}, },
    'K': {'number': 5, 'parts': {'saw_blade': 'verytop', 'red_sign': 'bottomleft'}, },
    }

multimachines = {
    # intermediate
    'circuit_board': {'machines': 'ABC',
                      'layout': 'AB  C ',
                      'input': [('0L', 'copper_ingot')],
                      'output': ('4R', 'circuit_board'),
                      'time': 7, },
    'paper': {'machines': 'BD',
              'layout': 'BD    ',
              'input': [('0L', 'brown_organic')],
              'output': ('1B', 'paper'),
              'time': 4, },
    'motherboard': {'machines': 'DFG',
                      'layout': 'D  FGI',
                      'input': [('0L', 'circuit_board'), ('3B', 'gold_ingot')],
                      'output': ('5R', 'motherboard'),
                      'time': 10, },
    'graphics_card': {'machines': 'BDC',
                      'layout': 'BD C  ',
                      'input': [('0L', 'circuit_board'), ('1T', 'copper_ingot')],
                      'output': ('3R', 'motherboard'),
                      'time': 9, },
    'lens': {'machines': 'HIJ',
              'layout': 'H  IJ ',
              'input': [('0T', 'glass'), ('3L', 'glass')],
              'output': ('4R', 'lens'),
              'time': 12, },
    'case': {'machines': 'AGJ',
              'layout': 'D  FG ',
              'input': [('0L', 'metal'), ('3L', 'metal')],
              'output': ('4R', 'case'),
              'time': 5, },
    'bowl': {'machines': 'DE',
              'layout': 'DE    ',
              'input': [('0L', 'glass'), ],
              'output': ('1R', 'bowl'),
              'time': 5, },
    'motor': {'machines': 'EFI',
              'layout': 'EF I  ',
              'input': [('0T', 'copper_ingot'), ('3L', 'metal')],
              'output': ('1T', 'motherboard'),
              'time': 7, },
    
    # final
    'book': {'machines': 'ABDE',
              'layout': 'ABD E ',
              'input': [('0T', 'paper'), ('1T', 'paper'), ('2T', 'brown_organic')],
              'output': ('4R', 'book'),
              'time': 8, },
    'coffee': 'machines': 'ACEG',
              'layout': 'A  CEG',
              'input': [('0L', 'organic'), ('3B', 'bowl'), ('4B', 'metal')],
              'output': ('5B', 'coffee'),
              'time': 7, },
    'axe': 'machines': 'BDF',
              'layout': 'BDF  ',
              'input': [('0L', 'metal'), ('2T', 'brown_organic')],
              'output': ('2B', 'axe'),
              'time': 8, },
    'blender': 'machines': 'FGJI',
              'layout': 'FGJ  I',
              'input': [('0T', 'motor'), ('1T', 'bowl'), ('2R', 'copper_ingot')],
              'output': ('5R', 'blender'),
              'time': 7, },
    'camera': 'machines': 'ADBEF',
              'layout': 'ADB EF',
              'input': [('0T', 'lens'), ('1T', 'case'), ('2T', 'circuit_board')],
              'output': ('4L', 'camera'),
              'time': 12, },
    'phone': 'machines': 'JHFAB',
              'layout': 'JHFA B',
              'input': [('3L', 'glass'), ('0T', 'circuit_board'), ('2T', 'gold_ingot')],
              'output': ('5R', 'phone'),
              'time': 10, },
    'tv': 'machines': 'KIGE',
              'layout': '  KIGE',
              'input': [('2T', 'glass'), ('3L', 'case'), ('4B', 'circuit_board')],
              'output': ('5T', 'tv'),
              'time': 12, },
    'computer': 'machines': 'FGHIJK',
              'layout': 'FHGKJI',
              'input': [('0L', 'case'), ('1T', 'motherboard'), ('2R', 'graphics_card')],
              'output': ('3B', 'computer'),
              'time': 15, },
    
    
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
        'conveyors': 16,
        'inputs': ('paper', 'brown_organic'),
        'machines': "ABCDE",
        'products': [(12, 'book'),],
        'help': ['circuit_board', 'book'],
    },

    # axe
    'Chop chop!': {
        'conveyors': 15,
        'inputs': ('metal', 'brown_organic'),
        'machines': "ABDEF",
        'products': [(8, 'axe'),],
        'help': ['circuit_board', 'book', 'axe'],
    },
    
    # coffee
    'eat, work, sleep, repeat': {
        'conveyors': 16,
        'inputs': ('organic', 'glass', 'metal'),
        'machines': "ACDEEGF",
        'products': [(10, 'coffee'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee'],
    },
    
    # blender
    'Cake day': {
        'conveyors': 20,
        'inputs': ('glass', 'copper_ingot', 'metal'),
        'machines': "ABDEFGJI",
        'products': [(15, 'blender'), (15, 'bowl'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                 'motor', 'blender'],
    },
    
    # phone
    "Don't forget to call your mother!": {
        'conveyors': 20,
        'inputs': ('glass', 'copper_ingot', 'metal', 'gold_ingot',),
        'machines': "JHFAB ABCD I",
        'products': [(10, 'tv'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                'motor', 'blender', 'case', 'tv', 'phone'],
    },
    
    # tv
    'Watch me get a promotion': {
        'conveyors': 20,
        'inputs': ('glass', 'copper_ingot', 'metal'),
        'machines': "KIGE AGJ ABCD",
        'products': [(10, 'tv'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                'motor', 'blender', 'case', 'tv'],
    },
    
    # computer
    'Employee of the month': {
        'conveyors': 20,
        'inputs': ('metal', 'copper_ingot', 'gold_ingot', 'copper_ingot'),
        'machines': "FGHIJK AGJ DFG BC", # missing second D, muahaha
        'products': [(5, 'computer'), (10, 'graphics card'),],
        'help': ['circuit_board', 'book', 'axe', 'bowl', 'coffee', 
                 'motor', 'blender', 'case', 'tv', 'motherboard', 'computer'],
    },
}