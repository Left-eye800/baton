"""主窗口
主窗口由文件树、问题表格、预览表格组成
本程序支持问题排序、移动、支持预览,用户可以自行扩展题库
用户可以根据喜好设置表格颜色、字体,另外在导出word文档时可以设置word文档
更多细节可以参考帮助文档

the statistics of this file:
lines(count)    understand_level(h/m/l)    classes(count)    functions(count)    fields(count)
000000000878    ----------------------h    00000000000001    0000000000000000    ~~~~~~~~~~~~~
"""

import sys
import os
import json

from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QFrame, QSplitter,
                             QHBoxLayout, QLabel, QVBoxLayout, QTreeWidget, QFontDialog,
                             QPushButton, QFileDialog, QTableWidget, QWidget, QMessageBox,
                             QInputDialog, QLineEdit, QDialog, QColorDialog, QListWidget,
                             QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from docx.shared import Pt

from mainwindow import Ui_MainWindow
from file_tree import FileTree
from question_and_preview_widget import QuestionPreview
from undo_model import UndoList
from write_docx import write_in_docx
from generate_json import write_in_json_file
from about import read_about

__author__ = '与C同行'


class MainApp(QMainWindow, Ui_MainWindow):
    status_message_stop_time = 10000
    question_preview_table_font = QFont('Times new Roman', 12)
    undo_remember_count = 3
    docx_paragraph_space_after = Pt(10)
    doc_font_name = 'Times New Roman'
    doc_font_size = Pt(12)
    option_length = 70
    table_border_color = '#000000'

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        self.action_exit.triggered.connect(self.close)

        # 将不能立马使用的操作弃用
        self.action_read_or_write.setEnabled(False)
        self.action_save_remark.setEnabled(False)
        self.action_save_as_docx.setEnabled(False)
        self.action_redo.setEnabled(False)
        self.action_undo.setEnabled(False)
        self.action_close_json_file.setEnabled(False)
        self.action_recover_no_select.setEnabled(False)
        self.action_save_json.setEnabled(False)

        # 判断有没有最近打开文件
        try:
            with open('recent_open.json', 'r', encoding='utf8') as f:
                recent_files = json.load(f)
                if isinstance(recent_files, list):
                    pass
                else:
                    raise ValueError
                if recent_files:
                    self.action_open_recent.setEnabled(True)
                    self.recent_files = recent_files
                else:
                    self.action_open_recent.setEnabled(False)
        except:
            self.action_open_recent.setEnabled(False)
            with open('recent_open.json', 'w', encoding='utf8') as f:
                json.dump([], f)

        # 绑定方法
        self.action_open.triggered.connect(self.open)
        self.action_question_font.triggered.connect(self.question_font)
        self.action_undo.triggered.connect(self.undo_action)
        self.action_redo.triggered.connect(self.redo_action)
        self.action_undo_count.triggered.connect(self.set_undo_count)
        self.action_read_or_write.triggered.connect(self.transfer_write_or_read)
        self.action_save_remark.triggered.connect(self.save_remark)
        self.action_save_as_docx.triggered.connect(self.save_as_docx)
        self.action_docx_font_name.triggered.connect(self.set_docx_font_name)
        self.action_docx_font_size.triggered.connect(self.set_docx_font_size)
        self.action_docx_paragraph_space_after.triggered.connect(self.set_paragraph_space_after)
        self.action_docx_option_length.triggered.connect(self.set_options_length)
        self.action_generate_json_file.triggered.connect(self.generate_json_file)
        self.action_close_json_file.triggered.connect(self.close_json_file)
        self.action_table_border_color.triggered.connect(self.set_table_border_color)
        self.action_recover_no_select.triggered.connect(self.recover_no_select)
        self.action_save_json.triggered.connect(self.save_json_file)
        self.action_about.triggered.connect(self.about)
        self.action_open_recent.triggered.connect(self.recent_open)
        self.action_help_file.triggered.connect(self.help_pdf)

        # 创建树、问题、预览窗体
        self.tree_frame = QFrame()
        self.tree_frame.setFrameShape(QFrame.StyledPanel)
        self.question_frame = QFrame()
        self.question_frame.setFrameShape(QFrame.StyledPanel)
        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.StyledPanel)

        # 添加树
        tree_v_box = QVBoxLayout()
        tree_label = QLabel('json文件')
        tree_v_box.addWidget(tree_label, alignment=Qt.AlignLeft|Qt.AlignTop)
        json_file_tree = FileTree(QTreeWidget())
        self.tree = json_file_tree.give_tree()
        self.tree.clicked.connect(self.show_tree_message)
        self.tree.doubleClicked.connect(self.tree_open_file)
        tree_v_box.addWidget(self.tree)
        self.tree_frame.setLayout(tree_v_box)
        self.tree_frame.setMinimumWidth(70)

        # 添加问题
        self.question_frame.setMinimumWidth(200)
        self.undo_list = UndoList(self.undo_remember_count)

        # 添加预览
        self.preview_frame.setMinimumWidth(150)

        # 视图绑定
        self.action_only_question.triggered.connect(self.question_only)
        self.action_question_preview.triggered.connect(self.question_preview)
        self.action_tree_question_preview.triggered.connect(self.tree_question_preview)

        # 添加分割窗口
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setFrameStyle(3)
        self.splitter.addWidget(self.tree_frame)
        self.splitter.addWidget(self.question_frame)
        self.splitter.addWidget(self.preview_frame)
        h_box = QHBoxLayout(self.centralwidget)
        h_box.addWidget(self.splitter)

        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        origin_x = int((screen.width() - size.width()) / 2)
        origin_y = int((screen.height() - size.height()) / 2)
        self.move(origin_x, origin_y)

    def recent_open(self):
        def open_recent_json_file():
            item = list_widget.currentItem()
            try:
                self.open_json_file(item.text(), is_recent_open=True)
            except:
                with open('recent_open.json', 'w', encoding='utf8') as f:
                    json.dump([], f)
                self.action_open_recent.setEnabled(False)
                QMessageBox.warning(self, '打开文件', f'{item.text()}文件已经被修改或者不存在',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                self.statusbar.showMessage(f'{item.text()}文件已经被修改或者不存在', self.status_message_stop_time)
            dialog.close()

        dialog = QDialog()
        list_widget = QListWidget(dialog)
        recent_files = self.recent_files.copy()
        recent_files.reverse()
        list_widget.addItems(recent_files)
        list_widget.itemDoubleClicked.connect(open_recent_json_file)
        dialog.setWindowTitle('双击文件打开')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setFixedSize(300, 100)
        dialog.exec_()

    def set_table_border_color(self):
        color = QColorDialog.getColor()
        MainApp.table_border_color = color.name()
        if hasattr(self, 'question_table'):
            self.setStyleSheet(f'QTableWidget::item{{border:1px solid {self.table_border_color}}}')
            self.question_table.resizeRowsToContents()
            self.preveiw_table.resizeRowsToContents()

    def close_json_file(self):
        button = QMessageBox.warning(self, '关闭json文件', '确定关闭文件吗？', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)
        if button == QMessageBox.Yes:
            self.question_frame.deleteLater()
            self.preview_frame.deleteLater()
            self.question_frame = QFrame()
            self.question_frame.setFrameShape(QFrame.StyledPanel)
            self.preview_frame = QFrame()
            self.preview_frame.setFrameShape(QFrame.StyledPanel)
            self.splitter.addWidget(self.question_frame)
            self.splitter.addWidget(self.preview_frame)
            self.action_save_as_docx.setEnabled(False)
            self.action_save_remark.setEnabled(False)
            self.action_undo.setEnabled(False)
            self.action_redo.setEnabled(False)
            self.action_read_or_write.setEnabled(False)
            self.action_recover_no_select.setEnabled(False)
            self.action_save_json.setEnabled(False)
            self.action_close_json_file.setEnabled(False)
            self.action_read_or_write.setText('只读')
            self.action_read_or_write.setIcon(QIcon(r'icons\file_unlock.gif'))
            self.statusbar.showMessage('关闭json文件', self.status_message_stop_time)
            try:
                with open('recent_open.json', 'r', encoding='utf8') as f:
                    recent_files = json.load(f)
                    if recent_files:
                        self.action_open_recent.setEnabled(True)
                        self.recent_files = recent_files.copy()
                    else:
                        self.action_open_recent.setEnabled(False)
            except:
                self.action_open_recent.setEnabled(False)
                with open('recent_open.json', 'w', encoding='utf8') as f:
                    json.dump([], f)

    def generate_json_file(self):
        def choose_txt_filename():
            txt_filename, ok = QFileDialog.getOpenFileName(self, '选择文本文件', r'source_files\text_source',
                                                           'All files(*.txt)')
            if ok:
                txt_edit_text.setText(txt_filename)

        def click_ok():
            txt_filename = txt_edit_text.text()
            try:
                write_in_json_file(txt_filename)
            except:
                self.statusbar.showMessage('生成json文件失败', self.status_message_stop_time)
            dialog.close()
            QMessageBox.information(self, '生成json文件', '成功生成json文件', QMessageBox.Yes|QMessageBox.No,
                                QMessageBox.Yes)
            self.statusbar.showMessage('成功生成json文件', self.status_message_stop_time)

        def click_cancel():
            dialog.close()
            self.statusbar.showMessage('取消生成json文件', self.status_message_stop_time)

        dialog = QDialog()
        widget = QWidget(dialog)
        v_box = QVBoxLayout()
        h_box_1 = QHBoxLayout()
        h_box_2 = QHBoxLayout()
        label1 = QLabel('文本文件')
        txt_edit_text = QLineEdit()
        txt_button = QPushButton('...')
        txt_button.setFixedSize(30, 20)
        ok_button = QPushButton('确认')
        cancel_button = QPushButton('取消')
        txt_button.clicked.connect(choose_txt_filename)
        ok_button.clicked.connect(click_ok)
        cancel_button.clicked.connect(click_cancel)
        h_box_1.addWidget(label1)
        h_box_1.addWidget(txt_edit_text)
        h_box_1.addWidget(txt_button)
        h_box_2.addStretch()
        h_box_2.addWidget(ok_button)
        h_box_2.addWidget(cancel_button)
        v_box.addLayout(h_box_1)
        v_box.addLayout(h_box_2)
        widget.setLayout(v_box)
        dialog.setWindowTitle('生成json文件')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setFixedSize(250, 65)
        dialog.exec_()

    # docx文件事件
    # region
    def set_docx_font_name(self):
        items = ['Times New Roman', '宋体', '仿宋', '楷体', '隶书']
        item, ok = QInputDialog.getItem(self, '设置docx文件字体名', '字体名列表', items, 0, False)
        if ok:
            MainApp.doc_font_name = item

    def set_docx_font_size(self):
        number, ok = QInputDialog.getInt(self, '设置docx文件字体大小', '字体大小', 12, 6, 40)
        if ok:
            MainApp.doc_font_size = Pt(number)

    def set_paragraph_space_after(self):
        number, ok = QInputDialog.getInt(self, '设置docx段落间距', '段落间距', 10, 0, 30)
        if ok:
            MainApp.docx_paragraph_space_after = Pt(number)

    def set_options_length(self):
        number, ok = QInputDialog.getInt(self, '设置选择题选项长度', '选项长度', 70, 20, 200)
        if ok:
            MainApp.option_length = number

    def save_as_docx(self):
        docx_filename, ok = QFileDialog.getSaveFileName(self, '保存的docx文件', './', 'All files(*)')
        if ok:
            if docx_filename.endswith('.docx'):
                pass
            else:
                docx_filename += '.docx'
            save_json_dict = {}
            for i in range(len(self.question_list)):
                save_json_dict[str(i+1)] = self.json_dict[str(self.question_list[i])]
            write_in_docx(save_json_dict, docx_filename, self.docx_paragraph_space_after,
                          self.doc_font_name, self.doc_font_size, self.option_length)
            QMessageBox.information(self, '另存为docx文件', f'成功保存文件,文件路径:{docx_filename}',
                                    QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
            self.statusbar.showMessage(f'将文件另存在{docx_filename}', self.status_message_stop_time)
        else:
            QMessageBox.information(self, '另存为docx文件', '选择文件出现错误', QMessageBox.Yes|QMessageBox.No,
                                    QMessageBox.Yes)
            self.statusbar.showMessage('另存docx文件失败', self.status_message_stop_time)
    # endregion

    def closeEvent(self, a0) -> None:
        reply = QMessageBox.information(self, '关闭程序', '请确认关闭该程序',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            a0.accept()
        else:
            a0.ignore()

    # 文件树事件
    # region
    def show_tree_message(self, qmodelindex):
        item = self.tree.currentItem()
        item_text = item.text(0)
        self.statusbar.showMessage('当前路径/文件：'+item_text, self.status_message_stop_time)

    def tree_open_file(self, qmodelindex):
        item = self.tree.currentItem()
        item_text = item.text(0)
        if item_text.endswith('.json'):
            while True:
                parent = item.parent()
                if parent:
                    item_text = os.path.join(parent.text(0), item_text)
                    item = item.parent()
                else:
                    open_filename = os.path.join(r'source_files', item_text)
                    break
            try:
                self.open_json_file(open_filename)
            except:
                QMessageBox.critical(self, '打开json文件', '检查json文件内容是否正确',
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        else:
            QMessageBox.warning(self, '打开json文件', '您打开的不是文件或者不是json文件',
                                QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
    # endregion

    # 视图绑定事件
    # region
    def question_only(self):
        self.tree_frame.hide()
        self.question_frame.show()
        self.preview_frame.hide()

    def question_preview(self):
        self.tree_frame.hide()
        self.question_frame.show()
        self.preview_frame.show()

    def tree_question_preview(self):
        self.tree_frame.show()
        self.question_frame.show()
        self.preview_frame.show()
    # endregion

    def question_font(self):
        def set_child_font(table):
            table_length = table.rowCount()
            for i in range(table_length):
                cell_widget = table.cellWidget(i, 0)
                children = cell_widget.children()
                for child in children:
                    if isinstance(child, QVBoxLayout):
                        pass
                    else:
                        child.setFont(MainApp.question_preview_table_font)

        font, ok = QFontDialog.getFont()
        if ok:
            MainApp.question_preview_table_font = font
            if hasattr(self, 'question_table'):
                set_child_font(self.question_table)
                set_child_font(self.preveiw_table)
                self.question_table.resizeRowsToContents()
                self.preveiw_table.resizeRowsToContents()

    def open_json_file(self, json_filename, is_recent_open=False):
        question_and_preview = QuestionPreview(QTableWidget(), QTableWidget(), json_filename)
        self.question_frame.deleteLater()
        self.preview_frame.deleteLater()
        self.question_frame = QFrame()
        self.question_frame.setFrameShape(QFrame.StyledPanel)
        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.StyledPanel)
        self.splitter.addWidget(self.question_frame)
        self.splitter.addWidget(self.preview_frame)
        # 添加question_table
        self.question_table = question_and_preview.give_question_table()
        table_length = self.question_table.rowCount()
        for i in range(table_length):
            cell_widget = self.question_table.cellWidget(i, 0)
            children = cell_widget.children()
            for child in children:
                if isinstance(child, QVBoxLayout):
                    pass
                else:
                    child.setFont(self.question_preview_table_font)
        self.question_table.resizeRowsToContents()
        self.question_v_box = QVBoxLayout()
        _, only_json_filename = os.path.split(json_filename)
        self.statusbar.showMessage(f'成功打开json文件{only_json_filename}', self.status_message_stop_time)
        question_frame_head_label = QLabel(only_json_filename)
        self.question_v_box.addWidget(question_frame_head_label)
        self.question_v_box.addWidget(self.question_table)
        control_widget = QWidget()
        control_h_box = QHBoxLayout()
        control_h_box.addStretch(1)
        self.up_button = QPushButton()
        self.up_button.setIcon(QIcon(r'icons\arrow_up.ico'))
        self.down_button = QPushButton()
        self.down_button.setIcon(QIcon(r'icons\arrow_down.ico'))
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(r'icons\Delete.ico'))
        control_h_box.addWidget(self.up_button)
        control_h_box.addWidget(self.down_button)
        control_h_box.addWidget(self.delete_button)
        control_h_box.setSpacing(10)
        control_widget.setLayout(control_h_box)
        self.question_v_box.addWidget(control_widget)
        self.question_frame.setLayout(self.question_v_box)
        # 添加preview_table
        self.preveiw_table = question_and_preview.give_preview_table()
        table_length = self.preveiw_table.rowCount()
        for i in range(table_length):
            cell_widget = self.preveiw_table.cellWidget(i, 0)
            children = cell_widget.children()
            for child in children:
                if isinstance(child, QVBoxLayout):
                    pass
                else:
                    child.setFont(self.question_preview_table_font)
        self.preveiw_table.resizeRowsToContents()
        preview_frame_head_label = QLabel('预览窗口')
        self.preview_v_box = QVBoxLayout()
        self.preview_v_box.addWidget(preview_frame_head_label)
        self.preview_v_box.addWidget(self.preveiw_table)
        self.preview_frame.setLayout(self.preview_v_box)
        # 设置表格样式
        self.setStyleSheet(f'QTableWidget::item{{border:1px solid {self.table_border_color}}}')
        self.question_table.resizeRowsToContents()
        self.preveiw_table.resizeRowsToContents()
        # splitter的最小宽度
        self.preview_frame.setMinimumWidth(150)
        self.question_frame.setMinimumWidth(200)
        # 绑定方法
        self.question_table.itemSelectionChanged.connect(self.selection_changed)
        self.preveiw_table.itemSelectionChanged.connect(self.disable_select)
        # 打开触发器
        self.action_save_remark.setEnabled(True)
        self.action_save_as_docx.setEnabled(True)
        self.action_read_or_write.setEnabled(True)
        self.action_close_json_file.setEnabled(True)
        self.action_recover_no_select.setEnabled(True)
        self.action_save_json.setEnabled(True)
        self.save_json_filename = None
        # 关闭触发器
        self.action_redo.setEnabled(False)
        self.action_undo.setEnabled(False)
        # 禁用按钮
        self.delete_button.setEnabled(False)
        self.up_button.setEnabled(False)
        self.down_button.setEnabled(False)
        # 按钮事件控制
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        self.delete_button.clicked.connect(self.delete_questions)
        # json字典
        self.json_dict = question_and_preview.give_json_dict()
        self.question_list = [i+1 for i in range(len(self.json_dict))]
        # 将文件写入json文件
        if not is_recent_open:
            with open('recent_open.json', 'r', encoding='utf8') as f:
                recent_files = json.load(f)
            if recent_files:
                self.recent_files = recent_files.copy()
                self.action_open_recent.setEnabled(True)
                if json_filename in recent_files:
                    pass
                else:
                    if len(recent_files) >= 5:
                        recent_files.append(json_filename)
                        for i in range(len(recent_files)-5):
                            recent_files.pop(0)
                    else:
                        recent_files.append(json_filename)
            else:
                self.action_open_recent.setEnabled(False)
                recent_files.append(json_filename)
            with open('recent_open.json', 'w', encoding='utf8') as f:
                json.dump(recent_files, f)

    def transfer_write_or_read(self):
        if self.action_read_or_write.text() == '只读':
            self.action_read_or_write.setText('可写')
            self.action_read_or_write.setIcon(QIcon(r'icons\file_lock.gif'))
            row_count = self.question_table.rowCount()
            for row in range(row_count):
                cell_widget = self.question_table.cellWidget(row, 0)
                children = cell_widget.children()
                for child in children:
                    if hasattr(child, 'is_remark'):
                        child.setReadOnly(True)
        elif self.action_read_or_write.text() == '可写':
            self.action_read_or_write.setText('只读')
            self.action_read_or_write.setIcon(QIcon(r'icons\file_unlock.gif'))
            row_count = self.question_table.rowCount()
            for row in range(row_count):
                cell_widget = self.question_table.cellWidget(row, 0)
                children = cell_widget.children()
                for child in children:
                    if hasattr(child, 'is_remark'):
                        child.setReadOnly(False)

    def save_json_file(self):
        save_json_dict = {}
        for i in range(len(self.question_list)):
            save_json_dict[str(i+1)] = self.json_dict[str(self.question_list[i])]
        if hasattr(self, 'save_json_filename') and self.save_json_filename:
            with open(self.save_json_filename, 'w', encoding='utf8') as f:
                json.dump(save_json_dict, f)
            QMessageBox.information(self, '保存json文件', f'成功将json字典保存在{self.save_json_filename}文件',
                                    QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
            self.statusbar.showMessage(f'成功将json字典保存在{self.save_json_filename}文件', self.status_message_stop_time)
        else:
            save_json_filename, ok = QFileDialog.getSaveFileName(self, '保存json文件', r'临时保存json',
                                                                 'all files(*.json)')
            if ok:
                if save_json_filename.endswith('.json'):
                    pass
                else:
                    save_json_filename += '.json'
                self.save_json_filename = save_json_filename
                with open(self.save_json_filename, 'w', encoding='utf8') as f:
                    json.dump(save_json_dict, f)
                QMessageBox.information(self, '保存json文件', f'成功将json字典保存在{self.save_json_filename}文件',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                self.statusbar.showMessage(f'成功将json字典保存在{self.save_json_filename}文件',
                                           self.status_message_stop_time)

    def save_remark(self):
        for i in range(len(self.question_list)):
            cell_widget = self.question_table.cellWidget(i, 0)
            if hasattr(cell_widget, 'is_tag'):
                pass
            else:
                children = cell_widget.children()
                remark = ''
                for child in children:
                    if hasattr(child, 'is_remark'):
                        remark = child.toPlainText()
                        remark = remark.strip()
                self.json_dict[str(self.question_list[i])]['content']['remark'] = remark
        QMessageBox.information(self, '保存备注', '成功将备注写入json字典', QMessageBox.Yes|QMessageBox.No,
                                QMessageBox.Yes)
        self.statusbar.showMessage('成功保存备注', self.status_message_stop_time)

    def set_buttons_enable(self, enable):
        self.up_button.setEnabled(enable)
        self.down_button.setEnabled(enable)
        self.delete_button.setEnabled(enable)

    def set_undo_redo_status(self):
        if self.undo_list.enable_undo():
            self.action_undo.setEnabled(True)
        else:
            self.action_undo.setEnabled(False)
        if self.undo_list.enable_redo():
            self.action_redo.setEnabled(True)
        else:
            self.action_redo.setEnabled(False)

    # 移动和删除
    # region
    def exchange_two_row(self, index, next_index):
        exchange_operate = 'exchange;'
        current_question_index = self.question_list[index]
        next_question_index = self.question_list[next_index]
        exchange_operate += f'{index},{next_index};{current_question_index},{next_question_index}'
        self.undo_list.add_operate(exchange_operate)
        self.question_list[index], self.question_list[next_index] = (
            self.question_list[next_index], self.question_list[index])
        remark_read = True if self.action_read_or_write.text() == '可写' else False
        question_cell_widget, preview_cell_widget = QuestionPreview.cell_widget(
            self.json_dict, next_question_index, remark_read)
        children = question_cell_widget.children()
        for child in children:
            if isinstance(child, QVBoxLayout):
                pass
            else:
                child.setFont(self.question_preview_table_font)
        children = preview_cell_widget.children()
        for child in children:
            if isinstance(child, QVBoxLayout):
                pass
            else:
                child.setFont(self.question_preview_table_font)
        self.question_table.removeRow(next_index)
        self.preveiw_table.removeRow(next_index)
        self.question_table.insertRow(index)
        self.preveiw_table.insertRow(index)
        self.question_table.setCellWidget(index, 0, question_cell_widget)
        self.preveiw_table.setCellWidget(index, 0, preview_cell_widget)
        self.question_table.resizeRowsToContents()
        self.preveiw_table.resizeRowsToContents()
        self.set_buttons_enable(False)
        self.statusbar.showMessage(f'成功交换第{index + 1}和第{next_index + 1}行', self.status_message_stop_time)

    def move_up(self):
        index = self.question_table.currentRow()
        previous_index = index-1
        self.exchange_two_row(previous_index, index)
        self.undo_list.redo_list.clear()
        self.set_undo_redo_status()
        cell_widget = self.question_table.cellWidget(index, 0)
        cell_widget.setStyleSheet('background-color:white')
        self.question_table.clearSelection()
        self.question_table.resizeRowsToContents()
        self.preveiw_table.resizeRowsToContents()

    def move_down(self):
        index = self.question_table.currentRow()
        next_index = index+1
        self.exchange_two_row(index, next_index)
        self.undo_list.redo_list.clear()
        self.set_undo_redo_status()
        cell_widget = self.question_table.cellWidget(next_index, 0)
        cell_widget.setStyleSheet('background-color:white')
        self.question_table.clearSelection()
        self.preveiw_table.resizeRowsToContents()
        self.question_table.resizeRowsToContents()

    def delete_rows(self, indexes):
        indexes_message_str = [str(i + 1) for i in indexes]
        indexes.reverse()
        question_indexes = []
        del_operate = 'del;'
        for index in indexes:
            question_index = self.question_list[index]
            question_indexes.append(question_index)
            self.question_table.removeRow(index)
            self.preveiw_table.removeRow(index)
            self.question_list.pop(index)
        indexes.reverse()
        indexes_str = [str(i) for i in indexes]
        question_indexes.reverse()
        question_indexes_str = [str(i) for i in question_indexes]
        del_operate += (','.join(indexes_str) + ';' + ','.join(question_indexes_str))
        self.undo_list.add_operate(del_operate)
        self.set_buttons_enable(False)
        self.statusbar.showMessage('成功删除' + ','.join(indexes_message_str) + '行', self.status_message_stop_time)

    def delete_questions(self):
        indexes = self.question_table.selectedIndexes()
        indexes = [i.row() for i in indexes]
        indexes.sort()
        self.delete_rows(indexes)
        self.undo_list.redo_list.clear()
        self.set_undo_redo_status()
        self.question_table.clearSelection()
        self.question_table.resizeRowsToContents()
        self.preveiw_table.resizeRowsToContents()
    # endregion

    # 撤销与重做
    # region
    def insert_rows(self, indexes, question_indexes):
        for index, question_index in list(zip(indexes, question_indexes)):
            remark_read = True if self.action_read_or_write.text() == '可写' else False
            question_cell_widget, preview_cell_widget = QuestionPreview.cell_widget(
                self.json_dict, question_index, remark_read)
            children = question_cell_widget.children()
            for child in children:
                if isinstance(child, QVBoxLayout):
                    pass
                else:
                    child.setFont(self.question_preview_table_font)
            children = preview_cell_widget.children()
            for child in children:
                if isinstance(child, QVBoxLayout):
                    pass
                else:
                    child.setFont(self.question_preview_table_font)
            self.question_table.insertRow(index)
            self.question_table.setCellWidget(index, 0, question_cell_widget)
            self.preveiw_table.insertRow(index)
            self.preveiw_table.setCellWidget(index, 0, preview_cell_widget)
            self.question_list.insert(index, question_index)
        indexes_message = [str(i+1) for i in indexes]
        message = ','.join(indexes_message)
        self.set_buttons_enable(False)
        self.statusbar.showMessage(f'恢复删除的第{message}行', self.status_message_stop_time)

    def undo_action(self):
        undo_operate = self.undo_list.give_undo_operate()
        if undo_operate.startswith('exchange'):
            indexes_str = undo_operate.split(';')[1]
            index_str, next_index_str = indexes_str.split(',')
            index, next_index = int(index_str), int(next_index_str)
            self.exchange_two_row(index, next_index)
            self.undo_list.undo_list.pop(-1)
        elif undo_operate.startswith('del'):
            _, indexes_str, question_indexes_str = undo_operate.split(';')
            indexes_str_list = indexes_str.split(',')
            indexes = [int(i) for i in indexes_str_list]
            question_indexes_str_list = question_indexes_str.split(',')
            question_indexes = [int(i) for i in question_indexes_str_list]
            self.insert_rows(indexes, question_indexes)
        self.set_buttons_enable(False)
        self.set_undo_redo_status()
        self.question_table.resizeRowsToContents()
        self.preveiw_table.resizeRowsToContents()

    def redo_action(self):
        redo_operate = self.undo_list.give_redo_operate()
        if redo_operate.startswith('exchange'):
            indexes_str = redo_operate.split(';')[1]
            index_str, next_index_str = indexes_str.split(',')
            index, next_index = int(index_str), int(next_index_str)
            self.exchange_two_row(index, next_index)
        if redo_operate.startswith('del'):
            _, indexes_str, _ = redo_operate.split(';')
            indexes_str_list = indexes_str.split(',')
            indexes = [int(i) for i in indexes_str_list]
            self.delete_rows(indexes)
        self.set_undo_redo_status()
        self.question_table.resizeRowsToContents()
        self.preveiw_table.resizeRowsToContents()
    # endregion

    def recover_no_select(self):
        for i in range(self.question_table.rowCount()):
            cell_widget = self.question_table.cellWidget(i, 0)
            cell_widget.setStyleSheet('background-color:white')
        self.question_table.clearSelection()
        self.set_buttons_enable(False)
        self.statusbar.showMessage('清除选中项', self.status_message_stop_time)

    def set_undo_count(self):
        num, ok = QInputDialog.getInt(self, '设置最大撤销次数', '设置最大撤销次数', value=3,
                                      max=20, min=0)
        if ok:
            MainApp.undo_remember_count = num
            self.undo_list.set_remember_count(self.undo_remember_count)
            self.undo_list.clear()
            self.set_undo_redo_status()
            self.statusbar.showMessage(f'将最大撤销次数设置为{num}次', self.status_message_stop_time)

    def selection_changed(self):
        indexes = self.question_table.selectedIndexes()
        if len(indexes) == 1:
            index = indexes[0]
            row_number = index.row()
            cell_widget = self.question_table.cellWidget(row_number, 0)
            try:
                cell_widget.setStyleSheet('background-color:lightblue')
            except:
                pass
            for i in range(self.question_table.rowCount()):
                if i != row_number:
                    other_cell_widget = self.question_table.cellWidget(i, 0)
                    try:
                        other_cell_widget.setStyleSheet('background-color:white')
                    except:
                        pass
            if hasattr(cell_widget, 'is_tag'):
                self.up_button.setEnabled(False)
                self.down_button.setEnabled(False)
                self.delete_button.setEnabled(False)
            elif row_number == self.question_table.rowCount()-1:
                self.down_button.setEnabled(False)
                self.up_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                self.statusbar.showMessage(f'选中第{row_number+1}行', self.status_message_stop_time)
            else:
                self.delete_button.setEnabled(True)
                previous_number = row_number-1
                previous_cell_widget = self.question_table.cellWidget(previous_number, 0)
                if hasattr(previous_cell_widget, 'is_tag'):
                    self.up_button.setEnabled(False)
                else:
                    self.up_button.setEnabled(True)
                next_number = row_number+1
                next_cell_widget = self.question_table.cellWidget(next_number, 0)
                if hasattr(next_cell_widget, 'is_tag'):
                    self.down_button.setEnabled(False)
                else:
                    self.down_button.setEnabled(True)
                self.statusbar.showMessage(f'选中第{row_number + 1}行', self.status_message_stop_time)
        elif len(indexes) > 1:
            self.down_button.setEnabled(False)
            self.up_button.setEnabled(False)
            enable_delete = True
            indexes_list = [i.row() for i in indexes]
            indexes_list.sort()
            for index in indexes:
                row_number = index.row()
                cell_widget = self.question_table.cellWidget(row_number, 0)
                if hasattr(cell_widget, 'is_tag'):
                    enable_delete = False
            if enable_delete:
                self.delete_button.setEnabled(True)
                indexes_list_str = [str(i + 1) for i in indexes_list]
                indexes_str = ','.join(indexes_list_str)
                self.statusbar.showMessage(f'选中第{indexes_str}行', self.status_message_stop_time)
            else:
                self.delete_button.setEnabled(False)
            for i in range(self.question_table.rowCount()):
                current_cell_widget = self.question_table.cellWidget(i, 0)
                if i in indexes_list:
                    try:
                        current_cell_widget.setStyleSheet('background-color:lightblue')
                    except:
                        pass
                else:
                    try:
                        current_cell_widget.setStyleSheet('background-color:white')
                    except:
                        pass

    def disable_select(self):
        self.preveiw_table.clearSelection()

    def open(self):
        json_filename, ok = QFileDialog.getOpenFileName(self, 'Open json_file',
                                                        r'.\source_files\json_source',
                                                        "All files (*.json)")
        try:
            self.open_json_file(json_filename)
        except:
            QMessageBox.critical(self, '打开json文件', '检查json文件内容是否正确',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def about(self):
        def ok_click():
            dialog.close()

        about_string = read_about('about.txt')
        dialog = QDialog()
        widget = QWidget(dialog)
        v_box = QVBoxLayout()
        h_box = QHBoxLayout()
        text_edit = QTextEdit()
        text_edit.setText(about_string)
        text_edit.setReadOnly(True)
        ok_button = QPushButton('确认')
        ok_button.clicked.connect(ok_click)
        v_box.addWidget(text_edit)
        h_box.addStretch()
        h_box.addWidget(ok_button)
        v_box.addLayout(h_box)
        widget.setLayout(v_box)
        dialog.setWindowTitle('关于')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setFixedSize(280, 240)
        dialog.exec_()

    def help_pdf(self):
        os.startfile(r'help.pdf')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
