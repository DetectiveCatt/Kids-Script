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
		# self.code = self.code.replace('\n', ' ')
		code = shlex.split(self.code, posix=False)
		keywords = [
			'Load',
			'Add',
			'Print',
			'Store',
			'If',
			'EndIf',
			'Then'
		]
		for word in code:
			if word == 'program:':
				self.tokens.append(['Start', word])
			elif word in keywords:
				self.tokens.append(['KEYWORD',word])
			elif re.match('"([^\\"]| \\")*"',word):
				self.tokens.append(['STRING', word])
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
		func_times = 0
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
					t = {'If'+str(if_times):0}
					self.add_nood(parent,t)
					parent = token[1]+str(if_times)
					t = {'If' + str(if_times):[[],[]]}
					self.parsed.append(t)
					ifb = True
					if_times +=1
				elif token[0] == 'CMP OPERATOR' and token[1] == '=':
					if ifb == True:
						t = { "Expr":[ [tokens[token_index - 2][1], tokens[token_index - 1][1]],tokens[token_index][1], [tokens[token_index + 1][1],tokens[token_index + 2][1] ] ] }
						self.add_nood(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'EndIf':
					parent = 'program'
					t = {'program':[]}
					self.parsed.append(t)
					ifb = False
				elif token[0] == 'KEYWORD' and token[1] == 'Load':
					if ifb == False:
						t = {"Load": [ tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
						self.add_nood(parent, t)
					elif ifb == True:
						t = {"Load": [ tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
						self.add_noog(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'Print':
					if ifb == False:
						t = {"Print":[ tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
						self.add_nood(parent, t)
					elif ifb == True:
						t = {"Print":[ tokens[token_index + 1][1], tokens[token_index + 2][1] ]}
						self.add_noog(parent, t)

				elif token[0] == 'KEYWORD' and token[1] == 'Store':
					if ifb == False:
						t = { "Store":[ tokens[token_index + 1][1],tokens[token_index + 2][1] ] }
						self.add_nood(parent, t)
					elif ifb == True:
						t = { "Store":[ tokens[token_index + 1][1],tokens[token_index + 2][1] ] }
						self.add_noog(parent, t)
				elif token[0] == 'KEYWORD' and token[1] == 'Then':
					if ifb == True:
						t = { "Then":[]}
						self.add_nood(parent, t)
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
		

class Interpreter():
	def out(self,object1):
		if_times = 0
		for node in object1:
			# print("NODE ",node)
			for key , values in node.items():
				# print("KEY : VALUE ",key,values)
				
				if "If" in key:
					self.parse_if(key,values)
					# pass
				elif "program" in key:
					self.program(node['program'])
	def program(self, tokens):
		# print("program tokens",tokens)
		# print(tokens)
		for token in tokens:
			# print(token)
			for k,v in token.items():
				if k == 'Store' :
					name = v[1]
					value = v[0]
					vars[name] = value
				elif k == 'Load':
					name = v[1]
					value = v[0]
					stacks[name].append(value)
				elif k == 'If':
					self.parse_if(k,v)
				elif k == 'Print':
					self.parse_print(k,v)
	def parse_if(self,key,value):
		if_times = 0
		if "If" in key:
			then = value[3]['Then']
			expr = value[2]['Expr']
			num1 = expr[0]
			if num1[0] == 'var':
				num1 = vars[num1[1]]
			elif num1[0] == 'stack':
				num1 = stacks[num1[1]].pop()

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
			if_times += 1
			# print(key,value)
	def parse_print(self,key,value):
		if "Print" in key:
			if value[0] == 'var':
				item = vars[value[1]]
			elif value[0] == 'stack':
				item = stacks[value[1]].pop()
			print("print ",item)
			# if_times += 1
				

			
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
inter = Interpreter()
print("Final")
inter.out(parsed)