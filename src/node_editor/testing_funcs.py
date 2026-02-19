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