# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 00:07:43 2021

@author: serge
"""

import os

def get_tests_directories_list(root_folder):
    directoty_list = []
    for i in range(len(os.listdir(root_folder))):
        test_res_folder = f"logs/{os.listdir(root_folder)[i]}"
        test_res_folder_list = os.listdir(test_res_folder)
        directoty_list.append([f"{test_res_folder}/" + x for x in test_res_folder_list if isinstance(x, str)])
    return directoty_list

root_folder = "logs"
tests_directories_list = get_tests_directories_list(root_folder)



FILENAME = 'report.txt'

out_file = 'out.stdout'
with open(f"{out_file}", 'w') as f:
    f.write('')

temp_file = 'output.txt'
with open(f"{temp_file}", 'w') as f:
    f.write('')



for i in range(len(tests_directories_list)):
    for j in range(len(tests_directories_list[i])):

        with open(f"{temp_file}", 'a') as output:            
            with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'r') as r:
                first = r.read(1)
                if not first:
                    print(f"OK: {tests_directories_list[i][j][5:]}")
                    output.write(f"OK: {tests_directories_list[i][j][5:]}\n")
                    continue
        
        with open(f"{temp_file}", 'a') as output:
            print(f"FAIL: {tests_directories_list[i][j][5:]}")
            output.write(f"FAIL: {tests_directories_list[i][j][5:]}\n") 
            with open(f"{tests_directories_list[i][j]}/{FILENAME}", 'r') as r:
                for line in r:
                    print(line)
                    output.write(f"{line}\n")

with open(f"{temp_file}") as a:
    with open(f"{out_file}", 'a') as out: 
        for line in filter(lambda x: x != '\n', a):
            out.write(line)
    
os.remove(f"{temp_file}")