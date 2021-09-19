# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 14:44:24 2021

@author: serge
"""

import os
import re

def get_tests_directories_list(root_folder):
    directoty_list = []
    for i in range(len(os.listdir(root_folder))):
        test_res_folder = f"logs/{os.listdir(root_folder)[i]}"
        test_res_folder_list = os.listdir(test_res_folder)
        directoty_list.append([f"{test_res_folder}/" + x for x in test_res_folder_list if isinstance(x, str)])
    return directoty_list

def result_folders_exist_check(test_directory, res_folders):
    res = [(x, os.path.exists(f"{test_directory}/{x}")) for x in res_folders]
    return res

def files_match_check(test_directory, res_folders):
    
    data = dict.fromkeys(res_folders)
    for i in range(len(res_folders)):
        data1 = []
        folders_list = []
        files_list = []
        for root, dirs, files in os.walk(f"{test_directory}/{res_folders[i]}"):  
            for name in dirs:
                folders_list.append(name)
            for file in files:
                files_list.append(file)
        for folder, file in zip(folders_list, files_list):
            data1.extend([folder, file])
        data[f"{res_folders[i]}"] = data1
    return data

def list_split(list_name, elem_number):
    return [list_name[d:d+2] for d in range(0, len(list_name), 2)]

def mswp_value_check(test_directory, data):
    ft_run = []
    ft_ref = []
    for l in range(len(list_split(data['ft_run'], 2))):
        ft_run_stdout_file_directory = f"{test_directory}/ft_run/{list_split(data['ft_run'], 2)[l][0]}/{list_split(data['ft_run'], 2)[l][1]}"
        ft_ref_stdout_file_directory = f"{test_directory}/ft_reference/{list_split(data['ft_reference'], 2)[l][0]}/{list_split(data['ft_reference'], 2)[l][1]}"
        ft_run_buf = []
        ft_ref_buf = []
        with open(ft_run_stdout_file_directory, 'r') as std:
            for line in std:
                if 'Memory Working Set Peak' in line:
                    index = ft_run_stdout_file_directory.index('ft_run')
                    ft_run_buf.append({f"{ft_run_stdout_file_directory[index:]}": nums_from_str(line)[1]})
        with open(ft_ref_stdout_file_directory, 'r') as std:
            for line in std:
                if 'Memory Working Set Peak' in line:
                    index = ft_ref_stdout_file_directory.index('ft_reference')
                    ft_ref_buf.append({f"{ft_ref_stdout_file_directory[index:]}": nums_from_str(line)[1]})
        
        ft_run.append(ft_run_buf[-1])
        ft_ref.append(ft_ref_buf[-1])        

# Этот вариант больше подходит по условию задания, но при нем результат не совпадает с файликом       
# =============================================================================
#         ft_run.append(max(ft_run_buf))
#         ft_ref.append(ft_ref_buf[ft_run_buf.index(max(ft_run_buf))])
# =============================================================================
        
    return ft_run, ft_ref

def nums_from_str(s):
    nums = re.findall(r'\d*\.\d+|\d+', s)
    nums = [float(i) for i in nums] 
    return nums

def bricks_total_value_check(test_directory, data):
    ft_run = []
    ft_ref = []
    for l in range(len(list_split(data['ft_run'], 2))):
        ft_run_stdout_file_directory = f"{test_directory}/ft_run/{list_split(data['ft_run'], 2)[l][0]}/{list_split(data['ft_run'], 2)[l][1]}"
        ft_ref_stdout_file_directory = f"{test_directory}/ft_reference/{list_split(data['ft_reference'], 2)[l][0]}/{list_split(data['ft_reference'], 2)[l][1]}"
        ft_run_buf = []
        ft_ref_buf = []
        with open(ft_run_stdout_file_directory, 'r') as std:
            for line in std:
                if 'MESH::Bricks:' in line:
                    index = ft_run_stdout_file_directory.index('ft_run')
                    ft_run_buf.append({f"{ft_run_stdout_file_directory[index:]}": nums_from_str(line)[0]})
        with open(ft_ref_stdout_file_directory, 'r') as std:
            for line in std:
                if 'MESH::Bricks:' in line:
                    index = ft_ref_stdout_file_directory.index('ft_reference')
                    ft_ref_buf.append({f"{ft_ref_stdout_file_directory[index:]}": nums_from_str(line)[0]})
        
        ft_run.append(ft_run_buf[-1])
        ft_ref.append(ft_ref_buf[-1])
        
    return ft_run, ft_ref





#_____Основная часть кода_____

root_folder = "logs"
res_folders = ('ft_reference','ft_run')
tests_directories_list = get_tests_directories_list(root_folder)


# Если нао проверить какой-то отдельный тест
# =============================================================================
# tests_directories_list = [[tests_directories_list[1][2]]]
# =============================================================================



#_____Путь к папке текущего проекта_____

for i in range(len(tests_directories_list)):
    for j in range(len(tests_directories_list[i])):
        
#        ok_flag = True

#_____Создаем файл report.txt в папке каждого проекта_____
        
        FILENAME = 'report.txt'
        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'w') as f:
            f.write('')

#_____Первая проверка_____

        result_folders_exist_check_list = result_folders_exist_check(tests_directories_list[i][j], res_folders)
        buf = []
        for folder in result_folders_exist_check_list:
            buf.append(folder[1])
            if False in folder:
                fail_text = f"directory missing: {folder[0]}"
#                print(f"FAIL:{tests_directories_list[i][j]}/\n{fail_text}")
                with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'a') as f:
                    f.write(f"{fail_text}\n")   
        if False in buf:
#            ok_flag = False
            print(f"FAIL:{tests_directories_list[i][j][5:]}")
            with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'r') as r:
                for line in r:
                    print(line) 
            continue
            
#_____Вторая проверка_____

        data = files_match_check((tests_directories_list[i][j]), res_folders)
        
        y = sorted(list(set(data['ft_reference']) - set(data['ft_run'])))
        yy = list_split(y, 2)
        x = sorted(list(set(data['ft_run']) - set(data['ft_reference'])))
        xx = list_split(x, 2)
        
        buf = []
        
        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'a') as f:
            if x:
                f.write('In ft_run there are extra files not present in ft_reference: ')
                for j in range(len(xx)):
                    f.write(f"'{xx[j][0]}/{xx[j][1]}'")
                    if j != len(xx) - 1:
                        f.write(', ')
                    if j == len(xx) - 1:
                        f.write('\n')
                buf.append(False)
            if y:
                f.write('In ft_run there are missing files present in ft_reference: ')
                for k in range(len(yy)):
                    f.write(f"'{yy[k][0]}/{yy[k][1]}'")
                    if k != len(yy) - 1:
                        f.write(', ')
                    if k == len(yy) - 1:
                        f.write('\n')
                buf.append(False)
        if False in buf:
#            ok_flag = False
            print(f"FAIL:{tests_directories_list[i][j][5:]}")
            with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'r') as r:
                for line in r:
                    print(line)            
            continue
            
#_____Третья проверка_____

        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'a') as f:
            for l in range(len(list_split(data['ft_run'], 2))):
                stdout_file_directory = f"{tests_directories_list[i][j]}/ft_run/{list_split(data['ft_run'], 2)[l][0]}/{list_split(data['ft_run'], 2)[l][1]}"
                test_file_index = stdout_file_directory.index('ft_run') + len('ft_run') + 1
                with open(stdout_file_directory, 'r') as std:
                    flag = 0
                    line_num = 1
                    for line in std:
                        if 'error' in line.lower():
                            f.write(f"{stdout_file_directory[test_file_index:]}({line_num}): {line}\n")
#                            ok_flag = False
                        if 'solver finished at' not in line.lower() and line.find('Solver') != 0:
                            flag += 1
                        line_num += 1                 
                    if flag == line_num - 3:
                        f.write(f"{stdout_file_directory[test_file_index:]}: missing 'Solver finished at'\n")
#                        ok_flag = False

#_____Четвертая проверка_____
#_____a_____

        criterion = 0.5
        
        ft_ref_mswp = []
        ft_run_mswp = []
        ft_run_mswp, ft_ref_mswp = mswp_value_check(tests_directories_list[i][j], data)
        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'a') as f:
            for mswp_run, mswp_ref in zip(ft_run_mswp, ft_ref_mswp):
                
                ft_reference_value = list(mswp_ref.values())[0]
                ft_run_value = list(mswp_run.values())[0]
                
                ft_reference_key = list(mswp_ref.keys())[0]
                ft_run_key = list(mswp_run.keys())[0]                
                
                rel_diff = round(ft_run_value/ft_reference_value - 1, 2)
                if abs(rel_diff) > criterion:
                    f.write(f"{ft_run_key[7:]}: different 'Memory Working Set Peak' (ft_run={ft_run_value}, ft_reference={ft_reference_value}, rel.diff={rel_diff}, criterion={criterion})\n")
#                    ok_flag = False

#_____b_____

        criterion = 0.1
        
        ft_ref_bricks = []
        ft_run_bricks = []
        ft_run_bricks, ft_ref_bricks = bricks_total_value_check(tests_directories_list[i][j], data)

        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'a') as f:
            for bricks_run, bricks_ref in zip(ft_run_bricks, ft_ref_bricks):
                
                ft_reference_value = list(bricks_ref.values())[0]
                ft_run_value = list(bricks_run.values())[0]
                
                ft_reference_key = list(bricks_ref.keys())[0]
                ft_run_key = list(bricks_run.keys())[0]                
                
                rel_diff = round(ft_run_value/ft_reference_value - 1, 2)
                if abs(rel_diff) > criterion:
                    f.write(f"{ft_run_key[7:]}: different 'Total' of bricks (ft_run={ft_run_value}, ft_reference={ft_reference_value}, rel.diff={rel_diff}, criterion={criterion})\n")
#                    ok_flag = False
                    
#_____Вывод результата в консоль_____
                    
        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'r') as r:
            first = r.read(1)
            if not first:
                print(f"OK:{tests_directories_list[i][j][5:]}")
                continue
        
        print(f"FAIL:{tests_directories_list[i][j][5:]}")
        with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'r') as r:
            for line in r:
                print(line)
            