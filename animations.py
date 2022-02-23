import pygame as pyg
import game_manager as gm

class Clip():
    def __init__(self, sprite_sheet, width, height, frame_duration) -> None:
        self.frame_duration = frame_duration
        self.frames = []
        self.sprite_sheet = sprite_sheet

        self.frame_index = 0

        self.time_since_last_frame = 0

        for i in range(width * height):
            self.frames.append(pyg.Surface((width, height), pyg.SRCALPHA))

        for i in range(height):
            for j in range(width):
                self.frames[i * width + j].blit(self.sprite_sheet, (0, 0), pyg.Rect((width * j, height * i), (width, height)))

        self.image = None
        self.next_frame = self.frames[0]
        self.step()

    def update(self):
        self.time_since_last_frame += gm.delta_time

        if self.time_since_last_frame > self.frame_duration:
            self.step()
            self.time_since_last_frame = 0

    def step(self):
        self.image = self.next_frame
        self.next_frame = self.frames[self.frame_index]
        self.frame_index += 1
        if self.frame_index > 2:
            self.frame_index = 0
        