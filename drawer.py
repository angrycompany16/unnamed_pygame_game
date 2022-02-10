class SurfGroup():
    def __init__(self):
        self.list = []

    def add(self, surface, order):
        self.list.append(0)
        self.list[order] = surface

    def draw(self, target_surf):
        for surf in self.list:
            target_surf.blit(surf, (0, 0))

    def fill(self, color):
        for surf in self.list:
            surf.fill(color)