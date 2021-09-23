# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 19:02:49 2021

@author: serge
"""

import os, re

def get_tests_directories_list(root_folder):
    directoty_list = []
    for i in range(len(os.listdir(root_folder))):
        test_res_folder = f"{root_folder}/{os.listdir(root_folder)[i]}"
        test_res_folder_list = os.listdir(test_res_folder)
        directoty_list.append([f"{test_res_folder}/" + x for x in test_res_folder_list if isinstance(x, str)])
    return directoty_list

def make_list_from_2dlist(tests_directories_list):
    res = []
    for i in range(len(tests_directories_list)):
        for j in range(len(tests_directories_list[i])):
            res.append(tests_directories_list[i][j])   
    return res

def list_split(list_name, elem_number):
    return [list_name[d:d+2] for d in range(0, len(list_name), 2)]

def nums_from_str(s):
    nums = re.findall(r'\d*\.\d+|\d+', s)
    nums = [float(i) for i in nums] 
    return nums

def files_match_check(test_directory, res_folders):
    res = dict.fromkeys(res_folders)
    for i in range(len(res_folders)):
        data = []
        folders_list = []
        files_list = []
        for root, dirs, files in os.walk(f"{test_directory}/{res_folders[i]}"):  
            for name in dirs:
                folders_list.append(name)
            for file in files:
                files_list.append(file)
        for folder, file in zip(folders_list, files_list):
            data.extend([folder, file])
        res[f"{res_folders[i]}"] = data
    return res

def ok_script(root_folder, test_directory, report_filename, temp_file):
    with open(f"{temp_file}", 'a') as output:            
        with open(f"{test_directory}/{report_filename}", 'r') as r:
            first = r.read(1)
            if not first:
                print(f"OK: {test_directory[len(root_folder)+1:]}/")
                output.write(f"OK: {test_directory[len(root_folder)+1:]}/\n")
    
def fail_script(root_folder, test_directory, report_filename, temp_file):
    with open(f"{temp_file}", 'a') as output:
        print(f"FAIL: {test_directory[len(root_folder)+1:]}/")
        output.write(f"FAIL: {test_directory[len(root_folder)+1:]}/\n") 
        with open(f"{test_directory}/{report_filename}", 'r') as r:
            for line in r:
                print(line)
                output.write(f"{line}\n")    

def first_check(root_folder, test_directory, res_folders, report_filename, temp_file):
    res = True
    def result_folders_exist_check(test_directory, res_folders):
        res = [(x, os.path.exists(f"{test_directory}/{x}")) for x in res_folders]
        return res
    result_folders_exist_check_list = result_folders_exist_check(test_directory, res_folders)
    buf = []
    for folder in result_folders_exist_check_list:
        buf.append(folder[1])
        if False in folder:
            fail_text = f"directory missing: {folder[0]}"
            res = False
            with open(f"{test_directory}/{report_filename}", 'a') as f:
                f.write(f"{fail_text}\n")
    if False in buf:
        fail_script(root_folder, test_directory, report_filename, temp_file)
    return res

def second_check(root_folder, test_directory, res_folders, report_filename, temp_file, data):
    res = True
    missing = sorted(list(set(data[res_folders[0]]) - set(data[res_folders[1]])))
    missing_split = list_split(missing, 2)
    extra = sorted(list(set(data[res_folders[1]]) - set(data[res_folders[0]])))
    extra_split = list_split(extra, 2)
    buf = []
    with open(f"{test_directory}/{report_filename}", 'a') as f:
        if extra:
            f.write(f"In {res_folders[1]} there are extra files not present in {res_folders[0]}: ")
            for j in range(len(extra_split)):
                f.write(f"'{extra_split[j][0]}/{extra_split[j][1]}'")
                if j != len(extra_split) - 1:
                    f.write(', ')
                if j == len(extra_split) - 1:
                    f.write('\n')
            buf.append(False)
        if missing:
            f.write(f"In {res_folders[1]} there are missing files present in {res_folders[0]}: ")
            for k in range(len(missing_split)):
                f.write(f"'{missing_split[k][0]}/{missing_split[k][1]}'")
                if k != len(missing_split) - 1:
                    f.write(', ')
                if k == len(missing_split) - 1:
                    f.write('\n')
            buf.append(False)
    if False in buf:
        res = False
        fail_script(root_folder, test_directory, report_filename, temp_file)
    return res

def third_check(test_directory, res_folders, report_filename, temp_file, data):
    res = True
    with open(f"{test_directory}/{report_filename}", 'a') as f:
        for l in range(len(list_split(data[res_folders[1]], 2))):
            stdout_file_directory = f"{test_directory}/{res_folders[1]}/{list_split(data[res_folders[1]], 2)[l][0]}/{list_split(data[res_folders[1]], 2)[l][1]}"
            test_file_index = stdout_file_directory.index(res_folders[1]) + len(res_folders[1]) + 1
            with open(stdout_file_directory, 'r') as std:
                line_num = 1
                flag = True
                for line in std:
                    str_split = line.split()
                    for elem in str_split:
                        if 'error' in elem.lower() and '_' not in elem.lower():
                            res = False
                            f.write(f"{stdout_file_directory[test_file_index:]}({line_num}): {line}\n")
                    if 'solver finished at' in line.lower() and line.find('Solver') == 0:
                        flag = False
                    line_num += 1                 
                if flag == True:
                    res = False
                    f.write(f"{stdout_file_directory[test_file_index:]}: missing 'Solver finished at'\n")
    return res

def fourth_check(test_directory, res_folders, report_filename, temp_file, data):
    res = True
    def value_check(test_directory, data, string):
        if string == 'Memory Working Set Peak':
            ind_of_num = 1
        elif string == 'MESH::Bricks: Total':
            ind_of_num = 0
        else: raise Exception ('You are finding wrong string')
        ft_run = []
        ft_ref = []
        for l in range(len(list_split(data[res_folders[1]], 2))):
            ft_run_stdout_file_directory = f"{test_directory}/{res_folders[1]}/{list_split(data[res_folders[1]], 2)[l][0]}/{list_split(data[res_folders[1]], 2)[l][1]}"
            ft_ref_stdout_file_directory = f"{test_directory}/{res_folders[0]}/{list_split(data[res_folders[0]], 2)[l][0]}/{list_split(data[res_folders[0]], 2)[l][1]}"
            ft_run_buf = []
            ft_ref_buf = []
            with open(ft_run_stdout_file_directory, 'r') as std:
                for line in std:
                    if string in line:
                        index = ft_run_stdout_file_directory.index(res_folders[1])
                        ft_run_buf.append({f"{ft_run_stdout_file_directory[index:]}": nums_from_str(line)[ind_of_num]})
            with open(ft_ref_stdout_file_directory, 'r') as std:
                for line in std:
                    if string in line:
                        index = ft_ref_stdout_file_directory.index(res_folders[0])
                        ft_ref_buf.append({f"{ft_ref_stdout_file_directory[index:]}": nums_from_str(line)[ind_of_num]})
            ft_run.append(ft_run_buf[-1])
            ft_ref.append(ft_ref_buf[-1])
        return ft_run, ft_ref
    def calculation_script(criterion, run, ref):
        ft_reference_value = list(ref.values())[0]
        ft_run_value = list(run.values())[0]
        #ft_reference_key = list(ref.keys())[0]
        ft_run_key = list(run.keys())[0]                
        rel_diff = round(ft_run_value/ft_reference_value - 1, 2)
        return ft_run_key, ft_run_value, ft_reference_value, rel_diff
    with open(f"{test_directory}/{report_filename}", 'a') as f:  
        #_____a_____
        mswp_criterion = 0.5
        
        ft_ref_mswp_list = []
        ft_run_mswp_list = []        
        ft_run_mswp_list, ft_ref_mswp_list = value_check(test_directory, data, 'Memory Working Set Peak')
        for run, ref in zip(ft_run_mswp_list, ft_ref_mswp_list):
            mswp_run_key, mswp_run_value, mswp_reference_value, mswp_rel_diff = calculation_script(mswp_criterion, run, ref)
            if abs(mswp_rel_diff) > mswp_criterion:
                res = False
                f.write(f"{mswp_run_key[7:]}: different 'Memory Working Set Peak' (ft_run={mswp_run_value}, ft_reference={mswp_reference_value}, rel.diff={mswp_rel_diff}, criterion={mswp_criterion})\n") 
        #_____b_____
        bricks_criterion = 0.1
        ft_ref_bricks_list = []
        ft_run_bricks_list = []        
        ft_run_bricks_list, ft_ref_bricks_list = value_check(test_directory, data, 'MESH::Bricks: Total')
        for run, ref in zip(ft_run_bricks_list, ft_ref_bricks_list):
            bricks_run_key, bricks_run_value, bricks_reference_value, bricks_rel_diff = calculation_script(bricks_criterion, run, ref)
            if abs(bricks_rel_diff) > bricks_criterion:
                res = False
                f.write(f"{bricks_run_key[7:]}: different 'Total' of bricks (ft_run={bricks_run_value}, ft_reference={bricks_reference_value}, rel.diff={bricks_rel_diff}, criterion={bricks_criterion})\n")
    return res



def main():
    
    root_folder = "logs"
    reference_res_folder = "ft_reference"
    run_res_folder = "ft_run"
    res_folders = (reference_res_folder, run_res_folder)
    
    temp_file = 'output.txt'
    with open(f"{temp_file}", 'w') as f:
        f.write('')
        
    out_file = 'out.stdout'
    with open(f"{out_file}", 'w') as f:
        f.write('')
    
    tests_directories_list = get_tests_directories_list(root_folder) # (num of types) X (num of tests of such type)
    
    formed_list = make_list_from_2dlist(tests_directories_list)
    
    for test_directory in formed_list:
        
        FILENAME = 'report.txt'
        with open(f"{test_directory}/{FILENAME}", 'w') as f:
            f.write('')
            
        flag = True
        
    #_____Первая проверка_____
        first_check_res = first_check(root_folder, test_directory, res_folders, FILENAME, temp_file)
        if first_check_res == False:
            continue
    #_____Вторая проверка_____
        matching_files_data = files_match_check(test_directory, res_folders)
        
        second_check_res = second_check(root_folder, test_directory, res_folders, FILENAME, temp_file, matching_files_data)
        if second_check_res == False:
            continue
    #_____Третья проверка_____
        third_check_res = third_check(test_directory, res_folders, FILENAME, temp_file, matching_files_data)
        if third_check_res == False:
            flag = False
            pass
    #_____Четвертая проверка_____
        fourth_check_res = fourth_check(test_directory, res_folders, FILENAME, temp_file, matching_files_data)
        if fourth_check_res == False:
            flag = False
            pass
        
        if flag == True:
            ok_script(root_folder, test_directory, FILENAME, temp_file)
            print(f"OK: {test_directory[len(root_folder)+1:]}/")
        else: fail_script(root_folder, test_directory, FILENAME, temp_file)
    
    with open(f"{temp_file}") as a:
        with open(f"{out_file}", 'a') as out: 
            for line in filter(lambda x: x != '\n', a):
                out.write(line)
        
    os.remove(f"{temp_file}")

    
if __name__ == "__main__":
    main()
