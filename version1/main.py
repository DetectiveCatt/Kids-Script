# Imports here....
import re, shlex
# input file
filename = "input.raw"
file = open(filename, 'r')
# raw verion of what we want to execute
what_to_execute_raw = file.read()
file.close()

# internal data structures
stack1 = []
stack2 = []
stack3 = []
stack4 = []
stack5 = []
# dictionary to contain all dicts
stacks = {
	'stack1':stack1,
	'stack2':stack2,
	'stack3':stack3,
	'stack4':stack4,
	'stack5':stack5
}
# variable data type for language
vars = {}
# lexer class
class Lexer():
	def __init__(self,code):
		self.code = code
		# output tokens..
		self.tokens = []
	# main function
	def tokenize(self):
		#  make the code one string instead of different lines
		self.code = self.code.replace('\n', ' ')
		# split the words
		code = shlex.split(self.code)
		# keywords for the language
		keywords = [
			'Load',
			'Add',
			'Print',
			'Store'
		]
		# for each word do.....
		for word in code:
			# If we reach program then we know we have started the code
			if word == 'program':
				self.tokens.append(['Start', word])
			# got a keyword? lets add a token for it
			elif word in keywords:
				self.tokens.append(['KEYWORD',word])
			# for datatypes like var and stack add a token
			elif word == 'var':
				self.tokens.append(['VAR', word])
			elif word in ['stack1','stack2','stack3','stack4','stack5']:
				self.tokens.append(['STACK', word])

			# we got a number? add a token!!
			elif re.match('[0-9]', word):
				self.tokens.append(['INT',word])
			# got a string? add a token!
			elif re.match('["a-z"]', word) or re.match('["A-Z"]', word):
				self.tokens.append(['STRING',word])
			# got a ; ? statement has ended!
			elif word == ';':
				self.tokens.append(['STATEMENT_END',word])
		# give all the tokens to the program back..
		return self.tokens

# parse class..
class Parse():
	def __init__(self):
		self.parsed = []
	def parse(self, tokens):
		# token inedx to keep track of tokens
		token_index = 0

		# Go through the tokens one by one
		while token_index < len(tokens):
			# The token type and value in different variables
			# eg: token: NUMBER["TYPE", "VALUE"]
			#                  |token number|
			#                               |value|
			token_type = tokens[token_index][0]
			token_value = tokens[token_index][1]
			for token in tokens:
				# the tokens[token_index + ?] means we want to get the value after ? number of times
				# we got a load keyword? lets add it to the program.
				if token[0] == 'KEYWORD' and token[1] == 'Load':
					self.parsed.append({"Load": [ tokens[token_index + 1][1], tokens[token_index + 2][1] ]})
				# we got a print keyword? lets add it to the program..
				elif token[0] == 'KEYWORD' and token[1] == 'Print':
					self.parsed.append({"Print":[ tokens[token_index + 1][1], tokens[token_index + 2][1] ]})
				# we got a add keyword? lets add it to the program..
				elif token[0] == 'KEYWORD' and token[1] == 'Add':
					self.parsed.append( { "Add":[ [tokens[token_index + 1][1], tokens[token_index + 2][1]],[tokens[token_index + 3][1], tokens[token_index + 4][1]],[tokens[token_index + 5][1],tokens[token_index + 6][1]] ] } )
				# we got a store keyword? lets add it to the program..
				elif token[0] == 'KEYWORD' and token[1] == 'Store':
					self.parsed.append( { "Store":[ tokens[token_index + 1][1],tokens[token_index + 2][1] ] } )
				token_index += 1
			return self.parsed
# Interpreter class to well.. interprete our parsed object from parser
class Interpreter():
	def out(self,object1):
		# for every node... (eg: program, this will be handy afterwards)
		for node in object1:
			# key values, load, store...
			for key , values in node.items():
				# we got a load?? lets check what values to load and into what stack..
				if key == "Load":
					# we get values as a list so we can get a particular value by its index.
					# we know that we ask for the stack name and then the value
					# i is the stack number, v is the value
					# eg: Load stack[i] [v]
					stacks[values[1]].append(values[0])
					print(
						"Load parsed ",stacks
						)
				# Got a add? lets check what values to add..
				elif key == "Add":
					# we know that we ask for the stack or variable and then the output stack or variable
					# a is the first value,b is the second value, c is the output value
					# eg: Add [Data type] a [Data type] b [Data type] c
					token_num = 0
					num1 = 0
					num2 = 0
					for value in values:
						dtype = value[0]
						dvalue = value[1]	
						# Check the datatype and
						# Get values accordingly
						if dtype == 'stack' and token_num == 0:
							num1 += int(stacks[dvalue].pop())
						elif dtype == 'stack' and token_num == 1:
							num2 += int(stacks[dvalue].pop())
						elif dtype == 'stack' and token_num == 2:
							out = stacks[dvalue]
							out.append(num1 + num2)
						elif dtype == 'var' and token_num == 0:
							num1 += int(vars[dvalue])
						elif dtype == 'var' and token_num == 1:
							num2 += int(vars[dvalue])
						elif dtype == 'var' and token_num == 2:
							result = num1 + num2
							if dvalue in vars:
								vars[dvalue] = vars[dvalue] + result
							else:
								vars[dvalue] = result
						token_num += 1
				# Most simplest function...
				# Print!
				elif key == "Print":
					# Get the values accordingly
					if values[0] == 'stack':
						item = stacks[values[1]].pop()
					elif values[0] == 'var':
						item = vars[values[1]]
					print("Print parsed  ",item)
				# Store... 
				elif key == "Store":
					# Keep it in the vars dict, global variables
					vars[values[1]] = values[0]
					print(
						"Store parsed  ",
						"vars ", vars
						)

# Get a lexer object from the lex class
lex = Lexer(what_to_execute_raw)
# get tokens from the lexer
tokens = lex.tokenize()
# Print the tokens
print("lexer")
for token in tokens:
	print(token)
# Get a parser from the parse class
parse = Parse()
# Get the parsed object
parsed = parse.parse(tokens)
# Print the parsed object
print("parser")
for node in parsed:
	print(node)
# Get the interpreter from the interpreter class
inter = Interpreter()
# print the final output for the program entered in the what_to_execute_raw
print("Final")
inter.out(parsed)

# We have completed the basic interpreter for our language in just under 190 lines!
# We can extend this to make it more powerfull later on..