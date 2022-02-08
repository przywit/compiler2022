import re

jump_points = []


def clear_output(program):
    line_counter = 0
    cleared_lines = []
    for line in program.split("\n"):
        matched = re.findall("@TO[0-9]+@", line)
        if matched:
            for match in matched:
                id = int(match[3:-1])
                jump_points[id] = line_counter
                line = re.sub("@TO[0-9]+@", "", line)
        cleared_lines.append(line)
        line_counter += 1
    jump_counter = 0
    result = ""
    for line in cleared_lines:
        matched = re.search("@JUMP[0-9]+@", line)
        if matched is not None:
            id = int(matched.group()[5:-1])
            jump_to = jump_points[id] - jump_counter
            line = re.sub("@JUMP[0-9]+@", str(jump_to), line)
        result += line + "\n"
        jump_counter += 1
    return result


def add_jump_points(quantity):
    jump = []
    to = []
    for _ in range(0, quantity):
        jump_points.append(-1)
        number = str(len(jump_points) - 1)
        jump.append("@JUMP" + number + "@")
        to.append("@TO" + number + "@")
    return to, jump
