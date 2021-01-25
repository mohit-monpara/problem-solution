import pandas as pd
import numpy as np
import spacy
sp_mod = spacy.load("en_core_web_sm")
import os, sys
import glob
from itertools import chain 

filenames = glob.glob('/Users/Mohit/Desktop/Work/Shreays Dataset/chuncker_raw_new_dataset/cnn/del/*.story', recursive = True)
# filenames = glob.glob('/Users/Mohit/Desktop/Work/Shreays Dataset/chuncker_raw_new_dataset/cnn/stories/*.story', recursive = True)
## filenames = filenames[0]
# print(filenames)

files = {} 
allstory_list = []
for filename in filenames: 
    with open(filename, "r") as file: 
        if filename in files: 
            continue 
        files[filename] = file.read() 
for filename, text in files.items(): 
    allstory_list.append(text)
    

def convert_allstory_list(allstory_list):
    final_list = []
    for i in range(len(allstory_list)):
        res_list = allstory_list[0].splitlines()
        res = [ele for ele in res_list if ele != []]
        res = [x for x in res if x]
        # res = res[: len(res) - 8]
        final_list.append(res)
    return final_list
    # print(res)
    
final_list = convert_allstory_list(allstory_list)

# IMP
def convert_pairs(final_list):
    new_list = []
    for i in range(len(final_list)):
        for j in range(len(final_list[i])):
            new_sents = [] # for sentences with lenght greater than 5
            text = final_list[i][j]
            doc = sp_mod(text)
            # Tokenise the sentence
            sents = [elem for elem in doc.sents]

            if len(sents) > 1:

                # Idnetify the length of the sentence
                sents_len = [len(elem) for elem in doc.sents]
                
                # Ignore the tokenise setence with length less than 5 
                for k in range(len(sents_len)):
                    if sents_len[k] > 5:
                        new_sents.append(sents[k])
            else:
                new_sents = []
                
            # Assign to final list
            final_list[i][j] = new_sents

    final_list = list(chain.from_iterable(final_list))
    final_list = [x for x in final_list if x]
    new_list.append(final_list)

    return new_list


final_list_converted_pairs = convert_pairs(final_list)
# final_list_converted_pairs

sent_1_list = []
sent_2_list = []
for i in range(len(final_list_converted_pairs)):
    print("Out of {}, {} Completed".format(len(final_list_converted_pairs), i))
    for j in range(len(final_list_converted_pairs[i])):
        first_val = final_list_converted_pairs[i][j][0]
        sent_1_list.append(first_val)
        
        last_val = final_list_converted_pairs[i][j][-1]
        sent_2_list.append(last_val)

# remove 1st and last element from sent_1_list and sent_2_list repsectively
sent_1_list = sent_1_list[1:] 
sent_2_list = sent_2_list[:-1]         
print(type(sent_1_list))

print("1st list: ", sent_1_list)
print("2nd list: ", sent_2_list)

columns = ["sent-1", "sent-2"]
final_df = pd.DataFrame(columns=columns)
final_df['sent-1'] = sent_1_list
final_df['sent-2'] = sent_2_list
final_df['sent-1'] = final_df['sent-1'].astype('str')
final_df['sent-2'] = final_df['sent-2'].astype('str')

print(final_df.shape)
print(final_df.head())

final_df['label'] = 0

final_df.to_csv("/mnt/problem_sol_exp/data/unrelated_cnn.csv")
final_df.to_json('/mnt/problem_sol_exp/data/unrelated_cnn.json', orient='records', lines=True)