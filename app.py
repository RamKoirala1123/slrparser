from itertools import zip_longest
from flask import Flask, render_template, request
import copy

app = Flask(__name__)

# global rules

def augmentgrammar(grammars):
    global start_symbol
    augmentedgrammar = []
    start_symbol = grammars[0].split("->")[0].strip()
    augchar = start_symbol + "'"
    augmentedgrammar.append([augchar, ['.', start_symbol]])
    print(grammars)
    for grammar in grammars:
        list = grammar.split("->")
        print(list)
        l = list[0].strip()
        r = list[1].strip()
         
        # if the righthand side contains '|' symbol, split it and add it to the list
        multirhs = r.split('|')
        for r in multirhs:
            r = r.strip().split()
            r.insert(0, '.')
            augmentedgrammar.append([l, r])
    return augmentedgrammar
 

def findClosure(input_state, dotSymbol):
	global start_symbol, \
		separatedRulesList, \
		statesDict
	closureSet = []
	if dotSymbol == start_symbol:
		for rule in separatedRulesList:
			if rule[0] == dotSymbol:
				closureSet.append(rule)
	else:
		closureSet = input_state
	prevLen = -1
	while prevLen != len(closureSet):
		prevLen = len(closureSet)
		tempClosureSet = []
		for rule in closureSet:
			indexOfDot = rule[1].index('.')
			if rule[1][-1] != '.':
				dotPointsHere = rule[1][indexOfDot + 1]
				for in_rule in separatedRulesList:
					if dotPointsHere == in_rule[0] and \
							in_rule not in tempClosureSet:
						tempClosureSet.append(in_rule)
		for rule in tempClosureSet:
			if rule not in closureSet:
				closureSet.append(rule)
	return closureSet


def compute_GOTO(state):
	global statesDict, stateCount
	generateStatesFor = []
	for rule in statesDict[state]:
		if rule[1][-1] != '.':
			indexOfDot = rule[1].index('.')
			dotPointsHere = rule[1][indexOfDot + 1]
			if dotPointsHere not in generateStatesFor:
				generateStatesFor.append(dotPointsHere)
	if len(generateStatesFor) != 0:
		for symbol in generateStatesFor:
			GOTO(state, symbol)
	return


def GOTO(state, charNextToDot):
	global statesDict, stateCount, stateMap
	newState = []
	for rule in statesDict[state]:
		indexOfDot = rule[1].index('.')
		if rule[1][-1] != '.':
			if rule[1][indexOfDot + 1] == \
					charNextToDot:
				shiftedRule = copy.deepcopy(rule)
				shiftedRule[1][indexOfDot] = \
					shiftedRule[1][indexOfDot + 1]
				shiftedRule[1][indexOfDot + 1] = '.'
				newState.append(shiftedRule)
	addClosureRules = []
	for rule in newState:
		indexDot = rule[1].index('.')
		if rule[1][-1] != '.':
			closureRes = \
				findClosure(newState, rule[1][indexDot + 1])
			for rule in closureRes:
				if rule not in addClosureRules \
						and rule not in newState:
					addClosureRules.append(rule)
	for rule in addClosureRules:
		newState.append(rule)
	stateExists = -1
	for state_num in statesDict:
		if statesDict[state_num] == newState:
			stateExists = state_num
			break
	if stateExists == -1:
		stateCount += 1
		statesDict[stateCount] = newState
		stateMap[(state, charNextToDot)] = stateCount
	else:
		stateMap[(state, charNextToDot)] = stateExists
	return


def generateStates(statesDict):
	prev_len = -1
	called_GOTO_on = []
	while (len(statesDict) != prev_len):
		prev_len = len(statesDict)
		keys = list(statesDict.keys())
		for key in keys:
			if key not in called_GOTO_on:
				called_GOTO_on.append(key)
				compute_GOTO(key)
	return


def first(rule, visited=None):
    global rules, nonterm_userdef, term_userdef, diction, firsts

    if visited is None:
        visited = set()

    if rule[0] in term_userdef:
        return [rule[0]]
    elif rule[0] == '#':
        return ['#']

    if rule[0] in visited:
        # To handle left recursion
        return []

    visited.add(rule[0])
    
    if rule[0] in list(diction.keys()):
        fres = []
        rhs_rules = diction[rule[0]]
        for itr in rhs_rules:
            indivRes = first(itr, visited)
            if type(indivRes) is list:
                fres.extend(indivRes)
            else:
                fres.append(indivRes)

        visited.remove(rule[0])

        if '#' not in fres:
            return fres
        else:
            newList = []
            fres.remove('#')
            if len(rule) > 1:
                ansNew = first(rule[1:], visited)
                if ansNew:
                    if type(ansNew) is list:
                        newList = fres + ansNew
                    else:
                        newList = fres + [ansNew]
                else:
                    newList = fres
                return newList
            fres.append('#')
            return fres

    visited.remove(rule[0])
    return []

def follow(nt):
	global start_symbol, rules, nonterm_userdef, \
		term_userdef, diction, firsts, follows
	solset = set()
	if nt == start_symbol:
		solset.add('$')
	for curNT in diction:
		rhs = diction[curNT]
		for subrule in rhs:
			if nt in subrule:
				while nt in subrule:
					index_nt = subrule.index(nt)
					subrule = subrule[index_nt + 1:]
					if len(subrule) != 0:
						res = first(subrule)
						if '#' in res:
							newList = []
							res.remove('#')
							ansNew = follow(curNT)
							if ansNew != None:
								if type(ansNew) is list:
									newList = res + ansNew
								else:
									newList = res + [ansNew]
							else:
								newList = res
							res = newList
					else:
						if nt != curNT:
							res = follow(curNT)
					if res is not None:
						if type(res) is list:
							for g in res:
								solset.add(g)
						else:
							solset.add(res)
	return list(solset)


def createParseTable(statesDict, stateMap, T, NT):
	global separatedRulesList, diction, Table, cols, numbered
	rows = list(statesDict.keys())
	cols = T+['$']+NT
	Table = []
	tempRow = []
	for y in range(len(cols)):
		tempRow.append('')
	for x in range(len(rows)):
		Table.append(copy.deepcopy(tempRow))
	for entry in stateMap:
		state = entry[0]
		symbol = entry[1]
		a = rows.index(state)
		b = cols.index(symbol)
		if symbol in NT:
			Table[a][b] = Table[a][b]\
				+ f"{stateMap[entry]} "
		elif symbol in T:
			Table[a][b] = Table[a][b]\
				+ f"S{stateMap[entry]} "
	numbered = {}
	key_count = 0
	for rule in separatedRulesList:
		tempRule = copy.deepcopy(rule)
		tempRule[1].remove('.')
		numbered[key_count] = tempRule
		key_count += 1
	addedR = f"{separatedRulesList[0][0]} -> " \
		f"{separatedRulesList[0][1][1]}"
	rules.insert(0, addedR)
	for rule in rules:
		k = rule.split("->")
		k[0] = k[0].strip()
		k[1] = k[1].strip()
		rhs = k[1]
		multirhs = rhs.split('|')
		for i in range(len(multirhs)):
			multirhs[i] = multirhs[i].strip()
			multirhs[i] = multirhs[i].split()
		diction[k[0]] = multirhs
	for stateno in statesDict:
		for rule in statesDict[stateno]:
			if rule[1][-1] == '.':
				temp2 = copy.deepcopy(rule)
				temp2[1].remove('.')
				for key in numbered:
					if numbered[key] == temp2:
						follow_result = follow(rule[0])
						for col in follow_result:
							index = cols.index(col)
							if key == 0:
								Table[stateno][index] = "Accept"
							else:
								Table[stateno][index] =\
									Table[stateno][index]+f"R{key} "
	print("\nSLR(1) parsing table:\n")
	frmt = "{:>8}" * len(cols)
	print(" ", frmt.format(*cols), "\n")
	ptr = 0
	j = 0
	for y in Table:
		frmt1 = "{:>8}" * len(y)
		print(f"{{:>3}} {frmt1.format(*y)}"
			.format('I'+str(j)))
		j += 1

# rules = ["S -> a X d | b Y d | a Y e | b X e",
#          "X -> c",
#          "Y -> c"
#          ]
# rules = ["E -> E + T | T",
# 		"T -> T * F | F",
# 		"F -> ( E ) | id"
# 		]


# nonterm_userdef = ['E', 'T', 'F']
# term_userdef = ['id', '+', '*', '(', ')']
# start_symbol = nonterm_userdef[0]

def extract_symbols(rules):
    terminal_symbols = []
    non_terminal_symbols = []

    for rule in rules:
        parts = rule.split(' -> ')
        if len(parts) == 2:
            lhs = parts[0].strip()
            rhs = parts[1].strip()

            # Add the left-hand side to non-terminals
            if lhs not in non_terminal_symbols:    
                non_terminal_symbols.append(lhs)
            # Add the right-hand side symbols to terminals and non-terminals
            for symbol in rhs.split():
                if not symbol == '|':
                    # if(symbol in non_terminal_symbols):
                    #     print('the symbol',symbol,'is already in ',non_terminal_symbols)
                    if not symbol.isupper() and symbol not in terminal_symbols:
                        terminal_symbols.append(symbol)
                    elif symbol.isupper() and symbol not in non_terminal_symbols:
                        non_terminal_symbols.append(symbol)


    return terminal_symbols, non_terminal_symbols

# term_userdef, nonterm_userdef = extract_symbols(rules)

# print('the sym ', extract_symbols(rules), term_userdef,nonterm_userdef)
# nonterm_userdef = ['S','X','Y']
# term_userdef = ['a','b','c','d','e']
# start_symbol = nonterm_userdef[0]	

# separatedRulesList = augmentgrammar(rules)
# start_symbol = separatedRulesList[0][0]

# I0 = findClosure(0, start_symbol)

# global nonterm_userdef, firsts
    # print("\nFirst sets:\n")
# statesDict = {}
# stateMap = {}

# statesDict[0] = I0
# stateCount = 0

# generateStates(statesDict)

# diction = {}

# createParseTable(statesDict, stateMap,
# 				term_userdef,
# 				nonterm_userdef)

# result_list = []
# for nonterm in nonterm_userdef:
#     first_set = set(first(nonterm))
#     firsts= '{' + ', '.join(map(str, first_set)) + '}'
#     follow_set = set(follow(nonterm))
#     follows = '{' + ', '.join(map(str, follow_set)) + '}'
#     result_list.append([nonterm, firsts,follows])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Get the form data
        grammar_text = request.form.get('grammartext')
        print(grammar_text)
        grammar_list = [line.strip() for line in grammar_text.split('\n') if line.strip()]

        augmentedgrammar = augmentgrammar(grammar_list)
        global term_userdef, nonterm_userdef, start_symbol, separatedRulesList, statesDict, stateMap,stateCount,diction,rules,Table,cols,numbered
        term_userdef, nonterm_userdef = extract_symbols(grammar_list)
        print('the is', term_userdef,nonterm_userdef)
        rules = grammar_list
        separatedRulesList = augmentgrammar(rules)
        start_symbol = separatedRulesList[0][0]

        I0 = findClosure(0, start_symbol)

        statesDict = {}
        stateMap = {}

        statesDict[0] = I0
        stateCount = 0

        generateStates(statesDict)

        diction = {}

        createParseTable(statesDict, stateMap, term_userdef, nonterm_userdef)

        result_list = []
        for nonterm in nonterm_userdef:
            first_set = set(first(nonterm))
            firsts = '{' + ', '.join(map(str, first_set)) + '}'
            follow_set = set(follow(nonterm))
            follows = '{' + ', '.join(map(str, follow_set)) + '}'
            result_list.append([nonterm, firsts, follows])


        input_string = "id + id * id"
        input_tokens = input_string.split()
        input_tokens.append('$')
        stack = [0]
        parsing_steps = []
        i=0

        while True:
            state = stack[-1]
            current_token = input_tokens[i]

            action = Table[state][cols.index(current_token)]

            if 'S' in action:
            # Shift
                nextState = int(action[1:])
                stack.append(current_token)
                stack.append(nextState)
                i += 1
                parsing_steps.append((f"{' '.join(map(str, stack))}", current_token, f"Shift{nextState}", ""))
            elif 'R' in action:
            # Reduce
                rule_num = int(action[1:])
                rule = numbered[rule_num]
                for _ in range(len(rule[1])):
                    stack.pop()
                    stack.pop()
                goto_state = Table[stack[-1]][cols.index(rule[0])]
                stack.append(rule[0])
                stack.append(int(goto_state))
                parsing_steps.append((f"{' '.join(map(str, stack))}", "", f"Reduce{rule_num}", f"Goto{goto_state}"))
            elif action == 'Accept':
                parsing_steps.append((f"{' '.join(map(str, stack))}", "", "Accept", ""))
                break
            else:
            # Error
                parsing_steps.append((f"{' '.join(map(str, stack))}", "", "Error", ""))
                break

        # stack = [0]  # Initialize stack with the initial state
        # parsing_steps = []  # List to store parsing steps

        # i = 0
    #     while True:
    #         state = stack[-1]
    #         current_token = input_tokens[i]

    #         action = Table[state][cols.index(current_token)]

    #         if 'S' in action:
    #         # Shift
    #             nextState = int(action[1:])
    #             stack.append(current_token)
    #             stack.append(nextState)
    #             i += 1
    #             parsing_steps.append((f"{' '.join(map(str, stack))}", current_token, f"Shift{nextState}"))
    #         elif 'R' in action:
    #         # Reduce
    #             rule_num = int(action[1:])
    #             rule = numbered[rule_num]
    #             for _ in range(len(rule[1])):
    #                 stack.pop()
    #                 stack.pop()
    #             goto_state = Table[stack[-1]][cols.index(rule[0])]
    #             stack.append(rule[0])
    #             stack.append(int(goto_state))
    #             parsing_steps.append((f"{' '.join(map(str, stack))}", current_token, f"Reduce{rule_num} Goto{goto_state}"))
    #         elif action == 'Accept':
    #             parsing_steps.append((f"{' '.join(map(str, stack))}", current_token, "Accept"))
    #             break
    #         else:
    #         # Error
    #             parsing_steps.append((f"{' '.join(map(str, stack))}", current_token, "Error"))
    #             break

    # # Combine stack, input, and action into a single list for easier rendering in the template
        combined_steps = list(zip_longest(parsing_steps, input_tokens[i:], fillvalue=''))

       
        return render_template('index.html',augmentedgrammar = augmentedgrammar, grammar_text = grammar_text, data=result_list, terminal = term_userdef, nonterminal = nonterm_userdef, table =Table, input_string = input_string, input_tokens = input_tokens, parsing_steps=combined_steps)

@app.route('/parse', methods=['POST'])
def parse():
    user_input = request.form['grammar']
    print([user_input])
    # result = process_grammar(user_input)
    result = augmentgrammar([user_input])
    return render_template('index.html', grammar=user_input, result=result)

if __name__ == '__main__':
    app.run(debug=True)
