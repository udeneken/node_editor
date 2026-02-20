from functools import partial
from math import dist

from .object import Node, Edge
from .export import open_file

class KeyboardHandler:
    def __init__(self, app):
        self.app = app

       # handle keyboard inputs

    def handles_key_input(self, event):
        app = self.app
        key = event.keysym
        if key == 'Escape':
            app.reset()
        elif key == 'colon' and app.mode != 'Command': # enter command mode
            app.root.cmd_frame.lift()
            app.change_mode('Command')

        elif app.mode == 'Command': # enter command
            command = app.get_command()
            if key == 'Return':
                # app.change_mode('Normal')
                app.root.cmd_frame.lower()
                self.run_command(command)
                return
            elif key == 'Escape':
                app.reset()
                return
            elif key == 'BackSpace' and len(command) == 1:
                app.set_command('')
                app.root.cmd_frame.lower()
                app.change_mode('Normal') # go back to normal mode with no command
                return
            else:
                if key == 'v' and app.modifiyers['Control']:
                    command += app.clipboard_get()
                else:
                    command = self.add_and_replace_key(command, event)
                app.set_command(command)

        elif app.mode == 'Normal':
            if key == 'question':
                app.change_mode('Help')
                help_str = '\n'.join(f'({i}) {n:<10}: {exp}'for i, (n, exp) in enumerate(app.modes.items())) # explain modes
                help_str += '\n Press <:> and enter "help" to get help with commands'
                app.display_help(help_str)
            elif key == 'v':
                app.select_once = True
                app.change_mode('Visual')
            elif key == 'V': # Enter visual mode
                app.change_mode('Visual')
            elif key == 'a': # create empty node at cursor
                new_node = Node(app.root.canvas, app.cursor_x, app.cursor_y)
                app.add_node(new_node)
                app.redraw()
            elif key == 'i': # create node at cursor and insert text
                # check if node under curser
                for node in app.get_objs(Node):
                    if node.get_point_inside(app.cursor_x, app.cursor_y):
                        app.deselect()
                        app.select_obj(node)

                if len(app.selection) == 0:
                    new_node = Node(app.root.canvas, app.cursor_x, app.cursor_y)
                    app.add_node(new_node)
                    app.select_obj(new_node)
                    app.redraw()
                app.change_mode('Insert')
            elif key == 'c': # enter connect mode
                app.change_mode('Connect')
                app.redraw()
            elif key == 'x': # delete selection otherwise delete node under cursor
                if len(app.selection) == 0:
                    for node in app.get_objs(Node):
                        if node.get_point_inside(app.cursor_x, app.cursor_y):
                            app.select_obj(node)

                if len(app.selection) > 0:
                    deleted_objs = app.delete_objs(app.selection)

                    app.add_undoredo(
                        undo_call=partial(app.all_objs.extend, deleted_objs),
                        redo_call=partial(app.delete_objs, deleted_objs)
                    )

                    app.deselect()

                    # select closest node to deleted nodes
                    nodes = app.get_objs(Node)
                    if len(nodes) > 0:
                        num_nodes = sum([type(sel) is Node for sel in deleted_objs])
                        center = [sum([sel.x if type(sel) is Node else 0 for sel in deleted_objs]) / num_nodes,
                            sum([sel.y if type(sel) is Node else 0 for sel in deleted_objs]) / num_nodes]
                        next_selected_node = sorted(nodes, key=lambda node: dist([node.x, node.y], center))[0]
                        print(f'next node: {next_selected_node}')
                        app.select_obj(next_selected_node)
                app.redraw()
            elif key == 'u':
                app.undo()
            elif key == 'r':
                app.redo()
            elif key == 'm':
                app.change_mode('Move')
            elif key.lower() in 'hjkl':
                if len(app.selection) == 0:
                    dx, dy = app.grid_width, app.grid_height
                    if event.state:
                        dx, dy = 2 * dx, 2 * dy

                    move = app.move_curser
                    if len(app.selection) > 0:
                        move = app.move_selection

                    if key.lower() == 'h':
                        app.move_curser(-dx, 0)
                    elif key.lower() == 'j':
                        app.move_curser(0, dy)
                    elif key.lower() == 'k':
                        app.move_curser(0, -dy)
                    elif key.lower() == 'l':
                        app.move_curser(dx, 0)
                else:
                    if key.lower() == 'h':
                        nodes = sorted(app.get_objs(Node), key=lambda node: node.x)
                    elif key.lower() == 'l':
                        nodes = sorted(app.get_objs(Node), key=lambda node: node.x, reverse=True)
                    elif key.lower() == 'j':
                        nodes = sorted(app.get_objs(Node), key=lambda node: node.y)
                    elif key.lower() == 'k':
                        nodes = sorted(app.get_objs(Node), key=lambda node: node.y, reverse=True)

                    for i, node in enumerate(nodes):
                        if node in app.selection:
                            if i == 0:
                                app.deselect()
                                app.select_obj(nodes[-1])
                                break

                            else:
                                app.deselect()
                                app.select_obj(nodes[i-1])
                                break

                app.redraw()

        elif app.mode == 'Move':
            dx, dy = app.grid_width, app.grid_height
            if event.state:
                dx, dy = 2 * dx, 2 * dy

            move = app.move_curser
            if app.modifiyers['Shift']:
                dx, dy = 2 * dx, 2 * dy

            move = app.move_curser
            if len(app.selection) > 0:
                move = app.move_selection

            if key.lower() == 'h':
                move(-dx, 0)
            elif key.lower() == 'j':
                move(0, dy)
            elif key.lower() == 'k':
                move(0, -dy)
            elif key.lower() == 'l':
                move(dx, 0)
            app.redraw()


        elif app.mode == 'Insert':

            if len(app.selection) == 1 and type(app.selection[0]) is Node:
                app.selection[0].text = self.add_and_replace_key(app.selection[0].text, event)
            app.redraw()

        elif app.mode == 'Connect':
            if key == 'v' or key == 'V':
                app.change_mode('Visual')
                return

            nodes = app.get_objs(Node)
            for letter, node in app.name_obj(nodes):
                if key == letter:
                    if app.connectNode is None:
                        app.connectNode = node
                        app.connectLetter = letter
                        app.set_status(f'Connect: {app.connectLetter}')
                    elif app.connectNode != node:
                        new_edge = Edge(app.root.canvas, app.connectNode, node)
                        app.add_edge(new_edge)
                        app.set_status(f'Connect: {app.connectLetter} --> {letter}')

                        #TODO: fix delete_obj increases undo counter
                        app.add_undoredo(
                            undo_call=partial(app.delete_objs, [new_edge]),
                            redo_call=partial(app.add_edge, new_edge)
                        )

                        app.connectNode = None # reset first Node
                    break

        elif app.mode == 'Visual':
            # app.deselect()
            if key == 'i':
                app.change_mode('Insert')
            elif key == 'v' or key == 'V': # leave visual mode with selection
                app.change_mode('Normal')
            nodes = app.get_objs(Node)

            if key.lower() not in 'hjkliv':
                if key.islower():
                    app.deselect()
                obj_selected = False
                for letter, node in app.name_obj(nodes):
                    if key.lower() == letter:
                        if node in app.selection:
                            app.deselect(node)
                        else:
                            app.select_obj(node)
                        obj_selected = True
                        break
                if obj_selected:
                    print(f'Selected: {app.selection}')
                else:
                    print(f'No obj selected. (key == {key})')


                app.redraw()
                # app.change_mode('Normal')


            # move
            dx, dy = app.grid_width, app.grid_height
            if event.state:
                dx, dy = 2 * dx, 2 * dy
            if key.lower() == 'h':
                app.move_selection(-dx, 0)
            elif key.lower() == 'j':
                app.move_selection(0, dy)
            elif key.lower() == 'k':
                app.move_selection(0, -dy)
            elif key.lower() == 'l':
                app.move_selection(dx, 0)

            if app.select_once:
                app.select_once = False
                if not app.modifiyers['Shift']:
                    app.change_mode('Normal')
        
        elif app.mode == 'Help':
            if key in '0123456789':
                mode = list(app.modes)[int(key)]
                app.redraw()
                if mode == 'Normal':
                    app.display_help('This is help for normal. ')
            else:
                app.change_mode('Normal')
        
        app.buffer.append(key)
        app.root.buffer_label.text = app.buffer

    def modifiyer_pressed(self, event):
        modifiyer = event.keysym[:-2]
        self.app.modifiyers[modifiyer] = True
        self.app.select_once = False
        # self.app.redraw()
        # if app.debug: print(f'{modifiyer} pressed')

    def modifiyer_released(self, event):
        modifiyer = event.keysym[:-2]
        self.app.modifiyers[modifiyer] = False
        # self.app.redraw()
        # if app.debug: print(f'{modifiyer} released')

    def add_and_replace_key(self, current_String, new_key_event):
        if new_key_event.keysym == 'BackSpace':
            if self.app.modifiyers['Control']:
                current_String = ' '.join(current_String.split(' ')[:-1])
                if current_String == '' and self.app.mode == 'Command':
                    current_String = ':'
            else:
                current_String = current_String[:-1] # delete last char
            return current_String
        elif new_key_event.keysym == 'Return':
            newKey = '\n'
        else:
            newKey = new_key_event.char
        return current_String + newKey

        # Handle commands

    def run_command(self, command):
        command = command.strip()
        app = self.app
        if command == ':q':
            app.ask_to_save()
        elif command == ':q!':
            print('Force quit!')
            app.root.quit()
        elif command.startswith(':w'):
            app.save(command)
        elif command.startswith(':o'):
            open_file(app, command[3:])
            app.change_mode('Normal')
        elif command.startswith(':help'):
            app.get_help(command)
        elif command == ':c' or command == ':clear':
            app.clean()
        elif command == ':grid':
            app.toggle_grid()
        elif command == ':debug':
            app.toggle_debug()
        elif command == ':av':
            app.align('vertically')
        elif command == ':ah':
            app.align('horizontally')
        elif command.startswith(':set canvas'):
            width, height = command.replace(':set canvas ', '').strip().split(' ')[:2]
            width, height = int(width), int(height)
            app.set_canvas_size(width, height)
        else:
            app.set_status(f'Command "{command}" does not exsit. ')
            print(f'Command "{command}" does not exsit. ')
            app.change_mode('Normal')
