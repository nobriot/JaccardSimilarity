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
input_file = open(working_directory + "res/" + "top_words_tfidf_web_new.json")
top_words_tfidf_web = json.load(input_file)
input_file.close()

input_file = open(working_directory + "res/" + "top_words_tfidf_orbit_1.json")
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
        
        try : 
            #Get the current web word list in a variable, it avoids repeating the long variable name everywhere
            web_word_list = top_words_tfidf_web[website][webpage].keys()

            #Now start comparing the current page with every Orbit department->document->topwords.
            for orbit_department in top_words_tfidf_orbit:
                for orbit_document_id in top_words_tfidf_orbit[orbit_department]:

                    #Get the current orbit word list in a variable, it avoids repeating the long variable name everywhere
                    orbit_word_list = top_words_tfidf_orbit[orbit_department][orbit_document_id].keys()

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

                        #Small printout in the console
                        if verbose : 
                            print "Number of matches : " + str(len(match_result_list))
        except Exception as e:
            if verbose : 
                print "Exception thrown in jaccard comparison : %s" % e #In case an error happened, just skip the comparison
                
    


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


#%% Initial R Code 
### : 
## the outer loop is web and the inner is orbit- as orbit has less different coprora (21)
#ind= 0
#for (item in 59:117){
#  # to find the web corpus name
#  name_of_dtm<-(names(top_words_tfidf_web_1[item]))
#  
#  for (row_doc in 1:nrow(as.matrix(top_words_tfidf_web_1[[item]]))){
#    print(paste('start', row_doc, 'from', item))
#    # find the single doc back
#    name_of_doc<- row.names(as.matrix(top_words_tfidf_web_1[[item]])) [row_doc]
#    the_best_per_doc<- as.matrix(unlist(top_words_tfidf_web_1[[item]][[row_doc]]))
#    words_for_web<-rownames(the_best_per_doc)
#    
#    
#    for( dp in 1:length(top_words_tfidf_orbit_1) ) {
#      #Find which department corpus
#      name_of_dtm_orbit<-(names(top_words_tfidf_orbit_1[dp]))
#      #nam2<-list()
#      for (row_doc_2 in 1:nrow(as.matrix(top_words_tfidf_orbit_1[[dp]]))){
#        #Find ID for the doc
#        name_of_doc_orbit<- row.names(as.matrix(top_words_tfidf_orbit_1[[dp]])) [row_doc_2]
#        the_best_per_doc_orbit<- as.matrix(unlist(top_words_tfidf_orbit_1[[dp]][[row_doc_2]]))
#        words_for_orbit<-rownames(the_best_per_doc_orbit)
#        # we compare and calculate Jaccard:
#        
#        common_words<-length(intersect(words_for_orbit,words_for_web))
#        distance<- common_words/(length(words_for_orbit)+length(words_for_web)-common_words)
#        #we find total words
#        words_total<-length(words_for_web)+length(words_for_orbit)
#        
#        #we find the real terms:to ensure we found the right docs containing these words!
#        common_terms<-intersect(words_for_orbit,words_for_web)
#        
#        #name<-paste0("tp", name_of_doc_orbit)
#        comparison<-c(name_of_dtm, name_of_doc , dp, name_of_doc_orbit ,common_words, distance, words_total)
#        
#        #we set the threshold:
#        if ((distance* common_words)>=(0.15 * 7)){
#          ind= ind+1
#          print(ind)
#          name1<-paste0('dp',dp, sep= '_', ind)
#          
#          name2<-paste('number', ind)
#          pair_list1[[name2]]<-comparison
#          list_of_terms_1[[name2]]<-common_terms
#        }
#      } 
#      
#    }
#  }
#}
#
## we  save the list:
#save(pair_list1, file = 'new_pairs')
#
