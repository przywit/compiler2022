class MemoryManager:
    inits = {}
    arrays = {}
    variables = {}
    iterators = {}
    memory = 1

    def __init__(self):
        pass

    def check_variable_initialization(self, id, lineno):
        if id not in self.inits:
            raise Exception('Błąd w linii ' + lineno + ": użycie niezainicjowanej zmiennej " + id)

    def check_variable_address(self, id, lineno):
        if id not in self.variables:
            if id in self.arrays:
                raise Exception('Błąd w linii ' + lineno + ": niewłaściwe użycie zmiennej tablicowej " + id)
            else:
                raise Exception('Błąd w linii ' + lineno + ": niezadeklarowana zmienna " + id)

    def check_array_address(self, id, lineno):
        if id not in self.arrays:
            if id in self.variables:
                raise Exception('Błąd w linii ' + lineno + ": niewłaściwe użycie zmiennej " + id)
            else:
                raise Exception('Błąd w linii ' + lineno + ": niewłaściwe zadeklarowanie tablicy " + id)

    def check_iterator_modification(self, id, lineno):
        if id in self.iterators:
            raise Exception('Błąd w linii ' + lineno + ": zabroniona modyfikacja iteratora " + id)

    def check_loop_errors(self, begin, end, iterator, lineno):
        if end == iterator:
            raise Exception('Błąd w linii ' + str(lineno)) + ": zmienna " + end + \
                  " jest niezainicjonowana o tej samej nazwie co iterator w pętli"
        if begin == iterator:
            raise Exception('Błąd w linii ' + str(lineno)) + ": zmienna " + begin + \
                  " jest niezainicjonowana o tej samej nazwie co iterator w pętli"

    def add_array(self, id, begin, end, lineno):
        lineno = str(lineno)
        if id in self.arrays:
            raise Exception('Błąd w linii ' + str(lineno) + ": druga deklaracja tablicy " + id)
        if begin > end:
            raise Exception('Błąd w linii ' + lineno + ": niewłaściwy zakres tablicy " + id)
        position = self.memory + 1
        self.arrays[id] = (position, begin, end)
        self.memory += (end - begin + 1)

    def add_variable(self, id, lineno):
        if id in self.variables:
            raise Exception('Błąd w linii ' + str(lineno) + ": druga deklaracja " + id)
        self.memory += 1
        self.variables[id] = self.memory

    def add_temporary_variable(self):
        tempo = "$T" + str(self.memory)
        self.add_variable(tempo, None)
        self.inits[tempo] = True
        return tempo

    def delete_variable(self, id):
        self.variables.pop(id)
