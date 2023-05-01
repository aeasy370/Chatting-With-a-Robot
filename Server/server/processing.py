from typing import List, Optional
from enum import Enum
import json
import nltk
from nltk.tokenize import word_tokenize


nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


def get_words(command: str) -> List[str]:
    """takes a string as an argument, most likely a command to do something
    returns a list of every word in the command argument
    """
    t = list(map(str.lower, word_tokenize(command)))
    return t

def get_all_nouns(command: str) -> List[str]:
    """takes a string as an argument, most likely a command to do something
    returns a list of every noun in the command argument
    """
    x = nltk.pos_tag(get_words(command))
    t = list(filter(lambda x: x[1] == "NN" or x[1] == "JJ", x))
    return t

def get_keywords(keywords: List[str], command: str) -> List[str]:
	"""1st argument: list of keywords that you want to be seen
	2nd argument: command you want to take the keywords from
	returns a list of the keywords seen in the command argument
	"""
	nouns = get_all_nouns(command)
	return list(map(lambda n: n[0], filter(lambda n: n[0] in keywords, nouns)))


def read_keyword_file(filename: str) -> dict[str, str]:
	"""reads a keyword tree
	"""
	keyword_dict = json.load(open(filename))
	return keyword_dict


def process_keyword_file(tree: dict[str, str]) -> List[str]:
	"""builds a list of keywords based on a keyword file
	"""
	def build_keywords(d: dict):
		if type(d) != dict:
			return []
		keys = []
		for key in d.keys():
			keys.append(key)
			if type(d[key]) == dict:
				keys += build_keywords(d[key])
		
		return keys
	
	return build_keywords(tree)


def traverse_keyword_tree(tree: dict[str, str], keyword_seq: List[str]) -> Optional[str]:
	"""traverses a keyword tree in order of keys from `keyword_seq` to get the leaf
	returns `None` if the keyword sequence did not produce a valid diagnostic name
	"""
	cur = tree
	if keyword_seq == []:
		return None

	for k in keyword_seq:
		if type(cur) == str:
			return cur
		x = cur.get(k)
		if not x:
			return None
		cur = x
	
	return cur


def get_diagnostic_from_transcription(tree: dict[str, str], transcript: str) -> Optional[str]:
	"""parse a diagnostic name from a transcription
	"""
	all_keywords = process_keyword_file(tree)
	print(all_keywords)
	seq = get_keywords(all_keywords, transcript)
	print(transcript)
	print(seq)
	return traverse_keyword_tree(tree, seq)


if __name__ == "__main__":
	tree = read_keyword_file("../diagnostic.json")
	print(tree)
	x = process_keyword_file(tree)
	print(x)
	print(get_diagnostic_from_transcription(tree, "get the robot gripper open"))
