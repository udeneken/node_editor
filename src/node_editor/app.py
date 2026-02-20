import tkinter as tk
import string
from itertools import product
from functools import partial
from math import ceil, dist
from subprocess import run
from os.path import join, abspath, isfile
from importlib.resources import files
from collections import deque


from .object import Node, Edge, Group
from .export import import_mermaid, export_mermaid, save_canvas, open_file, export_svg
from .testing_funcs import simulate_keypress
from .mouse_handler import MouseHandler
from .keyboard_handler import KeyboardHandler

class App:
    def __init__(self, file_name, width, height, root_dir):
        self.root = tk.Tk()
        self.root.title("Node Editor")
        self.file_name = None
        if file_name != '':
            self.file_name = file_name
            self.title(f"Node Editor: {file_name}")

        # add logo
        self.root_dir = root_dir
        print(root_dir)
        try:
            icon_path = files("node_editor").joinpath("assets", "logo.png")
        except Exception:
            icon_path = join(root_dir, 'images', 'logo.png')
        photo = tk.PhotoImage(file=str(icon_path))
        self.root.wm_iconphoto(False, photo)


        self.canvas_width = width
        self.canvas_height = height

        self.window_width = self.canvas_width
        self.window_height = self.canvas_height + 30

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Try to bring window to foreground
        self.root.update_idletasks()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)

        self.modes = {
            'Normal': 'Default mode',
            'Insert': 'Insert text into nodes',
            'Command': 'Enter command like :clean',
            'Visual': 'Select Objects',
            'Connect': 'Connect nodes with Edges',
            'Move': 'Move different objects',
            'Help': 'Get help in the current mode',
            }
        self.mode = 'Normal'
        self.colors = {
            'Visual': 'red',
            'Connect': 'blue',
        }
        self.debug_on = False

        self.keyboard_handler = KeyboardHandler(app=self)
        self.buffer_size = 4
        self.buffer = deque(list(self.buffer_size * ''), maxlen=self.buffer_size)

        self.cursor_x, self.cursor_y = [50, 50]
        self.cursor_color = 'red'
        self.cursor_width = 3

        self.grid_on = False
        self.grid_color = 'gray'
        self.grid_line_width = 1
        self.grid_width, self.grid_height = [10, 10]

        self.all_objs = []
        self.selection = []
        self.selectionbb = None
        self.select_once = False

        self.connectNode = None
        self.connectLetter = None

        self.mouse_handler = MouseHandler(self)
        self.mouse_is_pressed = False
        self.mouse_selection = None
        self.non_selected = True
        self.last_mouse_x, self.last_mouse_y = 0,0

        self.undo_history = []
        self.redo_history = []
        self.undo_index = 0

        # create layout / visuals
        self.create_layout()
        self.redraw()

        # create some logic
        self.modifiyers = {
            'Shift': False,
            'Alt': False,
            'Control': False,
        }
        self.bindings()

        # load file
        if isfile(file_name):
            open_file(self, file_name)# To extract:

        # test stuff
        # nodeA = self.add_node(text='NodeA')
        # self.set_cursor(300, 300)
        # nodeB = self.add_node(text='NodeB')
        # self.add_edge(nodeA, nodeB)

#         mermaid = r'''flowchart TD
# A --> B
# B --> C'''
#         import_mermaid(self, mermaid)
#         print(export_mermaid(self))


        # save_file(self, 'test.txt')

        # open_file(self, 'tmp/test.txt')
        # self.keyboard_handler.handles_key_input(simulate_keypress('c'))
        # self.keyboard_handler.handles_key_input(simulate_keypress('a'))
        # self.keyboard_handler.handles_key_input(simulate_keypress('c'))
        # self.keyboard_handler.handles_key_input(simulate_keypress('Escape'))

        # export_svg(self, 'tmp/test.svg')

        # text = 'this is a test pPpbTXY\ntest'
        # for i,t in enumerate(text):
        #     self.root.canvas.create_text(i*8 + 100, 100, text=t)

        # self.b = True
        # self.brect = None
        # def blink():
        #     if self.b:
        #         self.brect = self.root.canvas.create_rectangle(10,10, 20, 20, fill='black')
        #         self.b = False
        #     else:
        #         self.root.canvas.delete(self.brect)
        #         self.b = True
        #     self.after(500, blink)

        # blink()

        # for i, t in enumerate(text.split('\n')):
        #     draw_obj = self.root.canvas.create_text(100, 130 + 17*i, text=t, anchor='nw')
        #     bg_text = self.root.canvas.create_rectangle(self.root.canvas.bbox(draw_obj), fill="white", outline='black', width=2)
        #     self.root.canvas.tag_lower(bg_text, draw_obj) # draw box behind text

        #     print(draw_obj)

    ## LAYOUT

    def create_layout(self):
        self.root.frame = tk.Frame(self.root, height= self.canvas_height + 50, bg='grey')
        self.root.frame.pack(side=tk.TOP, fill='y')

        self.add_functions()
        self.root.canvas = tk.Canvas(self.root.frame, bg='white', width=self.canvas_width, height=self.canvas_height)
        # self.root.canvas = tk.Canvas(self.root.frame, bg='white', width=self.canvas_width, height=self.canvas_height, scrollregion=(0,0,700,700))
        self.root.canvas.pack(pady=0)

        self.root.bottom_frame = tk.Frame(self.root.frame, height=30, bg='grey')
        self.root.bottom_frame.pack(side=tk.BOTTOM, fill='x')

        self.root.status_label = tk.Label(self.root.bottom_frame, text=f"{self.mode}", bg='grey', fg='white')
        self.root.status_label.pack(side=tk.LEFT, pady=0)

        self.root.buffer_label = tk.Label(self.root.bottom_frame, text=''.join(self.buffer), bg='grey', fg='white')
        self.root.buffer_label.pack(side=tk.RIGHT, pady=0)


        self.root.cmd_frame = tk.Frame(self.root.frame, height=30, width=300, bg='grey')
        # self.root.cmd_frame.lift()
        self.root.cmd_frame.lower()
        self.root.cmd_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        self.root.cmd_line = tk.Label(self.root.cmd_frame, text=":", bg='grey', fg='white', )
        self.root.cmd_line.pack(side=tk.LEFT, pady=0)


        # self.root.canvas = tk.Canvas(self, bg='white', width=self.canvas_width, height=self.canvas_height)
        # self.root.canvas.pack(side=tk.TOP, padx=10, pady=10)
        # # self.root.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # self.root.bottom_frame = tk.Frame(self, height=30, bg='grey')
        # self.root.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # self.root.status_label = tk.Label(self.root.bottom_frame, text=f"{self.mode}", bg='grey', fg='white', anchor='w')
        # self.root.status_label.pack(pady=0)
        # # self.root.status_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def add_functions(self):
        '''Adds some functions to the canvas'''
        def _create_circle(self, x, y, r, **kwargs):
            return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
        tk.Canvas.create_circle = _create_circle

        def _create_circle_arc(self, x, y, r, **kwargs):
            if "start" in kwargs and "end" in kwargs:
                kwargs["extent"] = kwargs.pop("end") - kwargs["start"]
            return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
        tk.Canvas.create_circle_arc = _create_circle_arc

    def set_canvas_size(self, width, height):
        if self.canvas_height < height or self.canvas_width < width:
            print('Canvas gets smaller. ')
        self.root.canvas.config(width=width, height=height)


    # DRAWING

    def redraw(self):
        self.root.canvas.delete("all")

        if self.grid_on:
            for i in range(self.canvas_width // self.grid_width):
                self.root.canvas.create_line(i * self.grid_width, 0, i * self.grid_width, self.canvas_height, width=self.grid_line_width, fill=self.grid_color)
            for j in range(self.canvas_height // self.grid_height):
                self.root.canvas.create_line(0, j * self.grid_height, self.canvas_width, j * self.grid_height, width=self.grid_line_width, fill=self.grid_color)

        nodes = self.get_objs(Node)
        # # draw guide lines
        # for node in nodes:
        #     self.root.canvas.create_line(node.x, 0, node.x, self.canvas_height, dash=(5,1))
        #     self.root.canvas.create_line(node.x + node.width, 0, node.x + node.width, self.canvas_height, dash=(5,1))
        #     self.root.canvas.create_line(0, node.y, self.canvas_width,  node.y, dash=(5,1))
        #     self.root.canvas.create_line(0, node.y + node.height, self.canvas_width,  node.y + node.height, dash=(5,1))

        # draw edges
        for edge in self.get_objs(Edge):
            edge.draw()

        # draw nodes
        for node in nodes:
            node.draw()

        # draw letter at nodes
        if self.mode in ['Connect', 'Visual']:
            for letter, node in self.name_obj(nodes):
                if self.modifiyers['Shift']:
                    letter = letter.capitalize()
                color = self.colors[self.mode]
                if node in self.selection:
                    outline = color
                else:
                    outline = ''
                letter_text = self.root.canvas.create_text(self.pos_in_canvas(node.x, node.y - 14, 14), text=letter, fill=color)
                bg_text = self.root.canvas.create_rectangle(self.root.canvas.bbox(letter_text), fill="white", outline=outline, width=2)
                self.root.canvas.tag_lower(bg_text,letter_text) # draw box behind text

        # draw selection box
        if len(self.selection) > 0:
            if len(self.selection) > 1:
                for sel_node in self.selection:
                    self.root.canvas.create_rectangle(*sel_node.get_rect(3), outline=self.colors['Visual'], width=3, dash=(4, 6))

            self.root.canvas.create_rectangle(*self.selectionbb, outline=self.colors['Visual'], width=3, dash=(4, 6))


        self.draw_cursor()
        if self.mode == 'Insert' and len(self.selection) == 1:
            pass

        # debug stuff
        if self.debug_on:
            debug_texts = [
                f'curser pos: {self.cursor_x}, {self.cursor_y}',
                f'num_objs = {len(self.all_objs)}',
                f'undo_index = {self.undo_index}'
            ]
            for i, t in enumerate(debug_texts):
                self.root.canvas.create_text(self.canvas_width - 100, 30 + 15*i, text=t, anchor='e')


    def draw_cursor(self):
        self.root.canvas.create_line(self.cursor_x + 5, self.cursor_y, self.cursor_x - 5, self.cursor_y, width=3)
        self.root.canvas.create_line(self.cursor_x, self.cursor_y + 5, self.cursor_x, self.cursor_y - 5, width=3)


    # Handleling objects

    def bindings(self):
        # modifier
        for modifiyer in self.modifiyers:
            self.root.bind(f'<KeyPress-{modifiyer}_L>', self.keyboard_handler.modifiyer_pressed)
            self.root.bind(f'<KeyPress-{modifiyer}_R>', self.keyboard_handler.modifiyer_pressed)
            self.root.bind(f'<KeyRelease-{modifiyer}_L>', self.keyboard_handler.modifiyer_released)
            self.root.bind(f'<KeyRelease-{modifiyer}_R>', self.keyboard_handler.modifiyer_released)

        # bind all normal keys
        self.root.bind(f'<Key>', self.keyboard_handler.handles_key_input)

        # other keys
        self.root.bind(f'<F5>', lambda event: self.redraw)
        self.root.bind(f'<F9>', lambda event: self.toggle_debug)


        # mouse
        self.root.canvas.bind("<ButtonPress-1>", self.mouse_handler.mouse_pressed) # only canvas is clickable
        self.root.canvas.bind("<ButtonRelease-1>", self.mouse_handler.mouse_released) # only canvas is clickable
        self.root.canvas.bind("<Motion>", self.mouse_handler.mouse_moved) # only canvas is clickable

        # other events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # do this before closing window

    def add_node(self, new_node):
        if new_node not in self.all_objs:
            self.all_objs.append(new_node)

    def add_edge(self, new_edge):
        if new_edge not in self.all_objs:
            self.all_objs.append(new_edge)
            new_edge.connect()

    def delete_objs(self, objs):
        deleted_objs = []
        for obj in objs:
            if obj in self.all_objs:
                self.all_objs.remove(obj)
                deleted_objs.append(obj)
                print(f'Deleting: {obj}')

                if type(obj) is Node:
                    for e in obj.edges:
                        if e in self.all_objs:
                            self.all_objs.remove(e)
                            deleted_objs.append(e)
                            print(f'Deleting: {e}')
        return deleted_objs

    def get_objs(self, obj_type):
        '''Get all objs of type. '''
        return [elm for elm in self.all_objs if isinstance(elm, obj_type)]

    def select_obj(self, obj):
        if obj not in self.selection:
            self.selection.append(obj)
            self.selectionbb = self.calc_bb(self.selection)

    def deselect(self, obj=None):
        if obj is not None:
            self.selection.remove(obj)
            self.selectionbb = self.calc_bb(self.selection)
        else:
            self.selection.clear()
        self.redraw()

    def name_obj(self, objs):
        '''Returns a list of objects with unique letters. '''
        num_obj = len(objs)
        all_letters = string.ascii_lowercase

        ignore_letters = ''
        if self.mode == 'Visual':
            ignore_letters = 'hjkliv'
        elif self.mode == 'Connect':
            ignore_letters = 'v'
        for ignore_letter in ignore_letters:
            all_letters = all_letters.replace(ignore_letter, '')

        if len(all_letters) < num_obj:
            all_letters = product(all_letters, repeat=ceil(num_obj / len(all_letters)))

        return zip(all_letters, objs)

    def pos_in_canvas(self, x, y, offset=0):
        return [min(max(x, offset), self.canvas_width - offset), min(max(y, offset), self.canvas_height - offset)]

    def get_status(self):
        '''Return text inside status. '''
        return self.root.status_label.cget('text')

    def get_command(self):
        '''Return text inside command_bar. '''
        return self.root.cmd_line.cget('text')

    def set_status(self, status):
        self.root.status_label.config(text=status)

    def set_command(self, command):
        self.root.cmd_line.config(text=command)

    def change_mode(self, mode):
        if mode in self.modes:
            if mode == 'Command':
                self.set_command(':')
                self.set_status('Command')
            else:
                if self.mode == 'Command' and mode == 'Normal' and self.get_command() != ':':
                    pass # use this to pass command info to statusbar
                elif mode == 'Insert' and len(self.selection) > 1:
                    self.set_status('More than one object selected.')
                    return
                else:
                    if mode == 'Connect':
                        self.deselect()
                    self.set_status(mode)
            self.mode = mode
            print(f'Changed mode to: {mode}')
        else:
            print(f'Mode {mode} does not exsit.')
        self.redraw()

    def clean(self):
        '''Clear the canvas and delete all objs. '''
        self.all_objs.clear()
        self.deselect()
        self.redraw()
        self.change_mode('Normal')

        print('Clearing')

    def toggle_grid(self):
        '''Toggle visability of gird on or   off'''
        self.grid_on = not self.grid_on
        msg = f'Grid: {"on" if self.grid_on else "off"}'
        self.set_status(msg)
        print(msg)
        self.change_mode('Normal')
        self.redraw()

    def toggle_debug(self):
        '''Toggle debug mode'''
        self.debug_on = not self.debug_on
        msg = f'Debug: {"on" if self.debug_on else "off"}'
        self.set_status(msg)
        print(msg)
        self.change_mode('Normal')
        self.redraw()

    def set_cursor(self, new_x, new_y):
        self.cursor_x = new_x
        self.cursor_y = new_y

    def move_curser(self, new_rel_x, new_rel_y):
        if 0 < self.cursor_x + new_rel_x < self.canvas_width:
            self.cursor_x = self.cursor_x + new_rel_x

        if 0 < self.cursor_y + new_rel_y < self.canvas_height:
            self.cursor_y = self.cursor_y + new_rel_y
        # print(f'moving curser: {new_rel_x}, {new_rel_y}')

    def move_selection(self, new_rel_x, new_rel_y):
        for sel in self.selection:
            if 0 < self.cursor_x + new_rel_x < self.canvas_width:
                sel.x = sel.x + new_rel_x

            if 0 < self.cursor_y + new_rel_y < self.canvas_height:
                sel.y = sel.y + new_rel_y

            if type(sel) is Node:
                for e in sel.edges:
                    e.update()
        self.selectionbb = self.calc_bb(self.selection)
        self.redraw()
        # print(f'moving selection: {new_rel_x}, {new_rel_y}')

    ## functionallity

    def calc_bb(self, objs, offset=5):
        # calc bbox
        x0, y0, x1, y1 = 10000, 10000, 0,0
        for obj in objs:
            x0 = min(obj.x, x0)
            y0 = min(obj.y, y0)
            x1 = max(obj.x + obj.width, x1)
            y1 = max(obj.y + obj.height, y1)
        # self.selectionbb = [x0 , y0, x1, y1]
        return [x0 - offset, y0 - offset, x1 + offset, y1 + offset]

    def get_help(self, help_string):
        '''Get help'''
        help_string = help_string.lstrip(':help ')
        if help_string == '':
            self.set_status(f'Try :help <command> or :help <Mode>')
        elif help_string in self.modes:
            self.set_status(f'{help_string}: {self.modes[help_string]}')
        elif hasattr(self, help_string):
            try:
                doc_string = getattr(self, help_string).__doc__
                self.set_status(f'{help_string}: {doc_string}')
            except:
                self.set_status(f'{help_string}: not found')

    def display_help(self, help_str):
        lines = help_str.split('\n')
        count_lines = len(lines)
        max_lines = max([len(l) for l in lines])
        w = max_lines * 8
        h = count_lines * 20
        x0 = self.canvas_width//2 - w // 2
        x1 = self.canvas_width//2 + w // 2
        y0 = self.canvas_height//2 - h // 2
        y1 = self.canvas_height//2 + h // 2
        self.root.canvas.create_rectangle(x0, y0, x1, y1, width=2, fill='gray', outline='black')
        self.root.canvas.create_text((self.canvas_width//2, self.canvas_height//2), text=help_str, fill='black')
        print("display help")

    def reset(self):
        self.change_mode('Normal')
        self.set_status('Normal')
        self.set_command('')
        self.root.cmd_frame.lower()
        print('Deselect all. ')
        self.deselect()
        self.redraw()

    def align(self, mode='vertically'):
        '''Takes the selection and alignes them.'''
        if mode not in ['vertically', 'horizontally']:
            self.set_status(f'Mode {mode} does not exsist.')
            self.change_mode('Normal')
            return
        if len(self.selection) == 0:
            self.set_status('Selection is empty. ')
            self.change_mode('Normal')
            return

        # calculate selection center
        center_x, center_y = 0, 0
        for sel in self.selection:
            center_x += sel.x + sel.width // 2
            center_y += sel.y + sel.height // 2
        center_x /= len(self.selection)
        center_y /= len(self.selection)

        # apply translation
        if mode == 'vertically':
            for sel in self.selection:
                sel.x = center_x - sel.width // 2
        elif mode == 'horizontally':
            for sel in self.selection:
                sel.y = center_x - sel.height // 2

        # update edges and selectionbb
        for sel in self.selection:
            for e in sel.edges:
                e.update()
        self.selectionbb = self.calc_bb(self.selection)

        self.redraw()
        msg = f'{mode.capitalize()} algined'
        self.set_status(msg)
        print(msg)
        self.change_mode('Normal')

    def undo(self):
        if len(self.undo_history) > 0 and self.undo_index > 0:
            self.undo_index -= 1
            elem = self.undo_history[self.undo_index]
            elem() # run function
            self.set_status('Undo')
            print('Undo')
            print('undo_hist:  \n\t' + '\n\t'.join([str(s) for s in self.undo_history]))
            print('redo_hist:  \n\t' + '\n\t'.join([str(s) for s in self.redo_history]))
            print(f'undo_index: {self.undo_index}')
            self.redraw()

    def redo(self):
        if len(self.redo_history) > 0 and self.undo_index < len(self.redo_history):
            elem = self.redo_history[self.undo_index]
            elem()
            self.set_status('Redo')
            print('Redo')
            print('undo_hist:  \n\t' + '\n\t'.join([str(s) for s in self.undo_history]))
            print('redo_hist:  \n\t' + '\n\t'.join([str(s) for s in self.redo_history]))
            print(f'undo_index: {self.undo_index}')
            self.undo_index += 1
            self.redraw()

    def add_undoredo(self, undo_call, redo_call):
        # delete unreached entries
        self.undo_history = self.undo_history[:self.undo_index]
        self.redo_history = self.redo_history[:self.undo_index]

        # append new entry
        self.undo_history.append(undo_call)
        self.redo_history.append(redo_call)
        self.undo_index += 1

    def on_closing(self):
        self.ask_to_save()
        self.root.quit()

    def ask_to_save(self):
        '''TODO: Ask if and where to save. '''
        self.root.quit()

    def save(self, command):
        new_file = command.split(' ')[-1]
        if new_file != ':w':
            save_canvas(self, new_file)
        elif self.file_name is None:
            self.set_status('No file_name given. Please use :w path/to/file.txt')
            print('File not given')
        else:
            save_canvas(self, self.file_name)
            print(self.file_name)
        self.change_mode('Normal')
