import sys
from CodeGenerator import parser


def read_file(file):
    with open(file, "r") as file:
        return file.read()


def write_file(file, program):
    with open(file, "w") as file:
        file.write(program)


def output_handler():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    file = read_file(input_file)
    try:
        parsed = parser.parse(file, tracking=True)
    except Exception as e:
        print(e)
        exit()
    write_file(output_file, parsed)


output_handler()
