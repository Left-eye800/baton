""" 将txt文本内容转换成json文本

包括将txt文本内容转换成json文本的write_in_json_file函数

包括将json文本内容转换成python字典的read_from_json_file函数

在其他py文件中可以调用write_in_json_file和read_from_json_file函数,
也可以直接修改本文件text_source_path文件路径直接执行该文件,
亦可以使用cmd命令行窗口使用python generate_json.py "filename"执行该文件

the statistics of this file:
lines(count)    understand_level(h/m/l)    classes(count)    functions(count)    fields(count)
000000000149    ----------------------h    00000000000000    0000000000000005    ~~~~~~~~~~~~1
"""

import re
import json
import sys
import pprint

__author__ = '与C同行'
try:
    text_source_path = sys.argv[1]
except IndexError:
    text_source_path = r'.\source_files\text_source\example.txt'


def get_page_text(filename):
    with open(filename, 'r', encoding='utf8') as f:
        page_text_return = f.read()
    return page_text_return


def get_json_filename(page_text_para):
    json_file_pattern = r'<json_file_name>(.*?)</json_file_name>'
    json_file_name_content = re.findall(json_file_pattern, page_text_para, re.S)
    json_file_name = json_file_name_content[0].strip()
    return json_file_name


def get_json_dict(page_text_para):
    json_dict = {}
    div_pattern = r'<div>(.*?)</div>'
    type_pattern = r'<type>(.*?)</type>'
    content_pattern = r'<content>(.*?)</content>'
    question_pattern = r'<question>(.*?)</question>'
    img_pattern = r'<img>(.*?)</img>'
    options_pattern = r'<options>(.*?)</options>'
    item_pattern = r'<item>(.*?)</item>'
    attach_pattern = r'<attach>(.*?)</attach>'
    answer_pattern = r'<answer>(.*?)</answer>'

    def handle_question(content_para, dict_para):
        blank_question_list = re.findall(question_pattern, content_para, re.S)
        question = blank_question_list[0].strip()
        if question.startswith('<img>'):
            blank_question_img_list = re.findall(img_pattern, question, re.S)
            question_img = blank_question_img_list[0].strip()
            dict_para['content']['question'] = {'type': 'img', 'src': question_img}
        else:
            dict_para['content']['question'] = {'type': 'text', 'content': question}

    def handle_attach(content_para, dict_para):
        nonlocal json_dict
        blank_attach_list = re.findall(attach_pattern, content_para, re.S)
        if not blank_attach_list:
            pass
        else:
            attach = blank_attach_list[0].strip()
            blank_attach_img_list = re.findall(img_pattern, attach, re.S)
            attach_list = []
            for blank_attach_img in blank_attach_img_list:
                attach_img = blank_attach_img.strip()
                attach_list.append(attach_img)
            dict_para['content']['attach'] = attach_list
        json_dict[i + 1] = dict_para

    div_list = re.findall(div_pattern, page_text_para, re.S)
    for i, blank_div in enumerate(div_list):
        div = blank_div.strip()
        blank_type = re.findall(type_pattern, div, re.S)
        type_ = blank_type[0].strip()
        blank_content = re.findall(content_pattern, div, re.S)
        content = blank_content[0].strip()
        if type_ == '标签':
            json_dict[i+1] = {'type': 'tag',
                              'content': content}
        elif type_ == '标题':
            json_dict[i+1] = {'type': 'title',
                              'content': content}
        elif type_ == '选择题':
            choice_dict = {'type': '选择题',
                           'content': {}}
            handle_question(content, choice_dict)
            blank_options_list = re.findall(options_pattern, content, re.S)
            options = blank_options_list[0].strip()
            if options.startswith('<item>'):
                blank_item_list = re.findall(item_pattern, options, re.S)
                items_dict = {'items': []}
                for blank_item in blank_item_list:
                    item = blank_item.strip()
                    items_dict['items'].append(item)
                choice_dict['content']['options'] = items_dict
            elif options.startswith('<img>'):
                blank_options_img = re.findall(img_pattern, options, re.S)
                options_img = blank_options_img[0].strip()
                choice_dict['content']['options'] = {'img': options_img}
            handle_attach(content, choice_dict)
        elif type_ == '填空题':
            fill_blank_dict = {'type': '填空题',
                               'content': {}}
            handle_question(content, fill_blank_dict)
            handle_attach(content, fill_blank_dict)
        elif type_ == '简答题':
            short_answer_dict = {'type': '简答题',
                                 'content': {}}
            handle_question(content, short_answer_dict)
            blank_answer_list = re.findall(answer_pattern, content, re.S)
            answer = blank_answer_list[0].strip()
            if answer.startswith('<img>'):
                blank_answer_img_list = re.findall(img_pattern, answer, re.S)
                answer_img = blank_answer_img_list[0].strip()
                short_answer_dict['content']['answer'] = {'type': 'img', 'src': answer_img}
            else:
                short_answer_dict['content']['answer'] = {'type': 'text', 'content': answer}
            handle_attach(content, short_answer_dict)
    return json_dict


def write_in_json_file(text_filename):
    """
    将字典写入json文件
    """
    page_text = get_page_text(text_filename)
    json_file_path = get_json_filename(page_text)
    json_file_dict = get_json_dict(page_text)
    pprint.pprint(json_file_dict)
    with open(json_file_path, 'w', encoding='utf8') as f:
        json.dump(json_file_dict, f)


def read_from_json_file(json_filename):
    """
    将json文件读入字典
    """
    with open(json_filename, 'r', encoding='utf8') as f:
        json_dict = json.load(f)
    return json_dict


if __name__ == '__main__':
    write_in_json_file(text_source_path)
