import re, shlex
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
		code = shlex.split(self.code, posix=False)
		keywords = [
			'Load',
			'Print',
			'Store',
			'If',
			'EndIf',
			'Then',
			'Func',
			'EndFunc'
		]
		for word in code:
			# print(word[:-2])
			if word == 'program:':
				self.tokens.append(['Start', word])
			elif word in keywords:
				self.tokens.append(['KEYWORD',word])
			elif re.match('"([^\\"]| \\")*"',word):
				self.tokens.append(['STRING', word])
			elif word[-2:] == '()':
				self.tokens.append(['FUNC_CALL', word])
			elif word == 'var':
				self.tokens.append(['VAR', word])
			elif word in ['=', '>', '<', '<>']:
				self.tokens.append(['CMP OPERATOR', word])
			elif word in ['+', '-', '*', '/']:
				self.tokens.append(['MATH OPERATOR'])
			elif word in ['stack1','stack2','stack3','stack4','stack5']:
				self.tokens.append(['STACK', word])
			elif word in ['stack','var']:
				self.tokens.append(['DATATYPE', word])
			elif re.match('[0-9]', word):
				self.tokens.append(['INT',word])
			elif re.match('"([^\\"]| \\")*"', word):
				self.tokens.append(['INT', word])
			elif re.match('["a-z"]', word) or re.match('["A-Z"]', word):
				self.tokens.append(['IDENTIFIER',word])

		return self.tokens

class Parse():
	def __init__(self):
		self.parsed = []
	def parse(self, tokens):
		token_index = 0
		ifb = False
		funcb = False
		parent = {}
		global if_times, func_times
		if_times = 0
		while token_index < len(tokens):
			token_type = tokens[token_index][0]
			token_value = tokens[token_index][1]
			for token in tokens:
				# print(token)
				if token[0] == 'Start' and token[1] == 'program:':
					parent = token[1][:-1]
					name = 'program'
					t = {name:[]}
					self.parsed.append(t)
				elif token[0] == 'KEYWORD' and token[1] == 'If':
					t = {'If':str(if_times)}
					self.add_nood(parent,t)
					parent = token[1]+str(if_times)
					t = {'If'+str(if_times) : [[],[]]}
					self.parsed.append(t)
					ifb = True
					if_times +=1
				elif token[0] == 'CMP OPERATOR' and token[1] == '=':
					# if ifb == False:
					# 	t = { "Expr":[ [tokens[token_index - 1][1], tokens[token_index - 2][1]],tokens[token_index][1], [tokens[token_index + 1][1]],[tokens[token_index + 2][1],tokens[token_index + 3][1]] ] }
					# 	self.add_node(parent, t)
					if ifb == True:
						t = { "Expr":[ [tokens[token_index - 2][1], tokens[token_index - 1][1]],tokens[token_index][1], [tokens[token_index + 1][1],tokens[token_index + 2][1] ] ] }
						self.add_nood(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'EndIf':
					parent = 'program'
					# t = {'program':[]}
					# self.parsed.append(t)
					ifb = False
				elif token[0] == 'KEYWORD' and token[1] == 'EndFunc':
					parent = 'program'
					# t = {'program':[]}
					# self.parsed.append(t)
					funcb = False
				elif token[0] == 'KEYWORD' and token[1] == 'Load':
					# print("LOAD")
					t = {"Load": [ tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
					if ifb == True:
						self.add_noog(parent, t)
					elif funcb == True:
						self.add_func_node(parent,t)
					else:
						self.add_nood(parent,t)
				elif token[0] == 'KEYWORD' and token[1] == 'Print':
					t = {"Print":[ tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
					if ifb == True:
						self.add_noog(parent, t)
					elif funcb == True:
						self.add_func_node(parent,t)
					else:
						self.add_nood(parent,t)

				
				elif token[0] == 'KEYWORD' and token[1] == 'Func':
					t = {'FuncMake'+str(tokens[token_index + 1][1]):0}
					self.add_nood(parent,t)
					parent = "FuncMake"+str(tokens[token_index + 1][1])
					t = {'FuncMake' + str(tokens[token_index + 1][1]):[]}
					self.parsed.append(t)
					funcb = True

				elif token[0] == 'KEYWORD' and token[1] == 'Store':
					t = { "Store":[ tokens[token_index + 1][1],tokens[token_index + 2][1] ] }
					if ifb == True:
						self.add_noog(parent, t)
					elif funcb == True:
						self.add_func_node(parent,t)
					else:
						self.add_nood(parent,t)
				elif token[0] == 'KEYWORD' and token[1] == 'Then':
					if ifb == True:
						t = {"Then":[]}
						self.add_nood(parent, t)
				elif token[0] == 'FUNC_CALL':
					t = { "FuncCall":token[1] }
					if ifb == True:
						self.add_noog(parent, t)
					elif funcb == True:
						self.add_func_node(parent,t)
					else:
						self.add_nood(parent,t)
				token_index += 1
		return self.parsed

	def add_nood(self, parent, t):
		for dicta in self.parsed:
			for key,  value in dicta.items():
				if parent == key:
					dicta[parent].append(t)
	def add_noog(self, parent, t):
		for dicta in self.parsed:
			for key,  value in dicta.items():
				if parent in key:
					dicta[parent][3]['Then'].append(t)
	def add_func_node(self,parent,t):
		for dicta in self.parsed:
			for key,  value in dicta.items():
				if parent in key:
					dicta[parent].append(t)
		

class Interpreter():
	def __init__(self,object1):
		self.object1 = object1
	def out(self):
		object1 = self.object1
		if_times = 0
		for node in object1:
			# print("NODE ",node)
			for key , values in node.items():
				# print("KEY : VALUE ",key,values)
				
				# if "If" in key:
				# 	self.parse_if(key,values)
					# pass
				if "program" in key:
					self.program(node['program'])
				# elif 
	def parse_if_func(self,k,v):
		for node in self.object1:
			# print("NODE",node)
			for k2,v2 in node.items():
				# print("KEY VALUE",k2,v2)
				if k in k2:
					# print("KEY FOUND",k2)
					self.parse_if(k2,v2,v)
				pass
	def func_call(self,key2,value2):
		for node in self.object1:
			# print("NODE ",node)
			
			# print('FuncMake'+value2[:-2])
			for key , value in node.items():
				# print(key)
				if 'FuncMake'+value2[:-2] in key:
					for token in value:
						for k,v in token.items():
							if k == 'Print':
								self.parse_print(k,v)
							if k == 'Load':
								self.parse_load(k,v)
							if k == 'Store':
								self.parse_store(k,v)
							if 'If' in k:
								# print("IIIFFF")
								self.parse_if_func(k,v)
				pass
			# break
	def program(self, tokens):
		# print("program tokens",tokens)
		# print(tokens)
		for token in tokens:
			# print(token)
			for k,v in token.items():
				# print("program:",k,v)
				if k == 'Store' :
					# print("store",token)
					name = v[1]
					value = v[0]
					# print(name, " = ", value)
					vars[name] = value
					# print(vars)
				elif k == 'Load':
					name = v[1]
					value = v[0]
					stacks[name].append(value)
					print(stacks)
				elif 'If' in k:
					# print("If:",k,v)
					self.parse_if_func(k,v)
				elif k == 'Print':
					self.parse_print(k,v)
				elif 'FuncCall' in k:
					# print(k,v)
					self.func_call(k,v)

	def parse_if(self,key,value,if_time):
		time = if_time
		# if_times = 0
		print("IF")
		if "If" in key:
			then = node["If" + str(time)][3]['Then']
			expr = node["If" + str(time)][2]['Expr']
			# then = value[3]['Then']
			# expr = value[2]['Expr']
			# print(then, expr)
			num1 = expr[0]
			if num1[0] == 'var':
				num1 = vars[num1[1]]
			elif num1[0] == 'stack':
				num1 = stacks[num1[1]].pop()
				# print(stacks)

			num2 = expr[2]
			if num2[0] == 'var':
				num2 = vars[num2[1]]
			elif num2[0] == 'stack':
				num2 = stacks[num2[1]].pop()
				# print(stacks)
			# print(num1, num2)
			if expr[1] == '=':
				if num1 == num2:
					for token in then:
						for k,v in token.items():
							if k == 'Print':
								self.parse_print(k,v)
							elif k == 'Store':
								name = v[1]
								value = v[0]
								vars[name] = value
							elif k == 'Load':
								name = v[1]
								value = v[0]
								stacks[name].append(value)
							elif 'FuncCall' in k:
								# print("FUNC IN IF")
								self.func_call(k,v)
			# if_times += 1
			# print(key,value)
	def parse_print(self,key,value):
		if "Print" in key:
			if value[0] == 'var':
				item = vars[value[1]]
			elif value[0] == 'stack':
				item = stacks[value[1]].pop()
			print(item)
		# print("print",value)
	def parse_load(self,k,v):
		item = v[0]
		stack = v[1]
		stacks[stack].append(item)
		# print(stacks)
	def parse_store(self,k,v):
		print("store",v)
		vars[v[1]] = v[0]

			
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
	print(node)
inter = Interpreter(parsed)
print("Final")
inter.out()