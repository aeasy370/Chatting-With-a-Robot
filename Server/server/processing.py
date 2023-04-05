from typing import List, Tuple
from enum import Enum
import json
import nltk
from nltk.tokenize import word_tokenize


def get_words(command: str) -> List[str]:
    '''
    takes a string as an argument, most likely a command to do something
    returns a list of every word in the command argument
    '''
    return word_tokenize(command)

def get_all_nouns(command: str) -> List[str]:
    '''
    takes a string as an argument, most likely a command to do something
    returns a list of every noun in the command argument
    '''
    return list(filter(lambda x: x[1] == "NN", get_words(command)))

def get_keywords(keywords: List[str], command: str) -> List[str]:
	'''
	1st argument: list of keywords that you want to be seen
	2nd argument: command you want to take the keywords from
	returns a list of the keywords seen in the command argument
	'''
	nouns = get_all_nouns(command)
	return list(filter(lambda n: n in keywords, nouns))

def process_keyword_file(filename: str) -> List[str]:
	keyword_dict = json.load(filename)
	def build_keywords(d):
		keys = []
		for key in d.keys():
			keys.append(key)
			if type(d[key]) == dict:
				keys += build_keywords(d[key])
	
	return build_keywords(keyword_dict)

class InvalidIntent(Exception):
	def __init__(self, verb=None, obj=None):
		self.verb = verb
		self.obj = obj
		if verb:
			super().__init__(f"invalid verb '{verb}'")
		elif obj:
			super().__init__(f"invalid intent object '{obj}'")
		else:
			super().__init__(f"invald intent (no further information)")
	
class IntentVerb(Enum):
	GET = 0

class IntentObject(Enum):
	OEE = 0
	ROBOT = 1
	SPEED = 2
	POWER = 3
	CURRENT = 4
	PROGRAM = 5
	GRIPPER = 6
	OPEN = 7
	CLOSED = 8
	PART_COUNT = 9
	GOOD = 10
	NO_GOOD = 11
	TOTAL = 12
	MACHINE = 13
	CYCLE_TIME = 14
	POWER_CONSUMPTION = 15
	STATE = 16
	ESTOP = 17
	PUSH_BUTTON = 18

class Intent:
	def __init__(self, verb: str, obj: str):
		if verb.lower() != "get":
			raise InvalidIntent(verb=verb)
		
		self.verb = IntentVerb.GET
		self.obj = IntentObject.OEE # just for now
		# TODO: map objs to variants of IntentObject


def get_text_intent(keywords: List[str], command: str) -> Intent:
	# TODO: make this smarter
	important_keywords = get_keywords(keywords, command)
	return Intent("get", important_keywords[0])
