"""
模拟撤销过程生成一个undo_list和一个redo_list

the statistics of this file:
lines(count)    understand_level(h/m/l)    classes(count)    functions(count)    fields(count)
000000000052    ----------------------l    00000000000001    0000000000000000    ~~~~~~~~~~~~~
"""

__author__ = '与C同行'


class UndoList:
    def __init__(self, remember_count):
        self.remember_count = remember_count
        self.undo_list = []
        self.redo_list = []

    def check_undo_length(self):
        if len(self.undo_list) == self.remember_count+1:
            del self.undo_list[0]

    def add_operate(self, operation):
        self.undo_list.append(operation)
        self.check_undo_length()

    def give_undo_operate(self):
        undo_operation = self.undo_list.pop(-1)
        self.redo_list.append(undo_operation)
        return undo_operation

    def give_redo_operate(self):
        redo_operation = self.redo_list.pop(-1)
        return redo_operation

    def clear(self):
        self.undo_list.clear()
        self.redo_list.clear()

    def enable_undo(self):
        if self.undo_list:
            return True
        else:
            return False

    def enable_redo(self):
        if self.redo_list:
            return True
        else:
            return False

    def set_remember_count(self, count):
        self.remember_count = count
