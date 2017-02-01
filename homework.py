from kbObject import kbObject
import re
import copy

#####################################################
#############3#CONTENTS OF PARSER.PY#################

import ply.lex as lex
import ply.yacc as yacc
from cnf import SimplificationTree
from literal import Literal
import sys
#Define Tokens
tokens = (
   'STRING',
   'AND',
   'OR',
   'INFERENCE',
   'NEG',
   'VARIABLE',
   'LPAREN',
   'RPAREN',
)
#Ignore Spaces and Tabs
t_ignore  = ' \t'
#Define Regex for each token.
t_STRING = r'[a-zA-Z0-9]+(\,[a-zA-Z0-9]*)*'
t_AND = r'\&'
t_OR = r'\|'
t_INFERENCE = r'\=\>'
t_NEG = r'\~'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def p_SENTENCE(t):
    '''SENTENCE : LPAREN SENTENCE AND SENTENCE RPAREN
            | LPAREN SENTENCE OR SENTENCE RPAREN
            | LPAREN SENTENCE INFERENCE SENTENCE RPAREN
            | ATOMIC_SENTENCE'''
    if t[1] =="(":
        t[0] = SimplificationTree(t[2], t[3], t[4], "SENTENCE")
        # print t[0].__class__.__name__
        # printtree(t[0])
    else:
        t[0] = t[1]
        # print printtree(t[0])

def p_ATOMIC_SENTENCE(t):
    '''ATOMIC_SENTENCE : STRING LPAREN STRING RPAREN'''
    t[0] = Literal(t[1], t[3], "ATOMIC_SENTENCE")
    # print t[0]

def p_NEGATED_SENTENCE(t):
    '''ATOMIC_SENTENCE : LPAREN NEG SENTENCE RPAREN'''
    t[0] = SimplificationTree(t[3], t[2], "null", "ATOMIC_SENTENCE")

def parseline():
    inputFile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    input_data = open(inputFile)
    totallines = input_data.readlines()
    n = int(totallines[0].rstrip())
    for i in range(n+2, len(totallines)):
        line = totallines[i].rstrip()
        temp = yacc.parse(line)
        temp = remove_inference(temp)
        temp = push_negation_inwards(temp)
        temp = move_and_outwards(temp)
        temp = and_separation(temp)
        printtree(temp)
        textwriter.write("\n")
        print


def remove_inference(t):
    if t.__class__.__name__ == "Literal":
        return t
    elif t.op == "~" and t.left.__class__.__name__ =="Literal":
        return t
    elif t.op == "=>":
        temp = SimplificationTree(t.left, "~", "null", "SENTENCE")
        t.op = "|"
        t.left = temp
    t.left = remove_inference(t.left)
    if t.right != "null":
        t.right = remove_inference(t.right)
    return t



def printtree(t):
    if t.__class__.__name__ == "Literal":
        print t,
        textwriter.write(t.predicate + "(" + t.values + ")")
    elif t.__class__.__name__ == "SimplificationTree":
        if t.op != "~":
            print "(",
            textwriter.write("(")
            printtree(t.left),
            print t.op,
            textwriter.write(t.op)
            printtree(t.right),
            print ")",
            textwriter.write(")")
        else:
            print "(",
            textwriter.write("(")
            print t.op,
            textwriter.write(t.op)
            printtree(t.left),
            print ")",
            textwriter.write(")")




def push_negation_inwards(t):
    if t.__class__.__name__ == "Literal":
        return t
    if t.op == "~" and t.left.__class__.__name__ != "Literal":
        l = t.left
        if l.op == "~":
            return push_negation_inwards(l.left)
        elif l.op == "&":
            return push_negation_inwards(SimplificationTree(SimplificationTree(l.left, "~", "null", "SENTENCE"), "|", SimplificationTree(l.right, "~", "null", "SENTENCE"), "SENTENCE"))
        elif l.op == "|":
            return push_negation_inwards(SimplificationTree(SimplificationTree(l.left, "~", "null", "SENTENCE"), "&", SimplificationTree(l.right, "~", "null", "SENTENCE"), "SENTENCE"))
    else:
        t.left = push_negation_inwards(t.left)
        if t.right != "null":
            t.right = push_negation_inwards(t.right)
    return t

def move_and_outwards(t):
    #stop recursion if Literal
    if t != "null":
        if t.__class__.__name__ == "Literal":
            return t
        if t.op == "|":
            l = t.left
            r = t.right
            if l.__class__.__name__ == "SimplificationTree":
                if l.op =="&":
                    return move_and_outwards(SimplificationTree(SimplificationTree(l.left, "|", r, "SENTENCE"), "&", SimplificationTree(l.right, "|", r, "SENTENCE"), "SENTENCE"))
            if r.__class__.__name__ == "SimplificationTree":
                if r.op =="&":
                    return move_and_outwards(SimplificationTree(SimplificationTree(r.left, "|", l, "SENTENCE"), "&", SimplificationTree(r.right, "|", l, "SENTENCE"), "SENTENCE"))
        else:
            t.left = move_and_outwards(t.left)
            t.right = move_and_outwards(t.right)
    return t

def and_separation(t):
    if t.__class__.__name__ == "SimplificationTree":
        if t.op != "&":
            printtree(t)
        else:
            printtree(and_separation(t.left))
            textwriter.write("\n")
            printtree(and_separation(t.right))
            textwriter.write("\n")
    else:
        printtree(t)
        textwriter.write("\n")




textwriter=open("kb.txt", "w")
lexer = lex.lex()
yacc.yacc()
parseline()

textwriter.close()






















###############################################################################
#               CONTENTS of KBManipulation.py                                 #
###############################################################################






def ConvertLinetoObject(a):
    n = "N"
    if a[0] == "~":
        n = "Y"
        a = a[1:]
    p = re.search(r'[a-zA-Z]+\(', a)
    pr = p.group()
    pr = pr[:-1]
    values_with_parens = re.search('\([a-zA-Z]+(\,[a-zA-Z]+)*\)', a)
    values_with_parens = values_with_parens.group()
    values_with_parens = values_with_parens[1:-1]
    v = values_with_parens.split(",")
    return(kbObject(pr,v,n))

def GetSubstitutions(obj, q):
    a={}
    for i in range(len(obj.values)):
        if obj.values[i] != q.values[i]:
            if len(obj.values[i]) == 1 and len(q.values[i]) > 1:
                a[obj.values[i]] = q.values[i]
            if len(obj.values[i]) > 1 and len(q.values[i]) == 1:
                a[q.values[i]] = obj.values[i]
    return a

# def printsentence(s):
#     for word in s:
#         print word,



def Substitution(line, q, subs):
    #Substitution: Iterate through obj.values in both Line and querySentence and do Substitution.
    for key,value in subs.items():
        for obj in line:
            obj.values = [value if val == key else val for val in obj.values]
        for obj in q:
            obj.values = [value if val == key else val for val in obj.values]
    return line, q

def Unification(line,q):
    #Unification: Remove those predicates which have same predicates and are negated
    # print "Unifying ",line, "and", q
    for obj in line:
        for qobj in q:
            if obj.predicate == qobj.predicate and obj.n != qobj.n:
                if cmp(obj.values, qobj.values) == 0:
                #Remove theose objects from line and querySentence
                    line.remove(obj)
                    q.remove(qobj)
    # print "After Unification"
    # print line + q
    return (line + q)

def notalreadyconputed(q):
    for sentence in completed_refutations:
        if cmp(sentence, q) == 0:
            return False
    return True

#Find KB line which has an object whose predicate = query.predicate
def refutation(q, level):
    # print
    # print level
    # print
    # print
    # print "Refuting"
    # print q
    Subs = {}
    for query in q:
        for i in KBDict:
            # print "Checking the next sentence in the KB, for a match to", query
            # print
            # printsentence(i)
            # print
            for objs in i:
                if objs.predicate == query.predicate and objs.n != query.n:
                    #Found a negation.
                    # print "Considering line", i
                    Subs = GetSubstitutions(objs, query)
                    # print "subs are ",
                    # for key,value in Subs.items():
                    #     print key,value
                    line = copy.deepcopy(i)
                    temp = copy.deepcopy(q)
                    if len(Subs) != 0:
                        line,temp = Substitution(line, temp, Subs)
                    refutedquery = Unification(line,temp)
                    print len(refutedquery),len(i), len(q)
                    if len(refutedquery) == 0:
                        return "TRUE"
                    elif len(refutedquery) < (len(i) + len(q)):
                        if str(refutedquery) not in completed_refutations:
                            # for i in completed_refutations:
                            #     print (i)
                            print
                            completed_refutations.append(refutedquery)
                            res = refutation(refutedquery, level+1)
                            if res == "TRUE":
                                return "TRUE"
    return "FALSE"

allqueries = []
completed_refutations = []
KBDict = []


FileReader = open("kb.txt")
KBLines = FileReader.readlines()
for i in KBLines:
    i = i.rstrip()
    if i != "":
        arr=[]
        a = re.findall(r'\~?[a-zA-Z]+\([a-zA-Z]+[\,[a-zA-Z]*]*\)', i)
        if type(a) != "NoneType":
            for o in a:
                x = ConvertLinetoObject(o)
                arr.append(x)
        KBDict.append(arr)

# print KBDict
teller = open("output.txt", "w")
asker = open("input.txt")
numqueries = int(asker.readline())
for i in range(numqueries):
    allqueries.append(asker.readline())
# print allqueries
for query in allqueries:
    completed_refutations = []
    query = ConvertLinetoObject(query.rstrip())
    negated_query = query
    if query.n == "N":
        negated_query.n = "Y"
    else:
        negated_query.n = "N"
    #
    # for i in KBDict:
    #     printsentence(i)
    #     print "\n"
    querySentence = [negated_query]
    completed_refutations.append(str(querySentence))
    # print querySentence
    res = refutation(querySentence, 0)
    print res
    teller.write(res+"\n")
