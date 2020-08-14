"""创建json文件树

创建一个FileTree文件树,通过初始化满足文件树的条件,
通过give_tree方法返回包装好的树

the statistics of this file:
lines(count)    understand_level(h/m/l)    classes(count)    functions(count)    fields(count)
000000000048    ----------------------h    00000000000001    0000000000000000    ~~~~~~~~~~~~~
"""

import os

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QIcon

__author__ = '与C同行'


class FileTree:
    def __init__(self, tree: QTreeWidget):
        self.tree = tree
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        current_root = QTreeWidgetItem(self.tree)
        current_root.setText(0, 'json_source')
        current_root.setIcon(0, QIcon(r'icons\director.gif'))
        self.walk_file(r'source_files\json_source', current_root)

    def walk_file(self, dir_, current_root_para):
        filenames = os.listdir(dir_)
        for filename in filenames:
            full_path = os.path.join(dir_, filename)
            if os.path.isfile(full_path):
                current_child = QTreeWidgetItem(current_root_para)
                current_child.setText(0, filename)
                if filename.endswith('.json'):
                    current_child.setIcon(0, QIcon(r'icons\json_file.png'))
                else:
                    current_child.setIcon(0, QIcon(r'icons\unknow_file.gif'))
            else:
                new_dir = os.path.join(dir_, filename)
                current_root = QTreeWidgetItem(current_root_para)
                current_root.setText(0, filename)
                current_root.setIcon(0, QIcon(r'icons\director.gif'))
                self.walk_file(new_dir, current_root)

    def give_tree(self):
        return self.tree
