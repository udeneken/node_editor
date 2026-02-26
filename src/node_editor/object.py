import tkinter as tk
from math import dist
from itertools import accumulate

from .utils import lerp

class Text:
    def __init__(self, canvas, x, y, text):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.text = text

    def draw(self):
        self.canvas.create_text((self.x, self.y), text=self.text)

class Node:
    def __init__(self, canvas, x, y, width=200, height=50, text='', edges=None, outline_thickness=2, color_fill='white', color_outline='black', color_text='black', place_centered=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if place_centered:
            self.x = x - width // 2
            self.y = y - height // 2

        self.outline_thickness = outline_thickness
        self.color_fill = color_fill
        self.color_outline = color_outline
        self.color_text = color_text

        self.text = text

        self.selected = False

        if edges is not None:
            self.edges = edges
        else:
            self.edges = []


        print(f'New Node: x = {x}, y = {y}, width = {width}, height = {height}')

    def get_point_inside(self, x, y):
        '''Check if a point is inside the node'''
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            return True
        else:
            return False

    def get_inside_rect(self, rect):
        '''Check if the node is inside a rect. '''
        x0, y0, x1, y1, = rect
        if x0 <= self.x <= x1 and x0 <= self.x + self.width <= x1 and \
            y0 <= self.y <= y1 and y0 <= self.y + self.height <= y1:
            return True
        else:
            return False

    def get_data(self):
        return {'x': self.x, 'y': self.y, 'width': self.width, 'height': self.height, 'text': self.text,
                'color_fill': self.color_fill, 'color_outline': self.color_outline, 'color_text': self.color_text}

    def get_rect(self, margin=0):
        return [self.x - margin, self.y - margin, self.x + self.width + margin, self.y + self.height + margin]

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def draw(self):
        self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, width=self.outline_thickness, fill=self.color_fill, outline=self.color_outline)
        if self.text != '':
            self.canvas.create_text((self.x + self.width//2, self.y + self.height // 2), text=self.text, fill=self.color_text)


class Edge:
    def __init__(self, canvas, nodeA, nodeB, direction='-->', text='', text_pos_t=0.5):
        self.canvas = canvas

        self.nodeA = nodeA
        self.nodeB = nodeB
        self.connect()
        self.direction = direction

        self.description = f'{nodeA.text} {direction} {nodeB.text}'

        self.text = ''
        self.text_pos_t = text_pos_t
        self.text_pos = None # gets set in self.update

        self.update()

        print(f'New Edge: nodeA = {nodeA},  nodeB = {nodeB}, num_points = {len(self.points)}')
        # print(self.points)

    def connect(self):
        if self not in self.nodeA.edges:
            self.nodeA.add_edge(self)
        if self not in self.nodeB.edges:
            self.nodeB.add_edge(self)

    def find_points(self):
        xA, yA = self.nodeA.x, self.nodeA.y
        wA, hA = self.nodeA.width, self.nodeA.height
        xB, yB = self.nodeB.x, self.nodeB.y
        wB, hB = self.nodeB.width, self.nodeB.height

        # Centers
        centerA = (xA + wA // 2, yA + hA // 2)
        centerB = (xB + wB // 2, yB + hB // 2)

        dx = centerB[0] - centerA[0]
        dy = centerB[1] - centerA[1]

        # Determine direction from A to B
        if abs(dx) > abs(dy):
            # More horizontal movement
            if dx > 0:
                start = (xA + wA, centerA[1])  # EAST side of A
                end = (xB, centerB[1])         # WEST side of B
            else:
                start = (xA, centerA[1])       # WEST side of A
                end = (xB + wB, centerB[1])    # EAST side of B
        else:
            # More vertical movement
            if dy > 0:
                start = (centerA[0], yA + hA)  # SOUTH side of A
                end = (centerB[0], yB)         # NORTH side of B
            else:
                start = (centerA[0], yA)       # NORTH side of A
                end = (centerB[0], yB + hB)    # SOUTH side of B

        # If the start and end are not aligned in a straight line, add midpoints
        if start[0] == end[0] or start[1] == end[1]:
            return [start, end]
        else:
            dmid = (start[1] - end[1]) // 2

            mid1 = (start[0], start[1] - dmid)
            mid2 = (end[0], mid1[1])
            return [start, mid1, mid2, end]

    def update(self):
        self.points = self.find_points()
        self.text_pos = self.get_coords(self.text_pos_t)

    def get_coords(self, t):
        assert(0 <= t <= 1, 'Edge between 0 and 1. ')
        if t == 0:
            return self.points[0]
        elif t == 1:
            return self.points[-1]
        else:
            seg_lengths = [dist(self.points[i], self.points[i+1]) for i in range(len(self.points) - 1)]
            seg_lengths.insert(0, 0.)
            total_length = sum(seg_lengths)
            seg_lengths = list(accumulate([seg / total_length for seg in seg_lengths])) # numpy?
            # print(seg_lengths)
            for i, seg in enumerate(seg_lengths):
                if t < seg:
                    p1 = self.points[i-1]
                    t1 = seg_lengths[i-1]
                    p2 = self.points[i]
                    t2 = seg_lengths[i]
                    x = int(lerp(t1, p1[0], t2, p2[0], t))
                    y = int(lerp(t1, p1[1], t2, p2[1], t))
                    # print(f'found {x} {y}')
                    return [x, y]


    def get_data(self):
        return {'nodeA': self.nodeA, 'nodeB': self.nodeB, 'direction': self.direction}

    def draw(self):
        for i in range(len(self.points) - 1):
            if i == 0 and self.direction in ['<--', '<-->']:
                self.canvas.create_line(self.points[i][0], self.points[i][1], self.points[i + 1][0], self.points[i + 1][1], arrow=tk.FIRST)
            elif i == len(self.points) - 2 and self.direction in ['-->', '<-->']:
                self.canvas.create_line(self.points[i][0], self.points[i][1], self.points[i + 1][0], self.points[i + 1][1], arrow=tk.LAST)
            else:
                self.canvas.create_line(self.points[i][0], self.points[i][1], self.points[i + 1][0], self.points[i + 1][1])

        if self.text != '':
            self.canvas.create_text(self.text_pos, text=self.text, fill='black')

class Group:
    def __init__(self, canvas, elements, selected=False):
        self.canvas = canvas
        self.elements = elements

        self.selected = selected

        self.get_bbox()

    def get_bbox(self):
        x = 10000
        y = 10000
        width = 0
        height = 0
        for element in self.elements:
            x = min(element.x, x)
            y = min(element.y, y)
            width = max(element.x, x)
            height = min(element.y, y)
        self.x = x
        self.y = y
        self.width = width - x
        self.height = height - y

    def draw(self):
        if self.selected:
            self.canvas.create_line(self.x, self.y, self.x + self.width, self.y)
            self.canvas.create_line(self.x + self.width, self.y, self.x + self.width, self.y + self.height)
            self.canvas.create_line(self.x + self.width, self.y + self.height, self.x , self.y + self.height)
            self.canvas.create_line(self.x, self.y + self.height, self.x , self.y)
