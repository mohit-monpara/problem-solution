import pandas as pd
import numpy as np
import spacy
sp_mod = spacy.load("en_core_web_sm")
import os, sys
import glob
from itertools import chain 

def cell_expand(df, lst_cols, fill_value=''):
    # make sure `lst_cols` is a list
    if lst_cols and not isinstance(lst_cols, list):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)

    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()

    if (lens > 0).all():
        # ALL lists in cells aren't empty
        return pd.DataFrame({
            col:np.repeat(df[col].values, df[lst_cols[0]].str.len())
            for col in idx_cols
        }).assign(**{col:np.concatenate(df[col].values) for col in lst_cols}) \
          .loc[:, df.columns]
    else:
        # at least one list in cells is empty
        return pd.DataFrame({
            col:np.repeat(df[col].values, df[lst_cols[0]].str.len())
            for col in idx_cols
        }).assign(**{col:np.concatenate(df[col].values) for col in lst_cols}) \
          .append(df.loc[lens==0, idx_cols]).fillna(fill_value) \
          .loc[:, df.columns]
          
          
# filenames = glob.glob('/Users/Mohit/Desktop/Work/Shreays Dataset/chuncker_raw_new_dataset/cnn/del/*.story', recursive = True)
filenames = glob.glob('/mnt/problem_sol_exp/raw_ds/cnn/stories/*.story', recursive = True)

## filenames = filenames[0]
print(filenames)


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

def pairs_related(new_sents):
    df = pd.DataFrame(columns=['sent_list'], index = range(1))
    df['sent_list'][0] = new_sents

    df['sent_len'] = None
    for i in range(df.shape[0]):
        df['sent_len'][i] = len(df['sent_list'][i])
    df = df[df['sent_len']>1]
    # print("*"*100)
    # print(df.head())
    # print("*"*100)
    df = df.reset_index(drop=True)

    df['sent-1'] = None
    df['sent-2'] = None

    if df['sent_len'][0] > 2:
        for i in range(df.shape[0]):

            sent_1_list = []
            sent_2_list = []
            
            for j in range(df['sent_len'][i]):
                sent_1_list.append(df['sent_list'][i][j])
                if j+1 < df['sent_len'][i]:
                    sent_2_list.append(df['sent_list'][i][j+1])

            df['sent-1'][i] = sent_1_list
            df['sent-2'][i] = sent_2_list
            
            if len(df['sent-1'][i]) > len(df['sent-2'][i]):
                df['sent-1'][i].pop()

        col_list = ['sent-1','sent-2']
        df = cell_expand(df, lst_cols=col_list)
        df = df.reset_index(drop=True)

    else:

        for i in range(df.shape[0]):
            df['sent-1'][i] = df['sent_list'][i][0]
            df['sent-2'][i] = df['sent_list'][i][1]
        df = df.reset_index(drop=True)

    df['sent-1'] = df['sent-1'].astype('str')
    df['sent-2'] = df['sent-2'].astype('str')
    df['sent-1'].replace('', np.nan, inplace=True)
    df.dropna(subset=['sent-1'], inplace=True)
    df['sent-2'].replace('', np.nan, inplace=True)
    df.dropna(subset=['sent-2'], inplace=True)
    df = df[['sent-1','sent-2']]
    final_list2 = df.values.tolist()
    return final_list2


final_df = pd.DataFrame(columns = ["sent-1", "sent-2"])
for i in range(len(final_list_converted_pairs)):
    print("Out of {}, {} Completed".format(len(final_list_converted_pairs), i))
    for j in range(len(final_list_converted_pairs[i])):
        try:
            inter_df = pd.DataFrame(pairs_related(final_list_converted_pairs[i][j]))
            inter_df.columns = ["sent-1", "sent-2"]
            final_df = final_df.append(inter_df)
        except:
            # print(pairs_related(final_list_converted_pairs[i][j]))
            continue
final_df = final_df.reset_index(drop=True)


final_df['label'] = 1

<<<<<<< HEAD
final_df.to_csv("/Users/Mohit/Desktop/Work/Shreays Dataset/chuncker_raw_new_dataset/problem-solution/data/related.csv")

# conda env export > environment.yml
# conda env create -f environment.yml
=======
final_df.to_csv("/mnt/problem_sol_exp/data/related_cnn.csv")
final_df.to_json('/mnt/problem_sol_exp/data/related_cnn.json', orient='records', lines=True)
>>>>>>> 4ff84fd69fc8683ca28d5acc93bd3589f0f76e68
