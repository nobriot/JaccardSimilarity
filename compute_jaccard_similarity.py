# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 23:02:36 2016

Script for computing the top-words similarity loaded from JSON variables
Copyright (C) 2017  Nicolas Obriot - Sabrina Woltmann

@author: Sabrina Woltmann, Nicolas Obriot
"""

#%% Import the dependencies
import os
import json


#%% A couple of variables that we will need during the execution of the script
# Working directory is the directory where the script is placed.
working_directory = "/home/shared/Scripts/Python/Jaccard similarity/"
os.chdir(working_directory)
# Set this variable to TRUE in order to print all kind of information during execution
verbose = True
#Adjust this variable to affect the number of matchs : 
pass_criteria = 0.15 * 7 # Minimum match treshold for common_words * jaccard_similarity
min_jaccard_distance = 0.13


#%% 1. Load the JSON variables in the res folder.
input_file = open(working_directory + "res/" + "top_words_tfidf_web_Juni.json")
top_words_tfidf_web = json.load(input_file)
input_file.close()

input_file = open(working_directory + "res/" + "top_words_tfidf_orbit_Juni.json")
top_words_tfidf_orbit = json.load(input_file)
input_file.close()


#%% 2. Start exploring the JSON variables, which are dicts of dicts 
#Variables used to store the result
match_result_list = list() 
match_result_list_of_terms = list()

#top_words_tfidf contains websites as dictionary keys
website_index= 0 # Index only used for printouts
for website in top_words_tfidf_web: 
    #Index for printing
    website_index +=1
    webpage_index = 0 
    
    if verbose : 
        print "Starting to compare website : " + website + ". " + str(website_index) + " out of " + str(len(top_words_tfidf_web))
    #Each website contains webpages as dictionary keys
    for webpage in top_words_tfidf_web[website]:
        webpage_index += 1 #Index for printing
        if verbose and webpage_index % 200 == 0: 
            print "Starting to compare webpage : " + str(webpage_index) + " out of " + str(len(top_words_tfidf_web[website]))
        
        #Get the current web word list in a variable, it avoids repeating the long variable name everywhere
        if type(top_words_tfidf_web[website][webpage]) == list:
            web_word_list = top_words_tfidf_web[website][webpage]
        elif type(top_words_tfidf_web[website][webpage]) == dict:
            web_word_list = top_words_tfidf_web[website][webpage].keys()
        else: #If it is a single word, string or empty, we put it into a list
            web_word_list = [top_words_tfidf_web[website][webpage]]

        #Now start comparing the current page with every Orbit department->document->topwords.
        for orbit_department in top_words_tfidf_orbit:
            for orbit_document_id in top_words_tfidf_orbit[orbit_department]:
                
                #Get the current orbit word list in a variable, it avoids repeating the long variable name everywhere
                if type(top_words_tfidf_orbit[orbit_department][orbit_document_id]) == list:
                    orbit_word_list = top_words_tfidf_orbit[orbit_department][orbit_document_id]
                elif type(top_words_tfidf_orbit[orbit_department][orbit_document_id]) == dict:
                    orbit_word_list = top_words_tfidf_orbit[orbit_department][orbit_document_id].keys()
                else: #If it is a single word, string or empty, we put it into a list
                    orbit_word_list = [top_words_tfidf_orbit[orbit_department][orbit_document_id]]

                #Compute the jaccard similarity : 
                common_words = len(list(set(web_word_list).intersection(orbit_word_list)))
                words_total = len(web_word_list)+len(orbit_word_list)
                
                #Compute the jaccard distance. Remember to cast into float to get decimals
                jaccard_distance = float(common_words)/(words_total-common_words)
                
                # Minimum requirement test : 
                if (jaccard_distance * common_words) >= pass_criteria and jaccard_distance> min_jaccard_distance:
                    # Keep a list of the common terms
                    common_terms=list(set(web_word_list).intersection(orbit_word_list))
                    # Create a comparison list for the result: 
                    comparison_result = [website, webpage , orbit_department, orbit_document_id ,common_words, jaccard_distance, words_total, common_terms]
                    
                    #Check whether the result is not already in :
                    keep_comparison_result = True
                    for result in match_result_list : 
                        if result[0] == comparison_result[0] and result[3] == comparison_result[3] :
                            #tiebreak between the matches : 
                            if result[5] >= comparison_result[5] : 
                                keep_comparison_result = False
                            else : 
                                match_result_list.remove(result)
                    
                    if keep_comparison_result:                    
                        match_result_list.append(comparison_result)
                        print "New Match : Common words : ",
                        print common_terms
                
                    #Small printout in the console
                    if verbose : 
                        print "Number of matches : " + str(len(match_result_list))

    
#%% Post processing the result (re-ordering)    
for index in range(0,len(match_result_list)) : 
    # Remove some letters or whatever is in front at the beginning of orbit_department
    match_result_list[index][2] = match_result_list[index][2][4:-5]

# Sort the result after Jaccard distance
match_result_list = sorted(match_result_list, key=lambda result: result[5],reverse=True)


#%% Pick up the most common words in the result : 
most_common_words = dict()

for word_list in match_result_list_of_terms : 
    for word in word_list:
        if word in most_common_words:
            most_common_words[word] +=1
        else :
            most_common_words[word] = 1

most_common_words_list = list()
for word in most_common_words:
    most_common_words_list.append([word, most_common_words[word]])
    
most_common_words_list = sorted(most_common_words_list, key=lambda result: result[1],reverse=True)
    
#%% Export the result to a JSON variable
output_file = open(working_directory + "output/" + "consolidated_result.json",'w')
output_file.write(json.dumps(match_result_list))
output_file.close()

#output_file = open(working_directory + "output/" + "most_common_words_lis_new.json",'w')
#output_file.write(json.dumps(most_common_words_list))
#output_file.close()

## IN case of problem : 
#input_file = open(working_directory + "output/" + "match_result_list.json")
#match_result_list = json.load(input_file)
#input_file.close()


#%% Test : 
#input_file = open(working_directory + "output/" + "consolidated_result_new.json",'r')
#match_result_list = json.load(input_file)
#input_file.close()
#
#input_file = open(working_directory + "output/" + "most_common_words_lis_new.json",'r')
#most_common_words_list = json.load(input_file)
#input_file.close()
#
#filtered_match_result_list = match_result_list[:]
#for result1 in match_result_list:
#    for result2 in match_result_list:
#        if result1 != result2:
#            if result1[0] == result2[0] and result1[3] == result2[3]  : #Same website leading to the same paper
#                if result1[4] * result1[5] > result2[4] * result2[5] : 
#                    if result2 in filtered_match_result_list:
#                        filtered_match_result_list.remove(result2)
#                        print "There was something removed"
#                else : 
#                    if result1 in filtered_match_result_list:
#                        filtered_match_result_list.remove(result1)
#                        print "There was something removed"
#
#for result in match_result_list:
#    if result in filtered_match_result_list:
#        if result[5] < 0.13 : 
#            print result[5]
#            filtered_match_result_list.remove(result)
#
#for result in match_result_list:
#    if result in filtered_match_result_list:
#        if result[2] == '16' and result[3] == '28502' :
#            print "There was something removed"
#            filtered_match_result_list.remove(result)
#
#
#for result in match_result_list:
#    if result in filtered_match_result_list:
#        if 'ist' in result[7] or 'til' in result[7]  :
#            print "There was something removed"
#            filtered_match_result_list.remove(result)
#
#
#for result in filtered_match_result_list:
#    #if result[0] == "circ.ahajournals.org" : 
#    #    print result
#    print "website : " + result[0] + " Paper : " + result[3]
#    
#
#output_file = open(working_directory + "output/" + "2017_01_07_consolidated_result_second_pairs_filtered.json",'w')
#output_file.write(json.dumps(filtered_match_result_list))
#output_file.close()

