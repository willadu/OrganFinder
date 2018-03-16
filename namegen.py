import random 
def buildNameDictionaries():
	with open('firstnames.txt') as f:
	    content = f.readlines()
	first = [x.strip() for x in content]

	with open('lastnames.txt') as f:
	    content = f.readlines()
	last = [x.strip() for x in content]

	return first, last

def nameGenerator(first_dictionary, last_dictionary):
	first_ind = random.randint(0, len(first_dictionary)- 1)
	first = first_dictionary[first_ind]

	last_ind = random.randint(0, len(first_dictionary) - 1)
	last = last_dictionary[last_ind]

	return first + ' ' + last

#first_dict, last_dict = buildNameDictionaries()
#print(nameGenerator(first_dict, last_dict))