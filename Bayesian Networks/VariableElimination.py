import StringIO
import itertools
import copy

set_nodes_dictionary={}

def main():
    global set_nodes_dictionary
    inpath = "input.txt"
    inputData = readInput(inpath)
    outputFile = open('output.txt','w')
    # ##print inputData
    decodedInput = decodeInput(inputData)
    queries = decodedInput[0]
    probabilityTables = decodedInput[1]
    utility = decodedInput[2] if len(decodedInput)==3 else 'None'

    ##print "\nqueries are:\n" + queries
    ##print "\nprobabilities are:\n"+probabilityTables
    ##print "\nUtility is:\n"+utility

    #Decode the queries
    # print "The queries are"
    # print queries
    queries = decodeQueries(queries)
    # print "Queris are"
    # print queries
    # ##print P
    # ##print EU
    # ##print MEU

    #decode the probabiity tables
    probabilityTables = decodeProbabilityTables(probabilityTables)
    nodes = probabilityTables[0]
    CPT = probabilityTables [1]
    parentsDictionary = probabilityTables[2]
    for node in nodes:
        index = nodes.index(node)
        pTable = CPT[index]
        ##print "Table for Node-"+node+" whose parents are "+str(parentsDictionary[node])+":"
        ##print pTable
        ##print "--------------"

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



    # #decode the utility list
    # if utility != 'None':
    #     decodedUtility = decodeUtility(utility)
    #     utilityDictionary = decodedUtility[0]
    #     ##print utilityDictionary
    #     utilityNodes = decodedUtility[1]
    #     # EUquery = EU[0]
    #     ##print "EU query is"
    #     ##print EUquery
    #
    #     # Expected_utility = findEU(EUquery,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary)
    #     # MEUquery=MEU[1]
    #     ##print "MEU query is"
    #     ##print MEUquery
    #     # EUfromMEUqueries = makeEUsfromMEUs(MEUquery)
    #     ##print EUfromMEUqueries
    #     # MEUreturn = findMEU(EUfromMEUqueries,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary)
    #     # MEUvalue=MEUreturn[0]
    #     # highest_combo = MEUreturn[1]
    #     # ##print "MEU is"
    #     # ##print MEUvalue
    #     # ##print "highest was"
    #     # ##print highest_combo
    #     # highest_combo = findHighest(highest_combo,MEUquery)
    #     # print "Anser is"
    #     # print highest_combo+" "+str(MEUvalue)


    # q = P[0]
    # ##print q
    # probability = findProbabilty(q, nodes, CPT, parentsDictionary)
    ##print "*********************************************************************"
    ##print "*********************************************************************"
    ##print "And the final answer is"
    # ##print probability
    ##print "*********************************************************************"
    ##print "*********************************************************************"


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
    ##print "*********************************************"
    ##print "Decoding Input"
    inputData = inputData.split("******\n")
    ##print "Done Decoding"
    ##print "*********************************************"
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
    ##print "------------------------------------"
    ##print "Decoding probability tables:"
    ##print "------------------------------------"
    nodes = []  # stores nodes and their indices
    CPT = []  # stores the CPTs as a list of dictionaries
    probabilityTables = probabilityTables.split("***\n")
    parentsDictionary={}
    #add the nodes ot the nodes list
    for allData in probabilityTables:
        allData =  allData.rstrip()
        dataBuffer = StringIO.StringIO(allData)
        node = dataBuffer.readline().rstrip()
        ##print "Normal:"
        ##print node
        #split at separator
        node = node.split('|')
        ##print "After splitting:"
        ##print node
        conditional = True if len(node)>1 else False
        ##print "Conditional:"
        ##print conditional
        thisNode = node[0].strip()
        ##print "This Node:"
        ##print thisNode
        parents=None
        if conditional:
            parents = node[1].strip()
            ##print "Parents:"
            ##print parents
            parents = parents.split(' ')
            ##print parents
            parentsString=''
            for p in parents:
                parentsString += p+','
            parentsString = parentsString[:-1]
            ##print "parentString:"
            ##print parentsString

        else:
            parentsString=None
            ##print "parentString:"
            ##print parentsString

        nodes.append(thisNode)#adds the node and index to dictionary
        parentsDictionary[thisNode]=parents#adds to list of parents
        numParents = len(parents) if conditional else 0
        ##print "Number of Parents:"
        ##print numParents
        numLinesToRead = 2**numParents
        ##print "Number of lines to read:"
        ##print numLinesToRead
        probabilityDictionary = {}
        for i in range(0,numLinesToRead):
            tableData = dataBuffer.readline().rstrip()
            ##print "Raw Data is:"
            ##print tableData
            tableData=tableData.split(' ')
            condition = tableData[-numParents:] if conditional else None
            ##print "Conditionals are:"
            ##print condition
            if conditional:
                conditionString = generateCString(condition,parents)
                ##print conditionString
            else:
                conditionString = None
                ##print conditionString
            probability = tableData[0]
            ##print "Probability is:"
            ##print probability
            if probability != 'decision':
                probabilityDictionary[conditionString]=float(probability)
            else:
                probabilityDictionary[conditionString] = 'decision'
        CPT.append(probabilityDictionary)
        ##print ""
    return [nodes,CPT,parentsDictionary]

def decodeUtility(utility):
    ##print "==============================================="
    ##print "Decoding Utility"
    ##print "==============================================="
    ##print utility
    utility = utility.rstrip()
    dataBuffer = StringIO.StringIO(utility)
    node = dataBuffer.readline().rstrip()
    ##print "Normal:"
    ##print node
    # split at separator
    node = node.split('|')
    ##print "After splitting:"
    ##print node
    conditional = True if len(node) > 1 else False
    ##print "Conditional:"
    ##print conditional
    thisNode = node[0].strip()
    ##print "This Utility:"
    ##print thisNode
    parents = None
    if conditional:
        parents = node[1].strip()
        ##print "Parents of Utility:"
        ##print parents
        parents = parents.split(' ')
        ##print parents
        parentsString = ''
        for p in parents:
            parentsString += p + ','
        parentsString = parentsString[:-1]
        ##print "parentString:"
        ##print parentsString

    else:
        parentsString = None
        ##print "parentString:"
        ##print parentsString

    # nodes.append(thisNode)  # adds the node and index to dictionary
    # parentsDictionary[thisNode] = parents  # adds to list of parents
    numParents = len(parents) if conditional else 0
    ##print "Number of Parents:"
    ##print numParents
    numLinesToRead = 2 ** numParents
    ##print "Number of lines to read:"
    ##print numLinesToRead
    probabilityDictionary = {}
    for i in range(0, numLinesToRead):
        tableData = dataBuffer.readline().rstrip()
        ##print "Raw Data is:"
        ##print tableData
        tableData = tableData.split(' ')
        condition = tableData[-numParents:] if conditional else None
        ##print "Conditionals are:"
        ##print condition
        if conditional:
            conditionString = generateCString(condition, parents)
            ##print conditionString
        else:
            conditionString = None
            ##print conditionString
        probability = tableData[0]
        ##print "Probability is:"
        ##print probability
        if probability != 'decision':
            probabilityDictionary[conditionString] = float(probability)
        else:
            probabilityDictionary[conditionString] = 'decision'
    # CPT.append(probabilityDictionary)
    # ##print "Utility Dicttyionary is"
    # ##print probabilityDictionary
    # ##print ""
    return [probabilityDictionary,parents]

def findFixedNodes(euQuery):
    ##print "=============================="
    ##print "Checking Eu Query"
    ##print euQuery
    actual_stuff = euQuery[3:-1]
    ##print "actual EU query is"
    ##print actual_stuff
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
    # ##print "Given variables in query are"
    ##print "============================="
    return given_dictionary

def generateCString(condition,parents):
    ##print "Cstring starts"
    conditionString=set()
    ##print parents
    for i in parents:
        ind = parents.index(i)
        ##print ind
        symbol=condition[ind]
        combinedSymbol=symbol+i
        conditionString.add(combinedSymbol)
    conditionString = frozenset(conditionString)
    return conditionString

def generateReducedForm(query, nodes, CPT, parentsDictionary):
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    global set_nodes_dictionary
    ##print "------------------------------------------"
    ##print "ESTIMATE PROBABILITY"
    ##print "------------------------------------------"
    ##print "Passed variables are:"
    ##print "Query is"
    ##print query
    ##print type(query)
    ##print "Nodes are"
    ##print temp_nodes
    ##print type(temp_nodes)
    ##print "CPT is"
    ##print temp_CPT
    ##print type(temp_CPT)
    ##print "Parents Dictionary"
    ##print parentsDictionary
    ##print type(parentsDictionary)
    ##print "------------------------------------------"
    jointProbabilityData = makeJointProbability(query, temp_nodes)
    queriesVariables = jointProbabilityData[0]
    jointProbabilityQuery = jointProbabilityData[1]
    setVariablesDictionary = jointProbabilityData[2]
    ##print "Query variavles are:"
    ##print queriesVariables
    set_nodes_dictionary = copy.deepcopy(queriesVariables)
    ##print "Joint Probability Query is"
    ##print jointProbabilityQuery
    ##print"Set Variables dictionary is:"
    ##print setVariablesDictionary
    set_nodes_dictionary.update(setVariablesDictionary)
    jointProbabilityCPTqueryForm = expressInCPTform(jointProbabilityQuery,parentsDictionary,queriesVariables,setVariablesDictionary)
    CPTqueryTobeSolved = jointProbabilityCPTqueryForm[0]
    summations = jointProbabilityCPTqueryForm[1]
    ##print "CPT query to be solved:"
    ##print CPTqueryTobeSolved
    ##print "Summations:"
    ##print summations
    tempCPTQueryToBeSolved = list(CPTqueryTobeSolved)

    for termToBeSummedOut in reversed(summations):
        ##print "Term to be summed out"
        ##print termToBeSummedOut
        variableToBeSummedOut = termToBeSummedOut.split('|')[0]
        ##print "Variable to be summed out:"
        ##print variableToBeSummedOut
        tempCPTQueryToBeSolved = sumOut(tempCPTQueryToBeSolved, variableToBeSummedOut, termToBeSummedOut, temp_nodes, temp_CPT)
    ##print"==============================================================="
    ##print"==============================================================="
    ##print "Final Joint Table is:"
    ##print tempCPTQueryToBeSolved
    ##print"==============================================================="
    ##print"==============================================================="
    queryCopy = copy.deepcopy(tempCPTQueryToBeSolved)
    reducedQuery = reduceQuery(queryCopy)
    ##print "Reduced Query is"
    ##print reducedQuery
    return reducedQuery

def makeJointProbability(query, nodes):
    ##print "------------------------------------------"
    ##print "making joint probability"
    ##print "------------------------------------------"
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
    ##print "********************************************"
    ##print "ANALYSING QUERY"
    ##print "********************************************"
    setDictionary = {}
    queryDictionary ={}
    stuffs = query[query.index('(')+1:query.index(')')]
    ##print "actual query is"
    ##print stuffs
    stuffs = stuffs.replace(' ', '')
    ##print stuffs
    things = stuffs.split('|')
    ##print "After splitting at |"
    ##print things
    somethingsAreSet = True if len(things) == 2 else False
    ##print "is there a condition?"
    ##print somethingsAreSet
    if somethingsAreSet:
        thingsAlreadySet = things[1] if somethingsAreSet else None
        ##print thingsAlreadySet
        thingsAlreadySet = thingsAlreadySet.split(',')
        ##print thingsAlreadySet
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
    ##print "---------------------------------------"
    ##print "Entering Express in CPT form"
    ##print "---------------------------------------"

    CPTform = []
    summation = []
    for var in jointProbabilityQuery:
        ##print "Variable being considered"
        ##print var
        var2 = var.replace('+','')
        var2 = var2.replace('-','')
        ##print "Same variable after stripping of sign"
        ##print var2
        parent = parentsDictionary[var2]
        ##print "Its parents are"
        ##print parent
        parentWithSymbols = assignSymbolsToParents(parent,setVariablesDictionary)
        ##print "same parent with symbols"
        ##print parentWithSymbols
        cptform=var+'|'+str(parentWithSymbols)
        ##print cptform
        CPTform.append(cptform)
        if var2 not in queryVariables and var2 not in setVariablesDictionary:
            summation.append(cptform)
    ##print CPTform
    ##print summation
    moveHiddenVariablesOut(CPTform,summation)
    ##print CPTform
    ##print "Exiting Express in CPT Form function "
    ##print "---------------------------------------"
    return [CPTform,summation]

def assignSymbolsToParents(parent,setVariablesDictionary):
    ##print "------------------------------------------"
    ##print"assignSYmbol function"
    ##print "------------------------------------------"
    if parent == None:
        return None
    ##print "entered"
    parentWithSymbol=''
    parentSplit = parent
    ##print parentSplit
    for p in parentSplit:
        parentWithSymbol += p if p not in setVariablesDictionary else setVariablesDictionary[p]+p
        parentWithSymbol +=','
    ##print "Exiting assignSYmbols"
    return  parentWithSymbol[:-1]

def moveHiddenVariablesOut(CPTform,summation):
    ##print "moving hidden variables"
    numberOfSummations = len(summation)
    ##print numberOfSummations
    ##print summation
    for last_summation in reversed(summation):
        # last_summation = summation[i]
        ##print last_summation
        summation_var = last_summation.split('|')[0]
        ##print summation_var
        if summation[-1]==last_summation:
            things_check = CPTform[CPTform.index(last_summation)+1:]
        else:
            indexOfLastSummation = summation.index(last_summation)
            nextVar = summation[indexOfLastSummation+1]
            things_check = CPTform[CPTform.index(last_summation) + 1:CPTform.index(nextVar)]
        ##print things_check
        for things in things_check:
            if summation_var not in things:
                ##print things
                ##print CPTform
                ##print things in CPTform
                CPTform.remove(things)
                CPTform.insert(CPTform.index(last_summation),things)
            ##print CPTform
    return CPTform

def sumOut(CPTqueryTobeSolved, variableToBeSummedOut, wholeVarTerm, nodes, CPT):
    temp_nodes = list(nodes)
    temp_CPT = list(CPT)
    # ##print type(temp_CPTqueryTobeSolved)
    temp_CPTqueryTobeSolved = list(CPTqueryTobeSolved)
    ##print "---------------------------------------------------"
    ##print "Entering sum out function"
    ##print "---------------------------------------------------"
    factors={}
    ##print "Location of the variable in the term is:"
    summationIndex = temp_CPTqueryTobeSolved.index(wholeVarTerm)
    ##print summationIndex
    relevantTerms = temp_CPTqueryTobeSolved[summationIndex:]
    ##print "Relevant terms which can be summed out are:"
    ##print relevantTerms
    relevantFactors = findRelevantFactors(relevantTerms,variableToBeSummedOut)
    ##print "Relevant Factors are:"
    ##print relevantFactors
    ##print "Size of factors table will be "
    ##print 2**len(relevantFactors)
    if len(relevantFactors) !=0:
        factors['factors']=relevantFactors
        ##print"Factors initially consists of this which is just the arguments on which this factor is dependant on"
        ##print factors
        ##print "variable getting summed out is"
        ##print variableToBeSummedOut
        ##print "Term to be summed out is "
        ##print wholeVarTerm
        ##print "Query to be solved is"
        ##print temp_CPTqueryTobeSolved
        factorObject = makeFactor(variableToBeSummedOut,relevantTerms,relevantFactors,temp_nodes,temp_CPT)
        factors['factorTable']=factorObject
        modifiedCPTquery = temp_CPTqueryTobeSolved[0:summationIndex]
        modifiedCPTquery.append(factors)
    else:
        modifiedCPTquery = temp_CPTqueryTobeSolved[0:summationIndex]
    ##print "---------------------------------------------------"
    ##print "new CPT table is "
    ##print modifiedCPTquery
    ##print "---------------------------------------------------"
    return modifiedCPTquery

def findRelevantFactors(relevantTerms,variableToBeSummedOut):
    ##print "----------------------"
    ##print "Entering findRelevantFactors"
    ##print "----------------------"
    relevantFactors=set()
    for term in relevantTerms:
        ##print "Term considered is"
        ##print term
        if type(term)== str:
            ##print "its a string"
            vars=term.split('|')
            firstTerm = vars[0]
            ##print "First term is"
            ##print firstTerm
            if not firstTerm[0]=='+' and not firstTerm[0]=='-':
                if firstTerm != variableToBeSummedOut:
                    relevantFactors.add(firstTerm)
            if vars[1] != 'None':
                secTerm = vars[1].split(',')
                ##print "Second Term is"
                ##print secTerm
                for term in secTerm:
                    ##print "Term is :"
                    ##print term
                    ##print "Does it not have a sign"
                    if not term[0]=='+' and not term[0]=='-':
                        if term != variableToBeSummedOut:
                            relevantFactors.add(term)
        else:
            ##print "its a factor"
            relFactors = term['factors']#factors is key in the factor dictionary
            ##print "this is already a function of"
            ##print relFactors
            for fac in relFactors:
                ##print "Term being considered is"
                ##print fac
                if not fac[0] == '+' and not fac[0] == '-':
                    if fac != variableToBeSummedOut:
                        relevantFactors.add(fac)
    ##print "Exiting find relevant factors"
    ##print "-----------------------------------"
    return relevantFactors

def makeFactor(variableToBeSummedOut,relevantTerms,relevantFactors,nodes,CPT):
    ##print "-------------------------------------------"
    ##print "making Factors"
    ##print "-------------------------------------------"
    # returns a dictionary containig factors tables
    #produce all combinations fist
    factorArray=[]
    factorObject = {}
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    for factor in relevantFactors:
        tempSet=set()
        tempSet.add('+'+factor)
        tempSet.add('-'+factor)
        factorArray.append(tempSet)
    ##print "All possible variables are"
    ##print factorArray
    ##print "Permutations are"
    combos = list(set(tup) for tup in itertools.product(*factorArray))
    ##print [combo for combo in combos]
    ##print "Terms being considered"
    ##print relevantTerms
    for combo in combos:
        tempRelevantTerms = list(relevantTerms)
        ##print "Combo considered is"
        ##print combo
        ##print "relevant terms before evaluating"
        ##print tempRelevantTerms
        sumForCombo=evaluate(combo,tempRelevantTerms,variableToBeSummedOut,temp_nodes,temp_CPT)
        ##print "Type of combo is"
        ##print type(combo)
        factorObject[frozenset(combo)]=sumForCombo
    ##print "------------------------------------"
    ##print "Presenting the factor object !!!!!!"
    ##print "------------------------------------"
    ##print "==================================================="
    ##print factorObject
    ##print "==================================================="
    return factorObject

def evaluate(combo,RelevantTerms,variableToBeSummedOut,nodes,CPT):
    tempRelevantTerms=copy.deepcopy(RelevantTerms)
    temp_nodes = list(nodes)
    temp_CPT = list(CPT)
    ##print "----------------"
    ##print "Evaluating Node"
    ##print "-----------------"
    for node in combo:
        ##print "Node is"
        ##print node
        symbol = node[0]
        ##print "symbol is"
        # ##print symbol
        var=node[1:]
        ##print "var is"
        ##print var
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

    ##print "After evaluating"
    ##print tempRelevantTerms
    ##print "Variable to be summedOut"
    ##print variableToBeSummedOut
    tempRelevantTermsCopy = copy.deepcopy(tempRelevantTerms)
    positiveSum = findSum('+',tempRelevantTermsCopy,variableToBeSummedOut,nodes,CPT)
    ##print "After positive sum relative terms is"
    ##print tempRelevantTermsCopy
    tempRelevantTermsCopy2 = copy.deepcopy(tempRelevantTerms)
    ##print "Before Negative sum the relative terms is"
    ##print tempRelevantTermsCopy2
    negativeSum = findSum('-',tempRelevantTermsCopy2,variableToBeSummedOut,nodes,CPT)

    sum= positiveSum+negativeSum
    ##print "Value for Combo: " + str(combo)
    ##print sum
    return sum

def replaceTerm(term,var,node):
    ##print "term before replacing is"
    ##print term
    term2 = term.split('|')
    left = term2[0]
    right = term2[1]
    ##print "left is :" + str(left)
    if not isFixed(left):
        if var == left:
            left = node
    ##print "right is:" + str(right)
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
    # term = term.replace(var,node)
    ##print "term after replacing is "
    ##print term
    return term

def isFixed(var):
    if var[0]=='+' or var[0] =='-':
        return True
    else:
        return False

def findSum(sign, tempRelevantTerms, variableToBeSummedOut, nodes, CPT):
    ##print "----------------"
    ##print "Entering find sum"
    ##print "----------------"
    tempRelevantTerms2 = list(tempRelevantTerms)
    if variableToBeSummedOut != '':
        signedVar=sign+variableToBeSummedOut
        for term in tempRelevantTerms2:
            index = tempRelevantTerms2.index(term)
            if type(term)==str:
                ##print "Its a string"
                # ##print "term before replacing is"
                # ##print term
                terms2 = replaceTerm(term,variableToBeSummedOut,signedVar)
                # ##print "term after replacing is "
                # ##print term
                tempRelevantTerms2[index] = terms2
            else:
                ##print "Factor detecteed"
                dependantFactors=term['factors']
                ##print "Dependences are"
                ##print dependantFactors
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

    ##print sign+" terms would be"
    ##print tempRelevantTerms2
    probability = lookUpProbability(tempRelevantTerms2, nodes, CPT)
    return probability

def lookUpProbability(tempRelevantTerms, nodes, CPT):
    ##print "-------------------------------------"
    ##print "Looking up probabilities"
    ##print "--------------------------------------"
    tempRelevantTerms2 = list(tempRelevantTerms)
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    ##print "Terms are"
    ##print tempRelevantTerms2
    # ##print temp_nodes
    # ##print temp_CPT
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
                    ##print pTable[parentsSet]
                    product *= pTable[parentsSet]
                else:
                    product *= (1-pTable[parentsSet])
                    ##print (1 - pTable[parentsSet])
            else:
                if pTable[None] != 'decision':
                    if symbol == '+':
                        product *= pTable[None]
                        ##print pTable[None]
                    else:
                        product *= (1-pTable[None])
                        ##print pTable[None]
        else:
            fixedTerm = term['fixedVars']
            ##print "Fixed Term is "
            ##print fixedTerm
            factorTable = term['factorTable']
            ##print "Its probability is"
            ##print factorTable[frozenset(fixedTerm)]
            product *= factorTable[frozenset(fixedTerm)]

    ##print "final product is"
    ##print product
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
    ##print "NUMERATOR COMBO IS !!!!!!!!!!!"
    ##print combo
    sum=evaluate(combo,temp_reducedQuery,'',temp_nodes,temp_CPT)
    ##print "NUMERATOR SUM IS======================="
    return sum

def calculateDenominator(reducedQuery,variables,nodes,CPT):
    combos = makeCombo(variables) #list of combinations, each combination is a set
    temp_reducedQuery = copy.deepcopy(reducedQuery)
    temp_nodes=list(nodes)
    temp_CPT=list(CPT)
    sum=0
    ##print "========================================="
    ##print "Trying to use the same evaluate function"
    ##print "============================================="
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
    ##print "reduced query in main is"
    ##print reducedQuery
    variables = findRelevantFactors(reducedQuery, '')
    ##print variables
    query_vars = makeJointProbability(q, nodes)[0]
    ##print "In main the query variables are"
    ##print query_vars
    probability = calculateProbability(query_vars, reducedQuery, variables, nodes, CPT)

    ##print round(probability, 2)

    ##print "And the set nodes are"
    ##print set_nodes_dictionary

    return probability

def findEU(EUquery,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary):
    eu_nodes_fixed = findFixedNodes(EUquery)
    ##print "Utility Nodes are:"
    ##print utilityNodes
    ##print "These are the nodes already fixed"
    ##print eu_nodes_fixed
    findCombo = makeUtilityCombo(utilityNodes, eu_nodes_fixed)
    utilityCombo = findCombo[0]
    fixed_util_dictionary = findCombo[1]
    ##print "all utility combos are"
    ##print utilityCombo
    ##print "all fixed util nodes are"
    ##print fixed_util_dictionary
    temp_utilityCombo = copy.deepcopy(utilityCombo)
    temp_eu_nodes_fixed = copy.deepcopy(eu_nodes_fixed)
    ##print "EUEUEUEUEUEUEUEUEUEUEUEUEUEUEUEUUEUEUEUEUEUEUEUEUEU"
    ##print "utility combo considered is"
    ##print temp_utilityCombo
    ##print "fixed nodes are"
    ##print temp_eu_nodes_fixed
    ExpectedUtility =0
    for combo in temp_utilityCombo:
        ##print "combo is"
        ##print combo
        left=''
        comboset = set()
        for elements in combo:
            sign = elements[0]
            thisElm = elements[1:]+" = "+sign+", "
            left+=thisElm
            comboset.add(elements)
        left = left.strip()
        left=left[:-1]#removes the ,
        ##print "left is"
        ##print left
        right=''
        for elements in temp_eu_nodes_fixed:
            sign = temp_eu_nodes_fixed[elements]
            thisElm = elements + " = " + sign + ", "
            right += thisElm
        right = right.strip()
        right = right[:-1]  # removes the ,
        ##print "right is"
        ##print right
        probabilityQuery = 'P('+left+" | "+right+")"
        ##print "Probabilitty Query is"
        ##print probabilityQuery
        for fixed_util_node in fixed_util_dictionary:
            symbol=fixed_util_dictionary[fixed_util_node]
            toBeAdded= symbol+fixed_util_node
            comboset.add(toBeAdded)

        ExpectedUtility += findProbabilty(probabilityQuery,nodes,CPT,parentsDictionary)*utilityDictionary[frozenset(comboset)]
    ##print "******************************************************"
    ##print "EXPECTED UTILITY IS"
    ##print int(round(ExpectedUtility))
    ##print "******************************************************"
    return ExpectedUtility

def makeEUsfromMEUs(MEUquery):
    ##print "Making EUS from MEUs"
    EUfromMEUQueries=[]
    query=MEUquery[4:-1]
    query = query.split('|')
    util_nodes = query[0]
    conditionals = query[1] if len(query)>1 else None
    util_nodes=util_nodes.replace(' ','')
    util_nodes=util_nodes.split(',')
    ##print "util nodes are"
    ##print util_nodes
    combos = makeCombo(util_nodes)
    ##print "Combos are"
    ##print combos
    for combo in combos:
        EUQuery=''
        ##print "combo is"
        ##print combo
        left = ''
        comboset = set()
        for elements in combo:
            sign = elements[0]
            thisElm = elements[1:] + " = " + sign + ", "
            left += thisElm
            comboset.add(elements)
        left = left.strip()
        left = left[:-1]  # removes the ,
        ##print "left is"
        ##print left
        #right side
        if len(query)>1:
            right = conditionals.strip()
            EUQuery='EU('+left+" | "+right+")"
        else:
            EUQuery='EU('+left+")"
        # ##print "EU query for the combo" + str(combo) + "is:"
        EUfromMEUQueries.append(EUQuery)
    return EUfromMEUQueries

def findMEU(EUfromMEUqueries,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary):
    value=float('-inf')
    highestQuery=''
    for EUquery in EUfromMEUqueries:
        ##print "EUquery is"
        ##print EUquery
        EUval = findEU(EUquery,utilityNodes,utilityDictionary,nodes,CPT,parentsDictionary)
        ##print "value of EUval is"
        ##print EUval
        if EUval>value:
            value=EUval
            highestQuery=EUquery
    return [value,highestQuery]

def findHighest(highest_combo,MEUquery):
    relevantVars=highest_combo[3:-1]
    ##print relevantVars
    relevantVars = relevantVars.split('|')[0]
    ##print relevantVars
    relevantVars = relevantVars.replace(' ','')
    ##print relevantVars
    relevantVars=relevantVars.split(',')
    ##print relevantVars
    varDict={}
    for var in relevantVars:
        var=var.split('=')
        ##print var
        varDict[var[0]]=var[1]
    ##print varDict
    highVarSymbols=''
    temp_MEUquery=MEUquery[4:-1]
    ##print temp_MEUquery
    temp_MEUquery=temp_MEUquery.split('|')[0]
    ##print temp_MEUquery
    temp_MEUquery=temp_MEUquery.replace(' ','')
    temp_MEUquery=temp_MEUquery.split(',')
    ##print temp_MEUquery
    for var in temp_MEUquery:
        highVarSymbols+=varDict[var]+' '
    highVarSymbols = highVarSymbols.rstrip()
    ##print highVarSymbols
    return highVarSymbols



if __name__ == '__main__':
    main()