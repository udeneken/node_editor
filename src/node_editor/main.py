import argparse
import sys
from os.path import abspath, dirname, join

from .app import App

def parse_input():
    parser = argparse.ArgumentParser(description='A node editor')

    parser.add_argument('-f', '--filename', default='', type=str, help='The filename where the data is saved to.')
    parser.add_argument('-cw', '--width', default=800, type=int,help='Canvas width in pixels')
    parser.add_argument('-ch', '--height', default=600,type=int, help='Canvas height in pixels')


    args, unknown = parser.parse_known_args()

    # print args
    arg_list = list(filter(lambda x: not x.startswith('_'), dir(args)))  # get all new attributes
    args_dict = dict(zip(arg_list, list(map(lambda x : getattr(args, x), arg_list)))) # put them in a dict with there values
    print(f'Args: {args_dict}')

    if len(unknown) > 0:
        print(f'Unkown args: {unknown}')

    return args


def main():
    args = parse_input()

    file_name = args.filename
    width = args.width
    height = args.height

    root_dir = join(dirname(sys.argv[0]), '..')

    # run app
    app = App(file_name, width, height, root_dir)

    app.root.mainloop()


if __name__ == "__main__":
    main()
