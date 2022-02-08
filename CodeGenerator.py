import ply.yacc as yacc
from MemoryManager import MemoryManager
from Lekser import tokens
from JumpManager import clear_output, add_jump_points

storage = MemoryManager()


def p_program(p):
    """program : VAR declarations BEGIN commands END"""
    p[0] = clear_output(p[4] + "HALT")


def p_program_no_vars(p):
    """program : BEGIN commands END"""
    p[0] = clear_output(p[2] + "HALT")


def p_expression_value(p):
    """expression : value"""
    value, lineno = p[1], p.lineno(1)
    p[0] = load_var_to_register(value, "a", lineno)


def p_value_number(p):
    """value : NUMBER"""
    p[0] = ("num", p[1])


def p_value_identifier(p):
    """value : identifier"""
    p[0] = (p[1])


def p_identifier_id(p):
    """identifier : ID"""
    p[0] = ("id", p[1])


def p_identifier_tab_id(p):
    """identifier : ID PAREN_OPEN ID PAREN_CLOSE"""
    p[0] = ("tab", p[1], ("id", p[3]))


def p_identifier(p):
    """identifier : ID PAREN_OPEN NUMBER PAREN_CLOSE"""
    p[0] = ("tab", p[1], ("num", p[3]))


def p_declarations_variable(p):
    """declarations	: declarations COMMA ID"""
    id, lineno = p[3], p.lineno(3)
    storage.add_variable(id, lineno)


def p_declarations_array(p):
    """declarations	: declarations COMMA ID PAREN_OPEN NUMBER COLON NUMBER PAREN_CLOSE"""
    id, begin, end, lineno = p[3], p[5], p[7], p.lineno(3)
    storage.add_array(id, begin, end, lineno)


def p_declarations_last_variable(p):
    """declarations	: ID"""
    id, lineno = p[1], p.lineno(1)
    storage.add_variable(id, lineno)


def p_declarations_last_array(p):
    """declarations	: ID PAREN_OPEN NUMBER COLON NUMBER PAREN_CLOSE"""
    id, begin, end, lineno = p[1], p[3], p[5], p.lineno(1)
    storage.add_array(id, begin, end, lineno)


def p_declarations_empty(p):
    """declarations : """


def p_commands_mult(p):
    """commands : commands command"""
    p[0] = p[1] + p[2]


def p_commands_one(p):
    """commands	: command"""
    p[0] = p[1]


def p_command_assign(p):
    """command : identifier ASSIGN expression SEMICOLON"""
    identifier, expression, lineno = p[1], p[3], p.lineno(1)
    storage.check_iterator_modification(identifier[1], str(lineno))
    p[0] = expression + "SWAP g\n" + var_address_to_register(identifier, lineno, "b") + "SWAP g\n" + "STORE b\n"
    storage.inits[identifier[1]] = True


def p_command_input(p):
    """command : READ identifier SEMICOLON"""
    identifier, lineno = p[2], p.lineno(1)
    storage.inits[identifier[1]] = True
    p[0] = var_address_to_register(identifier, lineno, "b") + "GET\n" + "STORE b\n"


def p_command_output(p):
    """command : WRITE value SEMICOLON"""
    value, lineno = p[2], p.lineno(1)
    if value[0] == "num":
        p[0] = load_var_to_register(value, "a", lineno) + "PUT\n"
    else:
        storage.check_variable_initialization(value[1], str(lineno))
        p[0] = var_address_to_register(value, lineno, "b") + "LOAD b\n" + "PUT\n"


def p_expression_plus(p):
    """expression : value PLUS value"""
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = add(value1, value2, lineno)


def p_expression_minus(p):
    """expression : value MINUS value"""
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = sub(value1, value2, lineno)


def p_expression_mult(p):
    """expression : value MULT value"""
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = multiply(value1, value2, lineno)


def p_expression_div(p):
    """expression : value DIV value"""
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = divide(value1, value2, lineno)


def p_expression_mod(p):
    """expression : value MOD value"""
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = modulo(value1, value2, lineno)


def p_iterator(p):
    """iterator	: ID"""
    id, lineno = p[1], p.lineno(1)
    p[0] = id
    storage.add_variable(id, lineno)
    storage.inits[id] = True
    storage.iterators[id] = True


def p_command_for_to(p):
    """command : FOR iterator FROM value TO value DO commands ENDFOR"""
    iterator, begin, end, code, lineno = p[2], p[4], p[6], p[8], p.lineno(1)
    storage.check_loop_errors(begin[1], end[1], iterator, lineno)
    p[0] = for_loop(iterator, begin, end, code, lineno)
    storage.delete_variable(iterator)


def p_command_for_downto(p):
    """command : FOR iterator FROM value DOWNTO value DO commands ENDFOR"""
    iterator, begin, end, code, lineno = p[2], p[4], p[6], p[8], p.lineno(1)
    storage.check_loop_errors(begin[1], end[1], iterator, lineno)
    p[0] = for_loop_desc(iterator, begin, end, code, lineno)
    storage.delete_variable(iterator)


def p_command_while(p):
    """command : WHILE condition DO commands ENDWHILE"""
    condition, code, lineno = p[2], p[4], p.lineno(1)
    p[0] = while_loop(condition, code)


def p_command_if(p):
    """command : IF condition THEN commands ENDIF"""
    condition, if_command, lineno = p[2], p[4], p.lineno(1)
    p[0] = condition[0] + if_command + condition[1]


def p_command_if_else(p):
    """command : IF condition THEN commands ELSE commands ENDIF"""
    condition, if_command, else_command, lineno = p[2], p[4], p[6], p.lineno(1)
    labels, jumps = add_jump_points(1)
    p[0] = condition[0] + if_command + "JUMP " + jumps[0] + "\n" + condition[1] + else_command + "" + labels[0]


def p_condition_repeat_equal(p):
    """command : REPEAT commands UNTIL value EQUALS value SEMICOLON"""
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = not_equal(value1, value2, lineno)
    labels, jumps = add_jump_points(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_repeat_not_equal(p):
    """command : REPEAT commands UNTIL value NEQUALS value SEMICOLON"""
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = equal(value1, value2, lineno)
    labels, jumps = add_jump_points(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_repeat_less(p):
    """command : REPEAT commands UNTIL value LESS value SEMICOLON"""
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = greater_or_equal(value1, value2, lineno)
    labels, jumps = add_jump_points(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_repeat_greater(p):
    """command : REPEAT commands UNTIL value GREATER value SEMICOLON"""
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = less_or_equal(value1, value2, lineno)
    labels, jumps = add_jump_points(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_repeat_less_or_equal(p):
    """command : REPEAT commands UNTIL value LESSEQ value SEMICOLON"""
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = greater(value1, value2, lineno)
    labels, jumps = add_jump_points(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_repeat_greater_or_equal(p):
    """command : REPEAT commands UNTIL value GREATEREQ value SEMICOLON"""
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = less(value1, value2, lineno)
    labels, jumps = add_jump_points(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_equals(p):
    """condition : value EQUALS value"""
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = equal(value1, value2, lineno)


def p_condition_not_equals(p):
    """condition : value NEQUALS value"""
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = not_equal(value1, value2, lineno)


def p_condition_less(p):
    """condition : value LESS value"""
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = less(value1, value2, lineno)


def p_condition_greater(p):
    """condition : value GREATER value"""
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = greater(value1, value2, lineno)


def p_condition_less_or_equal(p):
    """condition : value LESSEQ value"""
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = less_or_equal(value1, value2, lineno)


def p_condition_greater_or_equal(p):
    """condition : value GREATEREQ value"""
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = greater_or_equal(value1, value2, lineno)


def load_var_to_register(value, register, lineno):
    lineno = str(lineno)
    if value[0] == "num":
        return generate_number(value[1], register)
    if value[0] == "id":
        storage.check_variable_initialization(value[1], lineno)
    if register != 'a':
        return var_address_to_register(value, lineno, "b") + "LOAD b" + "\n" + "SWAP " + register + "\n"
    else:
        return var_address_to_register(value, lineno, "b") + "LOAD b" + "\n"


def generate_number(value, register):
    output = ""
    if value >= 0:
        while value != 0:
            if value % 2 != 0:
                output = "INC a" + "\n" + output
                value = value - 1
            else:
                output = "SHIFT h " + "\n" + output
                value = value // 2
    else:
        while value != 0:
            if value % 2 != 0:
                output = "DEC a" + "\n" + output
                value = value + 1
            else:
                output = "SHIFT h" + "\n" + output
                value = value // 2

    output = "RESET h" + "\n" + "INC h" + "\n" + "RESET a" + "\n" + output
    if register != "a":
        output += "SWAP " + register + "\n"
    return output


def var_address_to_register(value, lineno, register):
    lineno = str(lineno)
    if value[0] == "id":
        storage.check_variable_address(value[1], lineno)
        return generate_number(storage.variables[value[1]], register)
    elif value[0] == "tab":
        storage.check_array_address(value[1], lineno)
        index, begin, _ = storage.arrays[value[1]]
        return load_var_to_register(value[2], register, lineno) + \
            generate_number(begin, "c") + \
            "SWAP " + register + "\n" + \
            "SUB c" + "\n" + \
            "SWAP " + register + "\n" + \
            generate_number(index, "c") + \
            "SWAP " + register + "\n" + \
            "ADD c" + "\n" + \
            "SWAP " + register + "\n"


def add(value1, value2, lineno):
    return load_var_to_register(value2, "d", lineno) + load_var_to_register(value1, "a", lineno) + "ADD d\n"


def sub(value1, value2, lineno):
    return load_var_to_register(value2, "d", lineno) + load_var_to_register(value1, "a", lineno) + "SUB d\n"


def multiply(value1, value2, lineno):
    return load_var_to_register(value1, "d", lineno) + \
        load_var_to_register(value2, "a", lineno) + \
        "JNEG 32\n" + \
        "RESET h\n" + \
        "RESET g\n" + \
        "INC h\n" + \
        "DEC g\n" + \
        "RESET c\n" + \
        "JZERO 24\n" + \
        "SWAP b\n" + \
        "RESET a\n" + \
        "ADD b\n" + \
        "SHIFT g\n" + \
        "SHIFT h\n" + \
        "SUB b\n" + \
        "JPOS 8\n" + \
        "JNEG 7\n" + \
        "SWAP d\n" + \
        "SHIFT h\n" + \
        "SWAP d\n" + \
        "SWAP b\n" + \
        "SHIFT g\n" + \
        "JUMP -14\n" + \
        "SWAP c\n" + \
        "ADD d\n" + \
        "SWAP c\n" + \
        "SWAP d\n" + \
        "SHIFT h\n" + \
        "SWAP d\n" + \
        "SWAP b\n" + \
        "SHIFT g\n" + \
        "JUMP -23\n" + \
        "SWAP c\n" + \
        "JUMP 13\n" + \
        "SWAP d\n" + \
        "JPOS -32\n" + \
        "JZERO 10\n" + \
        "SWAP b\n" + \
        "RESET a\n" + \
        "SUB b\n" + \
        "SWAP b\n" + \
        "RESET a\n" + \
        "SUB d\n" + \
        "SWAP d\n" + \
        "SWAP b\n" + \
        "JUMP -42\n"


def divide(value1, value2, lineno):
    return load_var_to_register(value1, "d", lineno) + \
        load_var_to_register(value2, "a", lineno) + \
        "RESET f\n" + \
        "RESET h\n" + \
        "INC h\n" + \
        "RESET g\n" + \
        "DEC g\n" + \
        "SWAP d\n" + \
        "JZERO 67\n" + \
        "JNEG 50\n" + \
        "SWAP d\n" + \
        "JZERO 64\n" + \
        "JNEG 42\n" + \
        "RESET c\n" + \
        "INC c\n" + \
        "SWAP b\n" + \
        "RESET a\n" + \
        "ADD d\n" + \
        "SUB b\n" + \
        "JZERO 9\n" + \
        "JNEG 8\n" + \
        "SWAP b\n" + \
        "SHIFT h\n" + \
        "SWAP b\n" + \
        "SWAP c\n" + \
        "SHIFT h\n" + \
        "SWAP c\n" + \
        "JUMP -11\n" + \
        "RESET a\n" + \
        "ADD d\n" + \
        "SWAP e\n" + \
        "RESET d\n" + \
        "RESET a\n" + \
        "ADD b\n" + \
        "SUB e\n" + \
        "JZERO 3\n" + \
        "JNEG 2\n" + \
        "JUMP 7\n" + \
        "SWAP e\n" + \
        "SUB b\n" + \
        "SWAP e\n" + \
        "SWAP d\n" + \
        "ADD c\n" + \
        "SWAP d\n" + \
        "SWAP b\n" + \
        "SHIFT g\n" + \
        "SWAP b\n" + \
        "SWAP c\n" + \
        "SHIFT g\n" + \
        "JZERO 3\n" + \
        "SWAP c\n" + \
        "JUMP -19\n" + \
        "SWAP d\n" + \
        "JUMP 12\n" + \
        "INC f\n" + \
        "SWAP c\n" + \
        "RESET a\n" + \
        "SUB c\n" + \
        "JUMP -45\n" + \
        "DEC f\n" + \
        "SWAP e\n" + \
        "RESET a\n" + \
        "SUB e\n" + \
        "SWAP d\n" + \
        "JUMP -53\n" + \
        "SWAP f\n" + \
        "JZERO 8\n" + \
        "RESET a\n" + \
        "SUB f\n" + \
        "SWAP e\n" + \
        "JZERO 2\n" + \
        "DEC e\n" + \
        "SWAP e\n" + \
        "JUMP 2\n" + \
        "SWAP f\n"


def modulo(value1, value2, lineno):
    return load_var_to_register(value1, "d", lineno) + \
        load_var_to_register(value2, "a", lineno) + \
        "SWAP g\n" + \
        "RESET a\n" + \
        "ADD g\n" + \
        "RESET f\n" + \
        "RESET h\n" + \
        "INC h\n" + \
        "SWAP d\n" + \
        "JZERO 75\n" + \
        "JNEG 53\n" + \
        "SWAP d\n" + \
        "JZERO 72\n" + \
        "JNEG 44\n" + \
        "RESET c\n" + \
        "INC c\n" + \
        "SWAP b\n" + \
        "RESET a\n" + \
        "ADD d\n" + \
        "SUB b\n" + \
        "JZERO 9\n" + \
        "JNEG 8\n" + \
        "SWAP b\n" + \
        "SHIFT h\n" + \
        "SWAP b\n" + \
        "SWAP c\n" + \
        "SHIFT h\n" + \
        "SWAP c\n" + \
        "JUMP -11\n" + \
        "RESET h\n" + \
        "DEC h\n" + \
        "RESET a\n" + \
        "ADD d\n" + \
        "SWAP e\n" + \
        "RESET d\n" + \
        "RESET a\n" + \
        "ADD b\n" + \
        "SUB e\n" + \
        "JZERO 3\n" + \
        "JNEG 2\n" + \
        "JUMP 7\n" + \
        "SWAP e\n" + \
        "SUB b\n" + \
        "SWAP e\n" + \
        "SWAP d\n" + \
        "ADD c\n" + \
        "SWAP d\n" + \
        "SWAP b\n" + \
        "SHIFT h\n" + \
        "SWAP b\n" + \
        "SWAP c\n" + \
        "SHIFT h\n" + \
        "JZERO 3\n" + \
        "SWAP c\n" + \
        "JUMP -19\n" + \
        "SWAP e\n" + \
        "JUMP 13\n" + \
        "DEC f\n" + \
        "DEC f\n" + \
        "SWAP c\n" + \
        "RESET a\n" + \
        "SUB c\n" + \
        "JUMP -48\n" + \
        "INC f\n" + \
        "SWAP e\n" + \
        "RESET a\n" + \
        "SUB e\n" + \
        "SWAP d\n" + \
        "JUMP -56\n" + \
        "SWAP f\n" + \
        "JZERO 13\n" + \
        "JNEG 4\n" + \
        "SWAP g\n" + \
        "SUB f\n" + \
        "JUMP 10\n" + \
        "INC a\n" + \
        "JZERO 4\n" + \
        "SWAP g\n" + \
        "ADD f\n" + \
        "JUMP 5\n" + \
        "RESET a\n" + \
        "SUB f\n" + \
        "JUMP 2\n" + \
        "SWAP f\n"


def equal(value1, value2, lineno):
    to, jump = add_jump_points(2)
    return load_var_to_register(value2, "d", lineno) + \
        load_var_to_register(value1, "a", lineno) + \
        "SUB d\n" + \
        "JPOS " + jump[1] + "\n" + \
        "JNEG " + jump[1] + "\n" + \
        "" + to[0], to[1] + ""


def not_equal(value1, value2, lineno):
    to, jump = add_jump_points(1)
    return load_var_to_register(value2, "d", lineno) + \
        load_var_to_register(value1, "a", lineno) + \
        "SUB d\n" + \
        "JZERO " + jump[0] + "\n" + \
        "", to[0]


def less(value1, value2, lineno):
    to, jump = add_jump_points(2)
    return load_var_to_register(value2, "d", lineno) + \
        load_var_to_register(value1, "a", lineno) + \
        "SUB d\n" + \
        "JZERO " + jump[1] + "\n" + \
        "JPOS " + jump[1] + "\n" + \
        "" + to[0], to[1] + ""


def greater(value1, value2, lineno):
    to, jump = add_jump_points(2)
    return load_var_to_register(value2, "d", lineno) + \
        load_var_to_register(value1, "a", lineno) + \
        "SUB d\n" + \
        "JZERO " + jump[1] + "\n" + \
        "JNEG " + jump[1] + "\n" + \
        "" + to[0], to[1] + ""


def less_or_equal(value1, value2, lineno):
    to, jump = add_jump_points(1)
    return load_var_to_register(value2, "d", lineno) + \
        load_var_to_register(value1, "a", lineno) + \
        "SUB d\n" + \
        "JPOS " + jump[0] + "\n" + \
        "", to[0]


def greater_or_equal(value1, value2, lineno):
    to, jump = add_jump_points(1)
    return load_var_to_register(value2, "d", lineno) + \
        load_var_to_register(value1, "a", lineno) + \
        "SUB d\n" + \
        "JNEG " + jump[0] + "\n" + \
        "", to[0]


def for_loop(iterator, begin, end, code, lineno):
    to, jump = add_jump_points(3)
    temp = storage.add_temporary_variable()
    temp_value = ("id", temp)
    it = ("id", iterator)
    return load_var_to_register(end, "e", lineno) + \
        var_address_to_register(temp_value, lineno, "b") + \
        "SWAP e\n" + \
        "STORE b\n" + \
        load_var_to_register(begin, "f", lineno) + \
        var_address_to_register(it, lineno, "b") + \
        "SWAP f\n" + \
        "STORE b\n" + \
        to[2] + \
        load_var_to_register(temp_value, "e", lineno) + \
        load_var_to_register(it, "a", lineno) + \
        "SUB e\n" + \
        "JZERO " + jump[0] + "\n" + \
        "JNEG " + jump[0] + "\n" + \
        "JUMP " + jump[1] + "\n" + \
        to[0] + code + \
        load_var_to_register(it, "f", lineno) + \
        "INC f\n" + \
        var_address_to_register(it, lineno, "b") + \
        "SWAP f\n" + \
        "STORE b\n" + \
        "JUMP " + jump[2] + "\n" + to[1]


def for_loop_desc(iterator, begin, end, code, lineno):
    to, jump = add_jump_points(3)
    temp = storage.add_temporary_variable()
    temp_value = ("id", temp)
    it = ("id", iterator)
    return load_var_to_register(end, "e", lineno) + \
        var_address_to_register(temp_value, lineno, "b") + \
        "SWAP e\n" + \
        "STORE b\n" + \
        load_var_to_register(begin, "f", lineno) + \
        var_address_to_register(it, lineno, "b") + \
        "SWAP f\n" + \
        "STORE b\n" + \
        to[2] + \
        load_var_to_register(temp_value, "e", lineno) + \
        load_var_to_register(it, "a", lineno) + \
        "SUB e\n" + \
        "JZERO " + jump[0] + "\n" + \
        "JPOS " + jump[0] + "\n" + \
        "JUMP " + jump[1] + "\n" + \
        to[0] + code + \
        load_var_to_register(it, "f", lineno) + \
        "DEC f\n" + \
        var_address_to_register(it, lineno, "b") + \
        "SWAP f\n" + \
        "STORE b\n" + \
        "JUMP " + jump[2] + "\n" + to[1]


def while_loop(condition, code):
    labels, jumps = add_jump_points(1)
    return "" + labels[0] + condition[0] + code + "JUMP " + jumps[0] + "\n" + condition[1] + ""


parser = yacc.yacc()
