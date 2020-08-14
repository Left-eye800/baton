"""
生成question和preview表格

the statistics of this file:
lines(count)    understand_level(h/m/l)    classes(count)    functions(count)    fields(count)
000000000158    ----------------------m    00000000000001    0000000000000000    ~~~~~~~~~~~~~
"""

from PyQt5.QtWidgets import (QTableWidget, QAbstractItemView, QHeaderView,
                             QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit)
from PyQt5.QtGui import QPixmap

from generate_json import read_from_json_file

__author__ = '与C同行'


class QuestionPreview:
    def __init__(self, question_table: QTableWidget, preview_table: QTableWidget,
                 json_file):
        self.question_table = question_table
        self.preview_table = preview_table
        self.json_dict = read_from_json_file(json_file)
        self.text_edit_dict = {}
        json_dict_length = len(self.json_dict)
        self.question_table.setColumnCount(1)
        self.question_table.setRowCount(json_dict_length)
        self.question_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.question_table.horizontalHeader().setVisible(False)
        self.question_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.setColumnCount(1)
        self.preview_table.setRowCount(json_dict_length)
        self.preview_table.horizontalHeader().setVisible(False)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i in range(json_dict_length):
            question_widget, preview_widget = QuestionPreview.cell_widget(self.json_dict, i+1)
            self.question_table.setCellWidget(i, 0, question_widget)
            self.preview_table.setCellWidget(i, 0, preview_widget)

    @classmethod
    def cell_widget(cls, json_dict_para, i, is_readonly=False):
        def set_question(content_para, question_vbox_para, preview_vbox_para):
            question = content_para['question']
            if question['type'] == 'text':
                question_question_text = QTextEdit()
                preview_question_text = QTextEdit()
                question_question_text.setText(question['content'])
                preview_question_text.setText(question['content'])
                question_question_text.setReadOnly(True)
                preview_question_text.setReadOnly(True)
                question_question_text.setMaximumHeight(60)
                preview_question_text.setMaximumHeight(60)
                question_vbox_para.addWidget(question_question_text)
                preview_vbox_para.addWidget(preview_question_text)
            else:
                question_question_label = QLabel()
                preview_question_label = QLabel()
                question_question_label.setPixmap(QPixmap(question['src']))
                preview_question_label.setPixmap(QPixmap(question['src']))
                question_vbox_para.addWidget(question_question_label)
                preview_vbox_para.addWidget(preview_question_label)

        def set_attach(content_para, question_vbox_para):
            attach = content_para.get('attach')
            if attach:
                for attach_img_path in attach:
                    question_attach_label = QLabel()
                    question_attach_label.setPixmap(QPixmap(attach_img_path))
                    question_vbox_para.addWidget(question_attach_label)

        def set_remark(content_para, question_vbox_para):
            question_remark_label = QLabel('备注')
            question_vbox.addWidget(question_remark_label)
            question_edit_text = QTextEdit()
            setattr(question_edit_text, 'is_remark', True)
            remark_text = content_para.get('remark')
            if remark_text:
                question_edit_text.setText(remark_text)
            question_edit_text.setReadOnly(is_readonly)
            question_edit_text.setMaximumHeight(50)
            question_vbox_para.addWidget(question_edit_text)

        div = json_dict_para[str(i)]
        question_widget = QWidget()
        question_vbox = QVBoxLayout()
        preview_widget = QWidget()
        preview_vbox = QVBoxLayout()
        content = div['content']
        if div['type'] == 'title':
            question_title_label = QLabel(div['content'])
            question_title_label.setStyleSheet("color:rgb(250, 128, 10)")
            preview_title_label = QLabel(div['content'])
            question_vbox.addWidget(question_title_label)
            question_widget.setLayout(question_vbox)
            preview_vbox.addWidget(preview_title_label)
            preview_widget.setLayout(preview_vbox)
            setattr(question_widget, 'is_tag', True)
        elif div['type'] == 'tag':
            question_tag_label = QLabel(div['content'])
            preview_tag_label = QLabel(div['content'])
            question_tag_label.setStyleSheet("color:rgb(250, 128, 10)")
            question_vbox.addWidget(question_tag_label)
            question_widget.setLayout(question_vbox)
            preview_vbox.addWidget(preview_tag_label)
            preview_widget.setLayout(preview_vbox)
            setattr(question_widget, 'is_tag', True)
        elif div['type'] == '选择题':
            set_question(content, question_vbox, preview_vbox)
            options = content['options']
            options_img_path = options.get('img')
            if options_img_path:
                question_options_img_label = QLabel()
                question_options_img_label.setPixmap(QPixmap(options_img_path))
                question_vbox.addWidget(question_options_img_label)
            else:
                items = options['items']
                question_options_listwidget = QListWidget()
                # question_options_listwidget.setStyleSheet('::item{border:0px solid #000000}')
                question_options_listwidget.setMaximumHeight(100)
                question_options_listwidget.addItems(items)
                question_vbox.addWidget(question_options_listwidget)
            set_attach(content, question_vbox)
            set_remark(content, question_vbox)
        elif div['type'] == '填空题':
            set_question(content, question_vbox, preview_vbox)
            set_attach(content, question_vbox)
            set_remark(content, question_vbox)
        elif div['type'] == '简答题':
            set_question(content, question_vbox, preview_vbox)
            answer = content['answer']
            if answer['type'] == 'text':
                question_answer_text = QTextEdit()
                question_answer_text.setText(answer['content'])
                question_answer_text.setReadOnly(True)
                question_answer_text.setMaximumHeight(60)
                question_vbox.addWidget(question_answer_text)
            else:
                question_answer_label = QLabel()
                question_answer_label.setPixmap(QPixmap(answer['src']))
                question_vbox.addWidget(question_answer_label)
            set_attach(content, question_vbox)
            set_remark(content, question_vbox)
        question_widget.setLayout(question_vbox)
        preview_widget.setLayout(preview_vbox)
        return question_widget, preview_widget
        # self.text_edit_dict[str(i)] = question_edit_text

    def give_question_table(self):
        return self.question_table

    def give_preview_table(self):
        return self.preview_table

    def give_text_edit_dict(self):
        return self.text_edit_dict

    def give_json_dict(self):
        return self.json_dict
