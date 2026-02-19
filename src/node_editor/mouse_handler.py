from .object import Node

class MouseHandler:
    def __init__(self, app):
        self.app = app

    def mouse_pressed(self, event):
        x, y = event.x, event.y
        self.app.last_mouse_x = x
        self.app.last_mouse_y = y
        self.app.mouse_is_pressed = True
        self.app.non_selected = True

        # self.app.change_mode('Visual')
        self.app.set_cursor(x, y)

        # if not self.app.modifiyers['Shift']:
        #     print('des')
        #     self.app.deselect()

        for node in self.app.get_objs(Node):
            if node.get_point_inside(x, y):
                if node in self.app.selection:
                    if self.app.modifiyers['Shift']:
                        self.app.deselect(node)
                elif node not in self.app.selection and not self.app.modifiyers['Shift']:
                    self.app.deselect()
                    self.app.select_obj(node)
                else:
                    self.app.select_obj(node)
                self.app.non_selected = False

        if self.app.non_selected:
            self.app.deselect()
            self.app.change_mode('Normal')
        self.app.redraw()

    def mouse_moved(self, event):
        if self.app.mouse_is_pressed:
            x, y = event.x, event.y

            # snap to grid with shift
            if self.app.modifiyers['Shift']:
                x = (x // self.app.grid_width) * self.app.grid_width
                y = (y // self.app.grid_height) * self.app.grid_height

            if self.app.non_selected:
                # delete and redraw the rect
                if self.app.mouse_selection is not None:
                    self.app.root.canvas.delete(self.app.mouse_selection)
                self.app.mouse_selection = self.app.root.canvas.create_rectangle(self.app.cursor_x, self.app.cursor_y, x, y, dash=(4,6))
            else:
                self.app.move_selection(x - self.app.last_mouse_x, y - self.app.last_mouse_y)
                self.app.last_mouse_x, self.app.last_mouse_y = x, y

    def mouse_released(self, event):
        print('Mouse released. ')
        self.app.mouse_is_pressed = False

        if self.app.mouse_selection is not None:
            rect = self.app.root.canvas.coords(self.app.mouse_selection)
            self.app.root.canvas.delete(self.app.mouse_selection)

            # find nodes inside mouse_selection rect and select
            for node in self.app.get_objs(Node):
                if node.get_inside_rect(rect):
                    self.app.select_obj(node)

        self.app.mouse_selection = None

        print(f'Selected: {self.app.selection}')
        # if len(self.app.selection) > 0:
        #     self.app.change_mode('Visual')
        self.app.redraw()
