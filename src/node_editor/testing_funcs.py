from .object import Node, Edge

class SimulatedEvent:
    def __init__(self, key=''):
        self.keysym = key
        if key.isupper():
            self.state = 1
        else:
            self.state = 0

        self.x = 0
        self.y = 0


def simulate_keypress(key):
    event = SimulatedEvent(key=key)
    print(f'Simulate pressing {key}')
    return event

def test_stuff(app):
    # test stuff
    app.reset()
    nodeA = Node(app.root.canvas, app.cursor_x, app.cursor_y, text='NodeA')
    app.add_node(nodeA)
    app.set_cursor(300, 300)
    nodeB = Node(app.root.canvas, app.cursor_x, app.cursor_y, text='NodeB')
    app.add_node(nodeB)
    edge = Edge(app.root.canvas, nodeA, nodeB)
    app.add_edge(edge)
    app.redraw()

#         mermaid = r'''flowchart TD
# A --> B
# B --> C'''
#         app.import_mermaid(app, mermaid)
#         print(app.export_mermaid())


#     app.save_file('test.txt')

#     app.open_file('tmp/test.txt')
#     app.keyboard_handler.handles_key_input(simulate_keypress('c'))
#     app.keyboard_handler.handles_key_input(simulate_keypress('a'))
#     app.keyboard_handler.handles_key_input(simulate_keypress('c'))
#     app.keyboard_handler.handles_key_input(simulate_keypress('Escape'))

#     app.export_svg('tmp/test.svg')

#     text = 'this is a test pPpbTXY\ntest'
#     for i,t in enumerate(text):
#         app.root.canvas.create_text(i*8 + 100, 100, text=t)

#     app.b = True
#     app.brect = None
#     def blink():
#         if app.b:
#             app.brect = app.root.canvas.create_rectangle(10,10, 20, 20, fill='black')
#             app.b = False
#         else:
#             app.root.canvas.delete(app.brect)
#             app.b = True
#         app.after(500, blink)

#     blink()

#     for i, t in enumerate(text.split('\n')):
#         draw_obj = app.root.canvas.create_text(100, 130 + 17*i, text=t, anchor='nw')
#         bg_text = app.root.canvas.create_rectangle(app.root.canvas.bbox(draw_obj), fill="white", outline='black', width=2)
#         app.root.canvas.tag_lower(bg_text, draw_obj) # draw box behind text

#         print(draw_obj)