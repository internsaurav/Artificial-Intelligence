import StringIO
import itertools
import copy

set_nodes_dictionary={}

def main():
    global set_nodes_dictionary
    inpath = "input.txt"
    inputData = readInput(inpath)
    outputFile = open('output.txt','w')
    decodedInput = decodeInput(inputData)
    queries = decodedInput[0]
    probabilityTables = decodedInput[1]
    utility = decodedInput[2] if len(decodedInput)==3 else 'None'
    queries = decodeQueries(queries)

    #decode the probabiity tables
    probabilityTables = decodeProbabilityTables(probabilityTables)
    nodes = probabilityTables[0]
    CPT = probabilityTables [1]
    parentsDictionary = probabilityTables[2]
    for node in nodes:
        index = nodes.index(node)
        pTable = CPT[index]

    #decoding utility
    decodedUtility=None
    utilityNodes = None
    utilityDictionary = None
    if utility != 'None':
        decodedUtility = decodeUtility(utility)
        utilityDictionary = decodedUtility[0]
        utilityNodes = decodedUtility[1]

    for query,type in queries:
        if type=='P':
            probability = findProbabilty(query,nodes,CPT,parentsDictionary)
            #print '%.2f' % round(probability,2)
            print >> outputFile,'%.2f' % round(probability, 2)
        elif type=='EU' and decodedUtility != None:
            Expected_utility = findEU(query, utilityNodes, utilityDictionary, nodes, CPT, parentsDictionary)
            #print int(round(Expected_utility,0))
            print >> outputFile, int(round(Expected_utility, 0))
        elif type=='MEU' and decodedUtility != None:
            EUfromMEUqueries = makeEUsfromMEUs(query)
            MEUreturn = findMEU(EUfromMEUqueries, utilityNodes, utilityDictionary, nodes, CPT, parentsDictionary)
            MEUvalue = MEUreturn[0]
            highest_combo = MEUreturn[1]
            highest_combo = findHighest(highest_combo, query)
            #print highest_combo + " " + str(int(round(MEUvalue,0)))
            print >> outputFile, highest_combo + " " + str(int(round(MEUvalue, 0)))

def readInput(inpath):
    f = open(inpath, 'r')
    #set a flag for query ending. Read line by line till encounter the flag
    #the flag is  ******
    query_ends = False
    inputLines = ""
    tables=[]
    for line in f:
        inputLines +=line

    f.close()
    return inputLines

def decodeInput(inputData):
    inputData = inputData.split("******\n")
    return inputData

def decodeQueries(queries):
    queryList=[]
    queries = queries.split('\n')
    # ##print queries
    queries.pop()
    # ##print queries
    for query in queries:
         if query[0] == 'P':
             queryList.append((query,'P'))
         elif query[0] == 'E':
             queryList.append((query,'EU'))
         else:
             queryList.append((query,'MEU'))
    return queryList

def decodeProbabilityTables(probabilityTables):
    nodes = []  # stores nodes and their indices
    CPT = []  # stores the CPTs as a list of dictionaries
    probabilityTables = probabilityTables.split("***\n")
    parentsDictionary={}
    #add the nodes ot the nodes list
    for allData in probabilityTables:
        allData =  allData.rstrip()
        dataBuffer = StringIO.StringIO(allData)
        node = dataBuffer.readline().rstrip()
        #split at separator
        node = node.split('|')
        conditional = True if len(node)>1 else False
        thisNode = node[0].strip()
        parents=None
        if conditional:
            parents = node[1].strip()
            parents = parents.split(' ')
            parentsString=''
            for p in parents:
                parentsString += p+','
            parentsString = parentsString[:-1]

        else:
            parentsString=None

        nodes.append(thisNode)#adds the node and index to dictionary
        parentsDictionary[thisNode]=parents#adds to list of parents
        numParents = len(parents) if conditional else 0
        numLinesToRead = 2**numParents
        probabilityDictionary = {}
        for i in range(0,numLinesToRead):
            tableData = dataBuffer.readline().rstrip()
            tableData=tableData.split(' ')
            condition = tableData[-numParents:] if conditional else None
            if conditional:
                conditionString = generateCString(condition,parents)
            else:
                conditionString = None
            probability = tableData[0]
            if probability != 'decision':
                probabilityDictionary[conditionString]=float(probability)
            else:
                probabilityDictionary[conditionString] = 'decision'
        CPT.append(probabilityDictionary)
    return [nodes,CPT,parentsDictionary]

def decodeUtility(utility):
    utility = utility.rstrip()
    dataBuffer = StringIO.StringIO(utility)
    node = dataBuffer.readline().rstrip()
    # split at separator
    node = node.split('|')
    conditional = True if len(node) > 1 else False
    thisNode = node[0].strip()
    parents = None
    if conditional:
        parents = node[1].strip()
        parents = parents.split(' ')
        parentsString = ''
        for p in parents:
            parentsString += p + ','
        parentsString = parentsString[:-1]
    else:
        parentsString = None

    numParents = len(parents) if conditional else 0
    numLinesToRead = 2 ** numParents
    probabilityDictionary = {}
    for i in range(0, numLinesToRead):
        tableData = dataBuffer.readline().rstrip()
        tableData = tableData.split(' ')
        condition = tableData[-numParents:] if conditional else None
        if conditional:
            conditionString = generateCString(condition, parents)
        else:
            conditionString = None
        probability = tableData[0]
        if probability != 'decision':
            probabilityDictionary[conditionString] = float(probability)
        else:
            probabilityDictionary[conditionString] = 'decision'
    return [probabilityDictionary,parents]

def findFixedNodes(euQuery):
    actual_stuff = euQuery[3:-1]
    given_dictionary={}
    vars=actual_stuff.split('|')
    left=vars[0]
    left=left.split(',')
    for var in left:
        var=var.strip()
        var=var.replace(' ','')
        var=var.split('=')
        given_dictionary[var[0]]=var[1]
    if len(vars)>1:
        right=vars[1]
        right = right.split(',')
        for var in right:
            var = var.strip()
            var = var.replace(' ', '')
            var = var.split('=')
            given_dictionary[var[0]] = var[1]
    return given_dictionary

def generateCString(condition,parents):
    conditionString=set()
    for i in parents:
        ind = parents.index(i)
        symbol=condition[ind]
        combinedSymbol=symbol+i
        conditionString.add(combinedSymbol)
    conditionString = frozenset(conditionString)
    return conditionString

def generateReducedForm(query, nodes, CPT, parentsDictionary):
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    global set_nodes_dictionary
    jointProbabilityData = makeJointProbability(query, temp_nodes)
    queriesVariables = jointProbabilityData[0]
    jointProbabilityQuery = jointProbabilityData[1]
    setVariablesDictionary = jointProbabilityData[2]
    set_nodes_dictionary = copy.deepcopy(queriesVariables)
    set_nodes_dictionary.update(setVariablesDictionary)
    jointProbabilityCPTqueryForm = expressInCPTform(jointProbabilityQuery,parentsDictionary,queriesVariables,setVariablesDictionary)
    CPTqueryTobeSolved = jointProbabilityCPTqueryForm[0]
    summations = jointProbabilityCPTqueryForm[1]
    tempCPTQueryToBeSolved = list(CPTqueryTobeSolved)

    for termToBeSummedOut in reversed(summations):
        variableToBeSummedOut = termToBeSummedOut.split('|')[0]
        tempCPTQueryToBeSolved = sumOut(tempCPTQueryToBeSolved, variableToBeSummedOut, termToBeSummedOut, temp_nodes, temp_CPT)
    queryCopy = copy.deepcopy(tempCPTQueryToBeSolved)
    reducedQuery = reduceQuery(queryCopy)
    return reducedQuery

def makeJointProbability(query, nodes):
    temp_nodes = list(nodes)
    jointProbabilityStatement = []
    analysedQuery = analyzeQuery(query)
    queryVariables = analysedQuery[0]
    setVariablesDictionary = analysedQuery[1]
    for node in temp_nodes:
        nodeToBeAdded = node if node not in setVariablesDictionary else setVariablesDictionary[node]+node
        jointProbabilityStatement.append(nodeToBeAdded)
    return [queryVariables,jointProbabilityStatement,setVariablesDictionary]

def analyzeQuery(query):
    setDictionary = {}
    queryDictionary ={}
    stuffs = query[query.index('(')+1:query.index(')')]
    stuffs = stuffs.replace(' ', '')
    things = stuffs.split('|')
    somethingsAreSet = True if len(things) == 2 else False
    if somethingsAreSet:
        thingsAlreadySet = things[1] if somethingsAreSet else None
        thingsAlreadySet = thingsAlreadySet.split(',')
        for setVariable in thingsAlreadySet:
            setVariable = setVariable.split('=')
            variable = setVariable[0]
            truthValue = setVariable[1]
            setDictionary[variable] = truthValue
    queryVariables = things[0]
    queryVariables = queryVariables.split(',')
    for queryVariable in queryVariables:
        queryVariable = queryVariable.split('=')
        variable = queryVariable[0]
        truthValue = queryVariable[1]
        queryDictionary[variable] = truthValue
    return [queryDictionary,setDictionary]

def expressInCPTform(jointProbabilityQuery,parentsDictionary,queryVariables,setVariablesDictionary):
    CPTform = []
    summation = []
    for var in jointProbabilityQuery:
        var2 = var.replace('+','')
        var2 = var2.replace('-','')
        parent = parentsDictionary[var2]
        parentWithSymbols = assignSymbolsToParents(parent,setVariablesDictionary)
        cptform=var+'|'+str(parentWithSymbols)
        CPTform.append(cptform)
        if var2 not in queryVariables and var2 not in setVariablesDictionary:
            summation.append(cptform)
    moveHiddenVariablesOut(CPTform,summation)
    return [CPTform,summation]

def assignSymbolsToParents(parent,setVariablesDictionary):
    if parent == None:
        return None
    parentWithSymbol=''
    parentSplit = parent
    ##print parentSplit    for p in parentSplit:

        parentWithSymbol += p if p not in setVariablesDictionary else setVariablesDictionary[p]+p
        parentWithSymbol +=','
    return  parentWithSymbol[:-1]

def moveHiddenVariablesOut(CPTform,summation):
    numberOfSummations = len(summation)
    for last_summation in reversed(summation):
        summation_var = last_summation.split('|')[0]
        if summation[-1]==last_summation:
            things_check = CPTform[CPTform.index(last_summation)+1:]
        else:
            indexOfLastSummation = summation.index(last_summation)
            nextVar = summation[indexOfLastSummation+1]
            things_check = CPTform[CPTform.index(last_summation) + 1:CPTform.index(nextVar)]
        for things in things_check:
            if summation_var not in things:
                CPTform.remove(things)
                CPTform.insert(CPTform.index(last_summation),things)
    return CPTform

def sumOut(CPTqueryTobeSolved, variableToBeSummedOut, wholeVarTerm, nodes, CPT):
    temp_nodes = list(nodes)
    temp_CPT = list(CPT)
    temp_CPTqueryTobeSolved = list(CPTqueryTobeSolved)
    factors={}
    summationIndex = temp_CPTqueryTobeSolved.index(wholeVarTerm)
    relevantTerms = temp_CPTqueryTobeSolved[summationIndex:]
    relevantFactors = findRelevantFactors(relevantTerms,variableToBeSummedOut)
    if len(relevantFactors) !=0:
        factors['factors']=relevantFactors
        factorObject = makeFactor(variableToBeSummedOut,relevantTerms,relevantFactors,temp_nodes,temp_CPT)
        factors['factorTable']=factorObject
        modifiedCPTquery = temp_CPTqueryTobeSolved[0:summationIndex]
        modifiedCPTquery.append(factors)
    else:
        modifiedCPTquery = temp_CPTqueryTobeSolved[0:summationIndex]
    return modifiedCPTquery

def findRelevantFactors(relevantTerms,variableToBeSummedOut):
    relevantFactors=set()
    for term in relevantTerms:
        if type(term)== str:
            vars=term.split('|')
            firstTerm = vars[0]
            if not firstTerm[0]=='+' and not firstTerm[0]=='-':
                if firstTerm != variableToBeSummedOut:
                    relevantFactors.add(firstTerm)
            if vars[1] != 'None':
                secTerm = vars[1].split(',')
                for term in secTerm:
                    if not term[0]=='+' and not term[0]=='-':
                        if term != variableToBeSummedOut:
                            relevantFactors.add(term)
        else:
            relFactors = term['factors']#factors is key in the factor dictionary
            for fac in relFactors:
                if not fac[0] == '+' and not fac[0] == '-':
                    if fac != variableToBeSummedOut:
                        relevantFactors.add(fac)
    return relevantFactors

def makeFactor(variableToBeSummedOut,relevantTerms,relevantFactors,nodes,CPT):
    factorArray=[]
    factorObject = {}
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    for factor in relevantFactors:
        tempSet=set()
        tempSet.add('+'+factor)
        tempSet.add('-'+factor)
        factorArray.append(tempSet)
    combos = list(set(tup) for tup in itertools.product(*factorArray))
    for combo in combos:
        tempRelevantTerms = list(relevantTerms)
        sumForCombo=evaluate(combo,tempRelevantTerms,variableToBeSummedOut,temp_nodes,temp_CPT)
        factorObject[frozenset(combo)]=sumForCombo
    return factorObject

def evaluate(combo,RelevantTerms,variableToBeSummedOut,nodes,CPT):
    tempRelevantTerms=copy.deepcopy(RelevantTerms)
    temp_nodes = list(nodes)
    temp_CPT = list(CPT)
    for node in combo:
        symbol = node[0]
        var=node[1:]
        for term in tempRelevantTerms:
            index = tempRelevantTerms.index(term)
            if type(term) == str:
                term2=replaceTerm(term,var,node)
                tempRelevantTerms[index]=term2
            else:
                factors = term['factors']
                if var in factors:
                    if 'fixedVars' not in term:
                        fixedTerm = term
                        nodeSet = set()
                        nodeSet.add(node)
                        fixedTerm['fixedVars']=nodeSet
                        tempRelevantTerms[index] = fixedTerm
                    else:
                        fixedVars = term['fixedVars']
                        fixedVars.add(node)
                        term['fixedVars'] = fixedVars
                        tempRelevantTerms[index] = term

    tempRelevantTermsCopy = copy.deepcopy(tempRelevantTerms)
    positiveSum = findSum('+',tempRelevantTermsCopy,variableToBeSummedOut,nodes,CPT)
    tempRelevantTermsCopy2 = copy.deepcopy(tempRelevantTerms)
    negativeSum = findSum('-',tempRelevantTermsCopy2,variableToBeSummedOut,nodes,CPT)
    sum= positiveSum+negativeSum
    return sum

def replaceTerm(term,var,node):
    term2 = term.split('|')
    left = term2[0]
    right = term2[1]
    if not isFixed(left):
        if var == left:
            left = node
    if right != 'None':
        right2 = right.split(',')
        rightString = ''
        for r in right2:
            if not isFixed(r):
                if var == r:
                    r = node
            rightString += r + ','
        rightString = rightString[:-1]
    else:
        rightString = 'None'
    term = left + '|' + rightString
    return term

def isFixed(var):
    if var[0]=='+' or var[0] =='-':
        return True
    else:
        return False

def findSum(sign, tempRelevantTerms, variableToBeSummedOut, nodes, CPT):
    tempRelevantTerms2 = list(tempRelevantTerms)
    if variableToBeSummedOut != '':
        signedVar=sign+variableToBeSummedOut
        for term in tempRelevantTerms2:
            index = tempRelevantTerms2.index(term)
            if type(term)==str:
                terms2 = replaceTerm(term,variableToBeSummedOut,signedVar)
                tempRelevantTerms2[index] = terms2
            else:
                ##print "Factor detecteed"
                dependantFactors=term['factors']
                if variableToBeSummedOut in dependantFactors:
                    #if fixed vars already present
                    if 'fixedVars' in term:
                        fixedVars = term['fixedVars']
                        fixedVars.add(signedVar)
                        newTerm = term
                        newTerm['fixedVars']=fixedVars
                        tempRelevantTerms2[index]=newTerm
                    else:
                        fixedTerm = term
                        nodeSet = set()
                        nodeSet.add(signedVar)
                        fixedTerm['fixedVars'] = nodeSet
                        tempRelevantTerms2[index] = fixedTerm

    probability = lookUpProbability(tempRelevantTerms2, nodes, CPT)
    return probability

def lookUpProbability(tempRelevantTerms, nodes, CPT):
    tempRelevantTerms2 = list(tempRelevantTerms)
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    product = 1
    for term in tempRelevantTerms2:
        if type(term)==str:
            parentsSet=set()
            term = term.split('|')
            variable = term[0]
            symbol=variable[0]
            node=variable[1:]
            indexOfNode = temp_nodes.index(node)
            pTable=temp_CPT[indexOfNode]
            parents = term[1]
            if parents != 'None':
                parents = parents.split(',')
                for parent in parents:
                    parentsSet.add(parent)
                parentsSet = frozenset(parentsSet)
                if symbol == '+':
                    product *= pTable[parentsSet]
                else:
                    product *= (1-pTable[parentsSet])
            else:
                if pTable[None] != 'decision':
                    if symbol == '+':
                        product *= pTable[None]
                    else:
                        product *= (1-pTable[None])
        else:
            fixedTerm = term['fixedVars']
            factorTable = term['factorTable']
            product *= factorTable[frozenset(fixedTerm)]
    return product

def checkConstant(term):
    result = True
    if type(term)==str:
        temp_str=term.split('|')
        left = temp_str[0]
        right = temp_str[1]
        if left[0] !='+' and left[0] != '-':
            return False
        if right == 'None':
            return True
        else:
            parents = right.split(',')
            for p in parents:
                if p[0] != '+' and p[0] != '-':
                    return False
    else:
        result = False
    return result

def reduceQuery(query):
    temp_query = list(query)
    reducedQuery=list(query)
    for term in temp_query:
        if checkConstant(term):
            reducedQuery.remove(term)
    return reducedQuery

def calculateProbability(query_vars,reducedQuery,variables,nodes,CPT):
    num = calculateNumerator(query_vars,reducedQuery,nodes,CPT)
    den = calculateDenominator(reducedQuery,variables,nodes,CPT)
    return num/den

def calculateNumerator(query_vars,reducedQuery,nodes,CPT):
    combo = set()
    temp_reducedQuery = copy.deepcopy(reducedQuery)
    temp_nodes = list(nodes)
    temp_CPT = list(CPT)
    for var in query_vars:
        symbol = query_vars[var]
        thisVar = symbol+var
        combo.add(thisVar)
    sum=evaluate(combo,temp_reducedQuery,'',temp_nodes,temp_CPT)
    return sum

def calculateDenominator(reducedQuery,variables,nodes,CPT):
    combos = makeCombo(variables) #list of combinations, each combination is a set
    temp_reducedQuery = copy.deepcopy(reducedQuery)
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    sum=0
    for combo in combos:
        sum += evaluate(combo,temp_reducedQuery,'',temp_nodes,temp_CPT)
    return sum

def makeCombo(variables):
    factorArray=[]
    for var in variables:
        tempSet = set()
        tempSet.add('+' + var)
        tempSet.add('-' + var)
        factorArray.append(tempSet)
    combos = list(set(tup) for tup in itertools.product(*factorArray))
    return combos

def makeUtilityCombo(variables,fixedNodesDict):
    factorArray=[]
    fixed_util_nodes={}
    for var in variables:
        if var not in fixedNodesDict:
            tempSet = set()
            tempSet.add('+' + var)
            tempSet.add('-' + var)
            factorArray.append(tempSet)
        else:
            fixed_util_nodes[var]=fixedNodesDict[var]

    combos = list(set(tup) for tup in itertools.product(*factorArray))
    return [combos,fixed_util_nodes]

def findProbabilty(q, nodes, CPT, parentsDictionary):
    reducedQuery = generateReducedForm(q, nodes, CPT, parentsDictionary)
    variables = findRelevantFactors(reducedQuery, '')
    query_vars = makeJointProbability(q, nodes)[0]
    probability = calculateProbability(query_vars, reducedQuery, variables, nodes, CPT)
    return probability

def findEU(EUquery,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary):
    eu_nodes_fixed = findFixedNodes(EUquery)
    findCombo = makeUtilityCombo(utilityNodes, eu_nodes_fixed)
    utilityCombo = findCombo[0]
    fixed_util_dictionary = findCombo[1]
    temp_utilityCombo = copy.deepcopy(utilityCombo)
    temp_eu_nodes_fixed = copy.deepcopy(eu_nodes_fixed)
    ExpectedUtility =0
    for combo in temp_utilityCombo:
        left=''
        comboset = set()
        for elements in combo:
            sign = elements[0]
            thisElm = elements[1:]+" = "+sign+", "
            left+=thisElm
            comboset.add(elements)
        left = left.strip()
        left=left[:-1]#removes the ,
        right=''
        for elements in temp_eu_nodes_fixed:
            sign = temp_eu_nodes_fixed[elements]
            thisElm = elements + " = " + sign + ", "
            right += thisElm
        right = right.strip()
        right = right[:-1]  # removes the ,
        probabilityQuery = 'P('+left+" | "+right+")"
        for fixed_util_node in fixed_util_dictionary:
            symbol=fixed_util_dictionary[fixed_util_node]
            toBeAdded= symbol+fixed_util_node
            comboset.add(toBeAdded)

        ExpectedUtility += findProbabilty(probabilityQuery,nodes,CPT,parentsDictionary)*utilityDictionary[frozenset(comboset)]
    return ExpectedUtility

def makeEUsfromMEUs(MEUquery):
    EUfromMEUQueries=[]
    query=MEUquery[4:-1]
    query = query.split('|')
    util_nodes = query[0]
    conditionals = query[1] if len(query)>1 else None
    util_nodes=util_nodes.replace(' ','')
    util_nodes=util_nodes.split(',')
    combos = makeCombo(util_nodes)
    for combo in combos:
        EUQuery=''
        left = ''
        comboset = set()
        for elements in combo:
            sign = elements[0]
            thisElm = elements[1:] + " = " + sign + ", "
            left += thisElm
            comboset.add(elements)
        left = left.strip()
        left = left[:-1]  # removes the ,
        if len(query)>1:
            right = conditionals.strip()
            EUQuery='EU('+left+" | "+right+")"
        else:
            EUQuery='EU('+left+")"
        EUfromMEUQueries.append(EUQuery)
    return EUfromMEUQueries

def findMEU(EUfromMEUqueries,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary):
    value=float('-inf')
    highestQuery=''
    for EUquery in EUfromMEUqueries:
        EUval = findEU(EUquery,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary)
        if EUval>value:
            value=EUval
            highestQuery=EUquery
    return [value,highestQuery]

def findHighest(highest_combo,MEUquery):
    relevantVars=highest_combo[3:-1]
    relevantVars = relevantVars.split('|')[0]
    relevantVars = relevantVars.replace(' ','')
    relevantVars=relevantVars.split(',')
    varDict={}
    for var in relevantVars:
        var=var.split('=')
        varDict[var[0]]=var[1]
    highVarSymbols=''
    temp_MEUquery=MEUquery[4:-1]
    temp_MEUquery=temp_MEUquery.split('|')[0]
    temp_MEUquery=temp_MEUquery.replace(' ','')
    temp_MEUquery=temp_MEUquery.split(',')
    for var in temp_MEUquery:
        highVarSymbols+=varDict[var]+' '
    highVarSymbols = highVarSymbols.rstrip()
    return highVarSymbols



if __name__ == '__main__':
    main()
