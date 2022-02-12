import pygame as pyg

class TextField:
    def __init__(self, size, pos, color, font, text):
        self.rect = pyg.Rect(pos, size)
        self.color = color
        self.font = font
        self.surf = pyg.Surface(size)
        self.text = text
        self.surf.fill(pyg.Color(32, 14, 135))
        self.surf.blit(self.font.render(str(self.text), False, color), self.rect.topleft)
        self.active = False

    # Call when trying to select text field (not implemented)
    def try_select(self):
        pass

    # Call when trying to update the text in a tect field (not implemented)
    def update_text(self):
        self.surf.fill(pyg.Color(32, 14, 135))
        text_surf = self.font.render(str(self.text), False, self.color)
        self.surf.blit(text_surf, self.rect.topleft)

    # Call every frame (to render to the screen)!
    def draw(self, other_surf):
        other_surf.blit(self.surf, self.rect.topleft)