# import game
import pygame as pyg
import vectors
import UI
import pyperclip

changed_variables = {}

def reset_all():
    for changed in changed_variables:
        changed = changed_variables[changed]

class DebugPanel:
    def __init__(self, size, pos):
        pass
        self.debug_surf = pyg.Surface(size)
        self.pos = pos
        self.input_box = UI.TextField(vectors.Vec([size[0], size[1] / 4]), vectors.Vec([0, 0]), pyg.Color(255, 255, 255), pyg.font.SysFont("DejaVu Serif", 16), "")
        self.output = ""

    # draw text field onto this, then draw this onto passed in surface
    def update(self, surf):
        self.debug_surf.fill(pyg.Color(158, 34, 29))
        self.input_box.draw(self.debug_surf)
        surf.blit(self.debug_surf, self.pos)

    # syntax for changing variable
    # change var1 val
    # changes variable var1 to the value val
    def parse_input(self) -> tuple:
        input_text = self.input_box.text.split(" ")
        self.output += self.input_box.text + "\n"
        self.input_box.text = ""
        if input_text[0].lower() == "change":
            return (input_text[1], float(input_text[2]))
        elif input_text[0].lower() == "copy":
            pyperclip.copy(self.output)
            return ()
        else:
            return ()