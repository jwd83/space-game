import pygame
import os


class Actor():
    def __init__(self, folder, position, sheet: str = "idle", scale=1.0, dimensions=None):
        self.x, self.y = position
        self.sheet: str = sheet
        self.frame: int = 0
        self.animation_rate = 1
        self.animation_length = 1
        self.sprites = {}
        self.scale = scale
        self.load_sheets(folder, dimensions)
        self.set_sheet(sheet)

    def set_sheet(self, sheet: str):
        self.sheet = sheet
        self.frame = 0

        self.animation_length = 0
        # check how many frames are in the sprite dictionary that start with the sheet name
        for key in self.sprites.keys():
            if key.startswith(self.sheet):
                self.animation_length += 1

    def load_sheets(self, sheet_folder, dimensions: list | None = None):
        # set self.sprites to a an empty dictionary
        self.sprites = {}
        h = 0
        w = 0
        if dimensions is not None:
            h = dimensions[0]
            w = dimensions[1]

        # load all files in a directory
        for file in os.listdir(sheet_folder):
            if file.lower().endswith(".png"):
                # remove png from the filename and store it in frame_base_name
                frame_base_name = file[:-4]

                frame = pygame.image.load(os.path.join(
                    sheet_folder, file)).convert_alpha()

                if dimensions is None:
                    if self.scale == 1.0:
                        self.sprites[frame_base_name] = frame
                    else:
                        self.sprites[frame_base_name] = pygame.transform.scale(
                            frame, (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale)))
                else:
                    # calculate how many rows and columns are in the sheet
                    rows = frame.get_height() // h
                    cols = frame.get_width() // w
                    frame_base_number = 0
                    for row in range(rows):
                        for col in range(cols):
                            frame_key = frame_base_name + \
                                "-" + str(frame_base_number)

                            # add the surface to the dictionary
                            # self.sprites[frame_key] = todo
                            frame_base_number += 1

    def move(self, vx, vy):
        self.x += vx
        self.y += vy

    def reposition(self, position):
        self.x, self.y = position

    def draw(self, surface):

        # calculate our frame number
        frame_number = int(
            self.frame / self.animation_rate) % self.animation_length
        frame_key = self.sheet + "-" + str(frame_number)

        # draw the frame onto the surface
        surface.blit(self.sprites[frame_key], (self.x, self.y))

        self.frame += 1
