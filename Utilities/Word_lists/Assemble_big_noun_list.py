import os

word_file_directory = 'Swedish_noun_collection'
word_files = os.listdir(word_file_directory)

full_word_list = []
for word_file in word_files:
   f = open('{}/{}'.format(word_file_directory, word_file))
   words = [word.strip().lower() for word in f]
   f.close()
   full_word_list += words
   
full_word_list = sorted(list(set(full_word_list)))

f = open("Full_Swedish_noun_list.txt", "w")
for word in sorted(full_word_list):
   f.write('{}\n'.format(word))
f.close()
