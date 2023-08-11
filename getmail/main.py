# -*- coding : utf-8 -*-
import re
import os
import zipfile
from mail import recv_email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from shutil import copyfile

to_solve_dir = 'to_solve'
solved_dir = 'solved'

homework_ddl = {'作业1':'2020-03-28 00:00', '作业2':'2020-04-04 00:00', '作业3':'2020-04-11 00:00',
                '作业4':'2020-04-18 00:00', '作业5':'2020-04-25 00:00', '作业6':'2020-05-02 00:00',
                '作业7':'2020-05-09 00:00', '作业8':'2020-05-16 00:00', '作业9':'2020-05-23 00:00',
                '作业10':'2020-05-30 00:00'}
student_map = {}
class_map = {}
homework_con = []

def read_condition(file_name):
    lines = open(file_name, 'r', encoding='utf-8').readlines()
    for i in range(len(homework_ddl)):
        homework_con.append({})
    for line in lines[1:]:
        params = line.strip().split(',')
        # print(params)
        student_map[params[0]] = params[1]
        class_map[params[0]] = params[2]
        for idx, elem in enumerate(params[3:]):
            if elem != '':
                homework_con[idx][params[0]] = elem

def write_condition(file_name):
    with open(file_name, 'w+', encoding='utf-8') as fp:
        fp.write('学号,姓名,班级,')
        for hw in homework_ddl.keys():
            fp.write(hw)
            fp.write(',')
        fp.write('\n')
        for id, name in student_map.items():
            fp.write(id)
            fp.write(',')
            fp.write(name)
            fp.write(',')
            fp.write(class_map[id])
            fp.write(',')
            for con in homework_con:
                if id in con:
                    fp.write(con[id])
                fp.write(',')
            fp.write('\n')

def parse_filename(attach_name):
    params = re.split(r'[-.()（）]', attach_name)
    if params[0] in homework_ddl.keys() and params[-1] == 'docx':
        if params[1] in student_map.keys():
            homework_type = params[0]
            student_id = params[1]
            student_name = student_map[student_id]
            student_class = class_map[student_id]
            save_dir = os.path.join(homework_type, student_class)
            save_filename = '{}-{}-{}.docx'.format(homework_type, student_id, student_name)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            return student_id, homework_type, os.path.join(save_dir, save_filename)
    return None, None, attach_name

def update_from_email(start_idx):
    email_addr = 'hitsz2020ds02@163.com'
    password = 'HFCIZFZSEGIUFQYG'
    pop3_server = 'pop.163.com'

    read_condition('homework_condition.csv')

    dl = recv_email(username=email_addr, password=password, email_server=pop3_server)

    for idx in range(dl.msg_num, start_idx, -1):
        msg = dl.get_msg(idx)
        info = dl.get_info(msg)
        msg_date = info[4]
        attach_name, attach_data = dl.get_attach(msg)
        if attach_name is None:
            print(idx, '非作业邮件 主题：', info[3])
            continue
        # print(attach_name)
        student_id, homework_type, save_name = parse_filename(attach_name)
        if save_name == attach_name:
            print(idx, '附件名不规范', attach_name)
            save_name = msg_date.replace(':', ';') + '.' + save_name
            with open(os.path.join(to_solve_dir, save_name), 'wb') as fp:
                fp.write(attach_data)
            continue
        homework_idx = list(homework_ddl.keys()).index(homework_type)

        if student_id not in homework_con[homework_idx]:
            print(idx, attach_name, ' \t收到新作业', save_name)
        elif homework_con[homework_idx][student_id] < msg_date:
            print(idx, attach_name, ' \t覆盖旧作业', save_name)
        else:
            print(idx, attach_name, ' \t文件已收到', save_name)
            continue
        homework_con[homework_idx][student_id] = msg_date
        with open(save_name, 'wb') as fp:
            fp.write(attach_data)

    write_condition('homework_condition.csv')

def update_from_backup():
    read_condition('homework_condition.csv')

    for file_name in os.listdir(solved_dir):
        params = file_name.strip().split('.')
        date_str = params[0].replace(';', ':')
        student_info = params[1].strip().split('-')
        file_suffix = params[2]
        if file_suffix == 'docx':
            homework_type = student_info[0]
            homework_idx = list(homework_ddl.keys()).index(homework_type)
            student_id = student_info[1]
            student_name = student_info[2]
            student_class = class_map[student_id]
            save_dir = os.path.join(homework_type, student_class)
            save_filename = '{}-{}-{}.docx'.format(homework_type, student_id, student_name)

            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            if student_id in homework_con[homework_idx] and homework_con[homework_idx][student_id] < date_str:
                print(file_name, date_str, '\t覆盖旧作业', os.path.join(save_dir, save_filename))
                homework_con[homework_idx][student_id] = date_str
                copyfile(src=os.path.join(solved_dir, file_name), dst=os.path.join(save_dir, save_filename))
                # os.remove(os.path.join(solved_dir, file_name))
                continue
            if student_id not in homework_con[homework_idx]:
                print(file_name, date_str, '\t收到新作业', os.path.join(save_dir, save_filename))
                homework_con[homework_idx][student_id] = date_str
                copyfile(src=os.path.join(solved_dir, file_name), dst=os.path.join(save_dir, save_filename))
                # os.remove(os.path.join(solved_dir, file_name))
                continue
        print(file_name, date_str, '文件无效')
        # os.remove(os.path.join(solved_dir, file_name))

    write_condition('homework_condition.csv')

def homework_compress(homework_type):
    homework_info = 'homework_info.txt'


    for student_class in os.listdir(homework_type):
        with zipfile.ZipFile(os.path.join(homework_type, student_class+'.zip'), mode='w') as zipf:
            zipf.write(os.path.join(homework_type, student_class))
            zipf.write(homework_info)
            print(student_class)

def output_condition():
    read_condition('homework_condition.csv')

    cond = []
    for homework_type, ddl in homework_ddl.items():
        i = list(homework_ddl.keys()).index(homework_type)
        cond.append({'type':homework_type, 'ddl':ddl, '未交':'\n', '补交':'\n'})
        for student_id, student_name in student_map.items():
            if student_id not in homework_con[i]:
                cond[i]['未交'] += '{}-{}\n'.format(student_id, student_name)
            if student_id in homework_con[i] and homework_con[i][student_id] >= ddl:
                cond[i]['补交'] += '{}-{}-{}\n'.format(student_id, student_name, homework_con[i][student_id])
        # print(cond[i])
    with open('homework_info.txt', 'w+', encoding='GBK') as fp:
        for it in cond:
            fp.write(it['type'])
            fp.write(' ')
            fp.write(it['ddl'])
            fp.write('\n')
            fp.write('未交')
            fp.write(it['未交'])
            fp.write('补交')
            fp.write(it['补交'])
            fp.write('-------------------------------------------------------------------------------\n')


if __name__ == '__main__':

    if not os.path.exists(to_solve_dir):
        os.makedirs(to_solve_dir)

    # update_from_email(500) # 639
    update_from_backup()
    output_condition()
    # homework_compress('作业2')