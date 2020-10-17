import re
filename = "input.raw"
file = open(filename, 'r')
data = file.read()
file.close()
what_to_execute_raw = data

stack1 = []
stack2 = []
stack3 = []
stack4 = []
stack5 = []
stacks = {
	'stack1':stack1,
	'stack2':stack2,
	'stack3':stack3,
	'stack4':stack4,
	'stack5':stack5
}
vars = {}
class Lexer():
	def __init__(self,code):
		self.code = code
		self.tokens = []

	def tokenize(self):
		self.code = self.code.replace('(', ' ')
		self.code = self.code.replace(')', ' ')
		self.code = self.code.replace(',', ' ')
		self.code = self.code.replace('\n', ' ')
		self.code = self.code.replace(';', ' ')
		# self.code = self.code.replace('\n', ' ')
		code = self.code.split()
		keywords = [
			'Load',
			'Add',
			'Print',
			'Store',
			'If',
			'EndIf',
			'end'
		]
		for word in code:
			if word == 'program:':
				self.tokens.append(['Start', word])
			elif word == 'end':
				self.tokens.append(['END',word])
			elif word in keywords:
				self.tokens.append(['KEYWORD',word])
			elif word in ['=', '>', '<', '<>']:
				self.tokens.append(['CMP OPERATOR', word])
			elif word in ['+', '-', '*', '/']:
				self.tokens.append(['MATH OPERATOR'])
			elif word == 'var':
				self.tokens.append(['VAR', word])
			elif word in ['stack1','stack2','stack3','stack4','stack5']:
				self.tokens.append(['STACK', word])
			elif word in ['stack','var']:
				self.tokens.append(['DATATYPE', word])
			elif re.match('[0-9]', word):
				self.tokens.append(['INT',word])
			elif re.match('["a-z"]', word) or re.match('["A-Z"]', word):
				self.tokens.append(['STRING',word])
			# elif word == ';':
			# 	self.tokens.append(['STATEMENT_END',word])
		return self.tokens
class Parse():
	def __init__(self):
		self.parsed = []
	def add_node(self, parent, t):
		for dicta in self.parsed:
			for key,  value in dicta.items():
				if parent == key:
					dicta[parent].append(t)

	def parse(self, tokens):
		token_index = 0
		parent = {}
		global if_times
		if_times = 0
		# [ { 'program:':[] } ]
		while token_index < len(tokens):
			for token in tokens:
				if token[0] == 'Start' and token[1] == 'program:':
					# parent = {token[1]:[]}
					# t = {token[1]}
					parent = token[1]
					t = {token[1]:[]}
					self.parsed.append(t)
					# self.add_node('program:', [])
					# 
					# self.add_node(parent, 'program:')
				elif token[0] == 'KEYWORD' and token[1] == 'EndIf':
					parent = 'program:'
					t = {'program:':[]}
					self.parsed.append(t)
				elif token[0] == 'END' and token[1] == 'end':
					break
				elif token[0] == 'CMP OPERATOR':
					t = {'Expr':[[tokens[token_index - 2][1], tokens[token_index - 1][1]], tokens[token_index][1], [tokens[token_index + 1][1],tokens[token_index + 2][1]]]}
					self.add_node(parent, t)
					parent = 'If ' + str(if_times) + " Code"
					t = {'If ' + str(if_times-1) + " Code":[]}
					self.parsed.append(t)
				elif token[0] == 'KEYWORD' and token[1] == 'Load':
					t = {'Load':[tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
					self.add_node(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'Print':
					t = {'Print':[ tokens[token_index + 1][1], tokens[token_index +2][1]]}
					self.add_node(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'Add':
					t =  { "Add":[ [tokens[token_index + 1][1], tokens[token_index + 2][1]],[tokens[token_index + 3][1], tokens[token_index + 4][1]],[tokens[token_index + 5][1],tokens[token_index + 6][1]] ] }
					self.add_node(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'Store':
					t =  { "Store":[ tokens[token_index + 1][1],tokens[token_index + 2][1] ] } 
					self.add_node(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'If':
					# ts = self.if_par(token_index, tokens)
					# tks = []
					# for i in range(ts):
					# 	tks.append(tokens[token_index + i][1])
					# t =  { "IF":[ tks ] }
					t = {'If':if_times}
					self.add_node(parent, t)
					parent = token[1] + " " + str(if_times)
					t = { token[1] +" "+ str(if_times):[] }
					self.parsed.append(t)
					if_times += 1 
					# self.add_node(parent, t)
					# parent = token[1]
					# t = {token[1]:[]}
					# self.parsed.append(t)
				token_index += 1
			return self.parsed
	def if_par(self, token_index, tokens):
		token_numbers = 0
		for token in tokens:
			if tokens[token_index + token_numbers][1] == 'EndIf':
				# token_numbers +=1
				break
			elif tokens[token_index + token_numbers][1] == 'If':
				pass
			token_numbers +=1
		return token_numbers
class Interpreter():
	def out(self,object1):
		code = object1[0]
		node_idx = 0
		# print("code ,", code)
		while node_idx < len(code['program:']):
			# print(code['program:'][node_idx])
			node = code['program:'][node_idx]
			global value
			for key, value in node.items():
				# print("key ",key, "value ",value)
				if key == 'Store':
					vars[value[1]] = value[0]
				elif key == 'Load':
					stacks[value[1]].append(value[0])
				elif key == 'Print':
					if value[0] == 'var':
						print(vars[value[1]])
					elif value[0] == 'stack':
						print(stacks[value[1]].pop()[1:-1])
				elif key == 'If':
					print(key)
					print(value)
					name = key +" "+ str(value)
					item1_value = 0
					item2_value = 0
					if_b = False
					for i in range(len(object1)):
						for key, items in object1[i].items():
							if key == name:
								# print(items[0]['Expr'])
								item1 = items[0]['Expr'][0]
								oper1 = items[0]['Expr'][1]
								item2 = items[0]['Expr'][2]
								if item1[0] == 'var':
									# print("var",item1)
									item1_value = "item1 value",vars[item1[1]]
								if item1[0] == 'stack':
									# print("stack",item1)
									pass
								if item2[0] == 'var':
									# print("var",item2)
									item2_value = "item1 value",vars[item1[1]]
								if item2[0] == 'stack':
									# print("stack",item2)
									pass
								if oper1 == '=':
									if item1[1] == item2[1]:
										if_b = True
									else:
										if_b = False
								if if_b == True:
									pass
								
								for key, items in object1[2].items():
									print(key)
									# print("If " + str(value + 1) + " Code")
									if "If" in key and "Code" in key and str(value + 1) in key:
										print("HEUU")
								# print(object1)
								# print(item2[0])
					# for i in range(len(object1)):
					# 	print(object1[i])
						# if name in object1[i].items():
						# 	print("If parer's fsdofidnf  ",code[name])
			node_idx +=1

			
lex = Lexer(what_to_execute_raw)
tokens = lex.tokenize()
print("lexer")
for token in tokens:
	print(token)
parse = Parse()
parsed = parse.parse(tokens)
print("parser")
# print(parsed)
for node in parsed:
	for key, value in node.items():
		print(key, value)
inter = Interpreter()
print("Final")
inter.out(parsed)