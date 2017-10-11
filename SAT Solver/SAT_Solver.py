import random
from operator import pos

positiveLiterals = set()
negativeLiterals = set()
finalResults =""

def main():
    inpath = "input.txt"
    input = readInput(inpath)
    global positiveLiterals
    global negativeLiterals
    global finalResults
    numGuests=int(input[0].rstrip())
    numTables=int(input[1].rstrip())
    relationList=input[2]
    atLeast1TableClauses=assignAtLeast1Table(numGuests,numTables)
    # print "atleast 1 table " + str(atLeast1TableClauses)
    assignOnly1tableClauses=assignOnly1table(numGuests,numTables)
    # print "atleast atmost 1 table " + str(assignOnly1tableClauses)
    relationClause=buildRelationClauses(relationList,numTables)
    # print "atleast release clauses " + str(relationClause)
    sentence = uniteLists(atLeast1TableClauses,assignOnly1tableClauses,relationClause)
    # print sentence
    result = DPLL_SAT(sentence)
    if not result:
        finalResults = "no"
    writeOutput(finalResults)
    # lite = '~X1*10'
    # res = lite.split('*')
    # print res
    # print res[0].split('X')
    # print res[0].split('X')[0]=='~'

def readInput(inpath):
    f = open(inpath, 'r')
    partySize=f.readline() #reads people and tables
    numGuests,numTables = partySize.split(" ");
    friendShipData = f.readlines();# returns a list of all lines
    relationList=[]
    for pair in friendShipData:
        first,second,relation=pair.split(" ")
        relation=relation.rstrip();
        relationList.append([first,second,relation])
    return [numGuests,numTables,relationList]

#Geenrates the clauses which ensure atleast 1 table assignment
def assignAtLeast1Table(numGuests,numTables):
    global positiveLiterals
    global negativeLiterals
    globalList=[]
    for guest in range(1,numGuests+1):
        guestClause=[]
        for table in range(1,numTables+1):
            guestClause.append("X"+str(guest)+"*"+str(table))
            positiveLiterals.add("X"+str(guest)+"*"+str(table))
        globalList.append(sorted(guestClause))
    return globalList

#Generates the clauses which prevent multiple table assignments
def assignOnly1table(numGuests,numTables):
    global positiveLiterals
    global negativeLiterals
    globalList=[]
    if(numTables>1):
        for guest in range(1, numGuests + 1):
            for table1 in range(1, numTables + 1):
                for table2 in range(table1 + 1, numTables + 1):
                    globalList.append(sorted(["~X" + str(guest) +"*"+ str(table1), "~X" + str(guest)+"*" + str(table2)]))
                    negativeLiterals.add("~X" + str(guest) +"*"+ str(table1))
                    negativeLiterals.add("~X" + str(guest)+"*" + str(table2))
    # else:
    #     for guest in range(1, numGuests + 1):
    #         for table1 in range(1, numTables + 1):
    #                 globalList.append(["X" + str(guest) + str(table1)])
    return globalList

#Generates the relationship clauses
def buildRelationClauses(relationList,numTables):
    globalList=[]
    for relation in relationList:
        firstGuy=relation[0]
        secondGuy=relation[1]
        relation=relation[2]
        if relation=='E':
            enemyClauses=buildEnemyClauses(firstGuy,secondGuy,numTables)
            for clause in enemyClauses:
                globalList.append(clause)
        else:
            friendClauses=buildFriendshipClauses(firstGuy,secondGuy,numTables)
            for clause in friendClauses:
                globalList.append(clause)
    return globalList

#Genrates enemy clauses
#If there is only one table then it should specifically mention that they cannot be seated on the same table
def buildEnemyClauses(firstGuy,secondGuy,numTables):
    global positiveLiterals
    global negativeLiterals
    globalList = []
    if numTables>1:
        for table in range(1, numTables + 1):
            globalList.append(sorted(["~X" + str(firstGuy) +"*"+ str(table), "~X" + str(secondGuy)+"*" + str(table)]))
            negativeLiterals.add("~X" + str(firstGuy) +"*"+ str(table))
            negativeLiterals.add("~X" + str(secondGuy)+"*" + str(table))

    else:
        globalList.append(sorted(["~X" + str(firstGuy) + "*1", "~X" + str(secondGuy) + "*1"]))#cannot be seated on the same table
        negativeLiterals.add("~X" + str(firstGuy) + "*1")
        negativeLiterals.add("~X" + str(secondGuy) + "*1")
    return globalList

#Geenrates Friends clauses
#Will not generate any friends clauses in case of single table since it does not matter . only the enemy list will be used.
def buildFriendshipClauses(firstGuy,secondGuy,numTables):
    global positiveLiterals
    global negativeLiterals
    globalList = []
    for table1 in range(1, numTables + 1):
        for table2 in range(1, numTables + 1):
            if table1!=table2:
                globalList.append(sorted(["~X" + str(firstGuy) +"*"+ str(table1), "~X" + str(secondGuy) +"*"+ str(table2)]))
                negativeLiterals.add("~X" + str(firstGuy) +"*"+ str(table1))
                negativeLiterals.add("~X" + str(secondGuy) +"*"+ str(table2))

    return globalList

#negates a literal
def literalNegator(literal):
    if literal[0]=="~":
        return literal.lstrip("~")
    else:
        return "~"+literal


#satisfied function takes in clauses and the dictionary and checcks if the clausesa are satisfied
#returns tuple(True,None) if the clauses satisfy
#returns tuple(False,False Clauses) if the clauses dont satisfy
def isModelTrue(clauses,assignment):
    for clause in clauses:
        if isClauseTrue(clause,assignment) != True :
            return False
    return True

def isModelFalse(clauses,assignment):
    for clause in clauses:
        if isClauseTrue(clause,assignment) == False :
            return True
    return False

#checks for clauseSatisfaction
def isClauseTrue(clause,assignment):
    result = None
    notYetAssigned=False
    for literal in clause:
        if assignment.has_key(literal):
            if assignment[literal] == True:
                return True
        else:
            notYetAssigned = True
    if not notYetAssigned:
        result = False  # if all literals have been assigned then all literal in this clause are false
    return result


#DPLL Algorithm
def DPLL_SAT(sentence):
    clauses=set()
    symbolsSet =set()
    model={}
    for clause in sentence:
        tupleOfClause=tuple(clause)
        clauses.add(tupleOfClause)
        for literal in clause:
            symbolsSet.add(literal)
    symbols = list(symbolsSet)
    # print clauses
    # print symbols
    return DPLL(clauses,symbols,model)

def DPLL(clauses,symbols,model):
    #if every clause in clauses is true in model then return true
    temp_clauses=clauses.copy()
    temp_model=model.copy()
    temp_symbols=list(symbols)
    if isModelTrue(temp_clauses,temp_model):
        contents = analyse(temp_model)
        return True
    # if some clause in clauses is False in model then return false
    if isModelFalse(temp_clauses,temp_model):
        return False

    #find a pure symbol, its a tuple of (literal,True)
    pAndVal =  findPureSymbol(clauses,symbols,model)
    if pAndVal != None:
        literalAssignedValue = pAndVal[0]
        assignedTruthValue = pAndVal[1]
        reducedSymbols = list(temp_symbols)
        reducedSymbols.remove(literalAssignedValue)
        modifiedModel = temp_model.copy()
        modifiedModel[literalAssignedValue]=assignedTruthValue
        return DPLL(temp_clauses,reducedSymbols,modifiedModel)

    #find unit clauses
    pAndVal = findUnitClauses(clauses,model)
    if pAndVal != None:
        literalAssignedValue = pAndVal[0]
        assignedTruthValue = pAndVal[1]
        reducedSymbols = list(temp_symbols)
        reducedSymbols.remove(literalAssignedValue)
        if literalNegator(literalAssignedValue) in reducedSymbols:
            reducedSymbols.remove(literalNegator(literalAssignedValue))
        modifiedModel = temp_model.copy()
        modifiedModel[literalAssignedValue] = assignedTruthValue
        modifiedModel[literalNegator(literalAssignedValue)] = not assignedTruthValue
        return DPLL(temp_clauses, reducedSymbols, modifiedModel)

    #try ture or false
    literal = temp_symbols[0]
    rest=list(temp_symbols)
    rest.remove(literal)
    negLiteral = literalNegator(literal)
    if (negLiteral in rest):
        rest.remove(negLiteral)

    modifiedModel1=temp_model.copy()
    modifiedModel1[literal]=True
    modifiedModel1[literalNegator(literal)]=False
    modifiedModel2=temp_model.copy()
    modifiedModel2[literal] = False
    modifiedModel2[literalNegator(literal)] = True

    return DPLL(clauses,rest,modifiedModel1) or DPLL(clauses,rest,modifiedModel2)


#finds the pure symbols and returns them
def findPureSymbol(clauses,symbols,model):
    result = None
    unassignedSymbols = set(symbols)
    purePositiveSymbols = set()
    pureNegativeSymbols = set()
    resultList=[]
    for clause in clauses:
        if isClauseTrue(clause,model):
            continue
        thisClauseSymbols = getPosNegSymbols(clause)
        posLiterals = thisClauseSymbols[0]
        negLiterals = thisClauseSymbols[1]
        for literal in posLiterals:
            if literal in unassignedSymbols:
                purePositiveSymbols.add(literal)
        for literal in negLiterals:
            if literal in unassignedSymbols:
                pureNegativeSymbols.add(literal)

    #remove impure symbols
    for literal in unassignedSymbols:
        if(literal in purePositiveSymbols and literalNegator(literal) in pureNegativeSymbols):
            purePositiveSymbols.remove(literal)
            pureNegativeSymbols.remove(literalNegator(literal))
        elif (literal in pureNegativeSymbols and literalNegator(literal) in purePositiveSymbols):
            pureNegativeSymbols.remove(literal)
            purePositiveSymbols.remove(literalNegator(literal))

    #return preferable positive symbols

    if len(purePositiveSymbols)>0:
        resultList.append(next(iter(purePositiveSymbols)))
        resultList.append(True)
        result = tuple(resultList)
    elif len(pureNegativeSymbols)>0:
        resultList.append(next(iter(pureNegativeSymbols)))
        resultList.append(True)
        result = tuple(resultList)


    return result

#finds unit clauses
def findUnitClauses(clauses,model):
    result = None
    resultList=[]
    for clause in clauses:
        if (isClauseTrue(clause,model) == None):
            literal = None
            if len(clause)==1:
                literal = clause[0]
            else:
                for symbol in clause:
                    value = model[symbol] if(model.has_key(symbol)) else None
                    if value == None:
                        if literal == None:
                            literal = symbol
                        else:
                            literal = None
                            break

            if literal != None:
                resultList.append(literal)
                resultList.append(True)
                result = tuple(resultList)
                break
    return result


# get positive and negative symbols
def getPosNegSymbols(clause):
    posLiterals = []  # positive literals
    negLiterals = []  # negative literals
    result=[]
    for literal in clause:
        if literal[0] == '~':
            negLiterals.append(literal)
        else:
            posLiterals.append(literal)
    result.append(posLiterals)
    result.append(negLiterals)
    return tuple(result)

#unions 3 lists
def uniteLists(list1,list2,list3):
    commonList=[]
    for clause in list1:
        commonList.append(clause)
    for clause in list2:
        commonList.append(clause)
    for clause in list3:
        commonList.append(clause)
    return commonList

#analyse the model
def analyse(model):
    temp_model = model.copy()
    result={}
    global finalResults
    finalResults="yes\n"
    for assignment in temp_model:
        lit = str(assignment)
        list1 = lit.split('*')
        table = list1[1]
        list2=list1[0].split('X')
        person = list2[1]
        truth=list2[0]          #is either '' or '~'
        value=temp_model[assignment]
        if truth=="" and value == True:
            # if person in result:
                # print "contradiction" if result[person] != table else "already assigned"
            # else:
                result[person] = table

        if truth == "~" and value == False:
            # if person in result:
            #     print "contradiction" if result[person] != table else "already assigned"
            # else:
                result[person] = table
    i=1
    while(i>0):
        if str(i) not in result:
            break
        finalResults += str(i) + " " + result[str(i)]+"\n"
        i += 1

def writeOutput(contents):
    f = open('output.txt', 'w+')
    f.write(contents)
    f.close()

if __name__ == '__main__':
    main()