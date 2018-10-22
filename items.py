
class Item(Actor):
    """A resource or built product of some sort,
    from ore, to circuit boards to bicycles.
    
    Mostly passive - position, etc. are set by its container,
    player, conveyor, etc.
    
    Item anchors should be in the bottom middle of the image,
    so that they sit on the conveyor in convincing fashion :)"""
    
    def __init__(self, name, *args, **kwargs):
        self.name = name
        image_name = 'items/{}'.format(self.name)
        super().__init__(image_name, *args, **kwargs)
        self.x = -100
        self.y = -100

    def __str__(self):
        return "<Item: {}>".format(self.name)
        
    def draw(self):
        super().draw()