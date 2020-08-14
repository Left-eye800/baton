"""
关于

the statistics of this file:
lines(count)    understand_level(h/m/l)    classes(count)    functions(count)    fields(count)
000000000043    ----------------------l    00000000000000    0000000000000001    ~~~~~~~~~~~~~
"""

import re

__author__ = '与C同行'


def read_about(about_filename):
    div_pattern = r'<div>(.*?)</div>'
    contributor_pattern = r'<contributors>(.*?)</contributors>'
    contribute_pattern = r'<contribute>(.*?)</contribute>'
    email_pattern = r'<email>(.*?)</email>'
    about_string = ''
    try:
        with open(about_filename, 'r', encoding='utf8') as f:
            content = f.read()
        div_list = re.findall(div_pattern, content, re.S)
        if not div_list:
            about_string = '贡献者:\n王创业\n贡献:\n开发baton软件的贡献者,有自己的微信公众号“与C同行”,欢迎关注\n'\
                                'email:\n3305703462@qq.com'
        for i in range(len(div_list)):
            if i == 0:
                about_string += '贡献者:\n王创业\n贡献:\n开发baton软件的贡献者,有自己的微信公众号“与C同行”,欢迎关注\n'\
                                'email:\n3305703462@qq.com'
            else:
                div = div_list[i].strip()
                contributors_list = re.findall(contributor_pattern, div, re.S)
                contributors = contributors_list[0].strip()
                contribute_list = re.findall(contribute_pattern, div, re.S)
                contribute = contribute_list[0].strip()
                email_list = re.findall(email_pattern, div, re.S)
                email = email_list[0].strip()
                about_string += f'\n\n贡献者:\n{contributors}\n贡献:\n{contribute}\nemail:\n{email}'
    except:
        about_string = '贡献者:\n王创业\n贡献:\n开发baton软件的贡献者,有自己的微信公众号“与C同行”,欢迎关注\n'\
                                'email:\n3305703462@qq.com'
    return about_string
