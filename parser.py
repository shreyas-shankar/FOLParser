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
t_STRING = r'[a-zA-Z]+[\,a-zA-Z]*'
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
    '''SENTENCE : LPAREN NEG SENTENCE RPAREN'''
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
        print "before moving and outwards"
        printtree(temp)
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
data = 'man(joe) | woman(x)'
yacc.yacc()
parseline()
