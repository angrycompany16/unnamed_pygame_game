import os, vectors

delta_time = 0
path = os.getcwd()
rounded_camera_scroll = vectors.Vec([0, 0])

def get_screen_pos(pos):
    return vectors.Vec([
        pos[0] - rounded_camera_scroll[0],
        pos[1] - rounded_camera_scroll[1]
    ])