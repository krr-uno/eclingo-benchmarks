#!/usr/bin/env python3

from lark import Lark
from lark import Transformer
import collections
import itertools
import sys
import argparse
import subprocess
import re

# input must not contain predicates with names beginning with "n_" or "tmp_".
argumentParser = argparse.ArgumentParser(description='reads in non-ground extended arithmetic EASP-not (optionally with limited sorts), grounds it, and outputs the program in ground EASP-not syntax with strong negation compiled away to new predicates prefixed with "n_". Abuses gringo for doing that. "limited sorts" because not all features of the sorts syntax are supported.')
argumentParser.add_argument('-i', metavar='FILE', type=argparse.FileType('r'), default=sys.stdin, help='non-ground extended arithmetic EASP-not input file (default standard input)')
argumentParser.add_argument('-o', metavar='FILE', type=argparse.FileType('w'), default=sys.stdout, help='ground EASP-not output file (default standard output)')
argumentParser.add_argument('-s', '--syntax', choices=['ELPS', 'ELP'], default='ELPS', help='input syntax. ELPS: non-ground extended EASP-not with limited sorts (default); ELP: same without sorts')
argumentParser.add_argument('-g', '--gringo', metavar='PATH', default='gringo', help='path to the gringo executable (default: "gringo")')
argumentParser.add_argument('--print-intermediate', action='store_true', help='prints the ASP program that gringo would get; does not perform any grounding')
#TODO additional option: print ELP: prints the input program in without sorts
args = argumentParser.parse_args()

# some class definitions for representing EASP syntax: (atoms are just represented by strings)
class Atom:
  def __init__(self, predName, arguments): # arguments is a collection of strings
    self.predName = predName
    self.arguments = arguments
  def __repr__(self):
    if len(self.arguments) == 0:
      return self.predName
    else:
      return self.predName + '(' + ','.join(self.arguments) + ')'
class ClassicalLiteral:
  def __init__(self, atom, positive):
    self.atom = atom
    self.positive = positive
  def __repr__(self):
    if self.positive:
      return repr(self.atom)
    else:
      return '-' + repr(self.atom)
class ObjectiveLiteral:
  def __init__(self, clasLit, positive):
    self.clasLit = clasLit
    self.positive = positive
  def __repr__(self):
    if self.positive:
      return repr(self.clasLit)
    else:
      return 'not ' + repr(self.clasLit)
class BodyElement:
  def __init__(self, positive):
    self.positive = positive
class ObjectiveBodyElement(BodyElement):
  def __init__(self, objLit):
    super(ObjectiveBodyElement, self).__init__(objLit.positive)
    self.objLit = objLit
  def __repr__(self):
    return repr(self.objLit)
class SubjectiveBodyElement(BodyElement):
  def __init__(self, positive, objLit):
    super(SubjectiveBodyElement, self).__init__(positive)
    self.objLit = objLit
  def __repr__(self):
    if self.positive:
      return '$not$ ' + repr(self.objLit)
    else:
      return 'not $not$ ' + repr(self.objLit)
class Rule:
  def __init__(self, head=None, body=None):
    if head is None:
      head = []
    if body is None:
      body = []
    self.head = head
    self.body = body
  def __repr__(self):
    return ' | '.join(map(lambda e : repr(e), self.head)) + ' :- ' + ', '.join(map(lambda e : e if isinstance(e, str) else repr(e), self.body)) + '.'

# transformer that transforms the parsed ELPS syntax tree into our representation:
class ElpsSyntaxTreeTransformer(Transformer):
  def constant(self, children):
    return children[0]
  def constants(self, children): # iterable of strings
    return children
  def ids(self, children): # iterable of ids as strings
    return map(lambda c : c.value, children)
  def sort_name(self, children):
    return children[0].value
  def sort_names(self, children): #iterable of sort names as strings
    return children
  def ground_set_sort(self, children): # pair (n,d) where n is the sort name and d an iterable representing its domain
    sortname = children[0]
    if len(children) == 1:
      return sortname, []
    else:
      return sortname, children[1]
  def numrange_sort(self, children): # pair (n,d) where n is the sort name and d an iterable representing its domain
    sortname = children[0]
    beg = int(children[1].value)
    end = int(children[2].value)
    return sortname, map(lambda n : str(n), range(beg, end+1))
  def sorts(self, children): # dict mapping sort names to their respective frozenset of domain
    return {n:d for (n,d) in children}
  def predicate(self, children): # pair (n,s) where n is the predicate name and s an iterable of its sorts
    predname = children[0]
    if len(children) == 1:
      return predname, []
    else:
      return predname, children[1]
  def predicates(self, children): # iterable of pairs (n,s) as from the "predicate" function
    return children
  def rules(self, children): #iterable of all rules
    return children
  def term_id(self, children): #string
    return children[0].value
  def term_arithterm(self, children): #string
    return children[0]
  def arithterm(self, children): #string
    return children[0].value
  def arithterm_paren(self, children): #string
    return '(' + children[0] + ')'
  def arithterm_minus(self, children): #string
    return '-' + children[0]
  def arithterm_arithop(self, children): #string
    return children[0] + children[1].value + children[2]
  def arithterm_minusop(self, children): #string. Has to be extra in grammar because LARK doesn't resolve conflicts
    return children[0] + '-' + children[1]
  def terms(self, children):
    return children
  def atom(self, children):
    predName = children[0].value
    if len(children) == 1:
      return Atom(predName, [])
    else:
      return Atom(predName, children[1])
  def pos_clas_lit(self, children):
    return ClassicalLiteral(children[0], True)
  def neg_clas_lit(self, children):
    return ClassicalLiteral(children[0], False)
  def poslit(self, children):
    return ObjectiveLiteral(children[0], True)
  def neglit(self, children):
    return ObjectiveLiteral(children[1], False)
  def bo(self, children):
    return ObjectiveBodyElement(children[0])
  def bs_pos(self, children):
    return SubjectiveBodyElement(True, children[1])
  def bs_neg(self, children):
    return SubjectiveBodyElement(False, children[2])
  def builtin_atom(self, children): # string
    return children[0] + children[1].value + children[2]
  def body(self, children): # list of BodyElement objects and strings
    return list(children)
  def head(self, children):
    return list(children)
  def emptyrule(self, children):
    return Rule()
  def constraint(self, children):
    return Rule(body=children[0])
  def fact(self, children):
    return Rule(head=children[0])
  def regularrule(self, children):
    return Rule(head=children[0], body=children[1])
  def program(self, children): # triplet (s,p,r), with s=sorts, p=predicates, r=rules as described above
    return children[0], children[1], children[2]

elpsGrammar = r'''
    
    program: "sorts" sorts "predicates" predicates "rules" rules
    
    sorts: sort*
    sort: sort_name "=" "{" constants? "}" "." -> ground_set_sort
        | sort_name "=" NUMBER ".." NUMBER "." -> numrange_sort
    
    predicates: predicate*
    predicate: ID "(" sort_names? ")" "."
    
    sort_names: sort_name ("," sort_name)*
    sort_name: "#" ID
    
    rules: rule*
      
    ids: ID ("," ID)*
        
    rule: ":-" "."           -> emptyrule
        | ":-" body "."      -> constraint
        | head "."           -> fact
        | head ":-" "."      -> fact
        | head ":-" body "." -> regularrule
    
    head: classical_literal ("|" classical_literal)*
    
    body: bodyelement ("," bodyelement)*
      
    bodyelement: objectiveliteral              -> bo
              | EPNEG objectiveliteral        -> bs_pos
              | DEFNEG EPNEG objectiveliteral -> bs_neg
              | arithterm BINOP arithterm     -> builtin_atom
    
    objectiveliteral: classical_literal        -> poslit
                    | DEFNEG classical_literal -> neglit
    
    classical_literal: atom     -> pos_clas_lit
                    | "-" atom -> neg_clas_lit
    
    atom : ID ("(" terms? ")")?
    
    terms: term ("," term)*

    term: ID        -> term_id
        | arithterm -> term_arithterm
        
    arithterm: NUMBER                      -> arithterm
            | VARIABLE                    -> arithterm
            | "(" arithterm ")"           -> arithterm_paren
            | "-" arithterm               -> arithterm_minus
            | arithterm ARITHOP arithterm -> arithterm_arithop
            | arithterm "-" arithterm     -> arithterm_minusop
        
    constant: ID
            | NUMBER
            
    constants: constant ("," constant)*
        
    EPNEG: "$not$"
    
    DEFNEG: "not"
        
    ID: /[a-z][A-Za-z0-9_]*/
      
    VARIABLE: /[A-Z][A-Za-z0-9_]*/
    
    COMMENT: "%" ( /[^*\n]/ /[^\n]/* )? NEWLINE

    MULTILINE_COMMENT: "%*" ( /[^*]/ | /\*[^%]/ )* "*%"
    
    ARITHOP: "+" | "*" | "/"
    
    BINOP: "=" | "!=" | "<" | ">"
    
    %import common.INT -> NUMBER
    %import common.WS
    %import common.NEWLINE
    %ignore COMMENT
    %ignore MULTILINE_COMMENT
    %ignore WS
    %ignore NEWLINE
    
    '''

# ELP(S) grammar parser:
if args.syntax == 'ELPS':
  startSymbol = 'program'
else:
  startSymbol = 'rules'
parser = Lark(elpsGrammar, start=startSymbol, parser='lalr', transformer=ElpsSyntaxTreeTransformer())

def replaceStrongNegation(classicalLiteral): # manipulates the given literal from "-a(X)" to "n_a(X)" (with X being an n-ary tuple of terms) and returns as a string the constraint ":- a(Y), n_a(Y).", where Y is an n-ary tuple of (new) variables.
  assert not classicalLiteral.positive
  basePredName = classicalLiteral.atom.predName
  arity = len(classicalLiteral.atom.arguments)
  varlist = ','.join('X'+str(i) for i in range(arity))
  classicalLiteral.positive = True
  classicalLiteral.atom.predName = 'n_' + basePredName
  return ':- ' + basePredName + '(' + varlist + '), ' + classicalLiteral.atom.predName + '(' + varlist + ').'
  #constraint = Rule(body=[ObjectiveLiteral(ClassicalLiteral(Atom(basePredName, varlist), True), True), ObjectiveLiteral(ClassicalLiteral(Atom(classicalLiteral.atom.predName, varlist), True), True)])
  #return constraint

if args.syntax == 'ELPS':
  sorts, predicates, rules = parser.parse(args.i.read())
else:
  rules = parser.parse(args.i.read())
newProgram = collections.deque() # list of rules, each rule represented as a string.
# first, compile away strong negation: if "-a" occurs in the program, replace it by "n_a" and add rule ":- a, n_a, d_a"
createdConstraints = set() # set of strings
for r in rules:
  for clasLit in r.head:
    if not clasLit.positive:
      createdConstraints.add(replaceStrongNegation(clasLit))
  for bodyEl in r.body:
    if not isinstance(bodyEl, str):
      clasLit = bodyEl.objLit.clasLit
      if not clasLit.positive:
        createdConstraints.add(replaceStrongNegation(clasLit))
newProgram.extend(createdConstraints)
# now, rules is free of strong negations.
if args.syntax == 'ELPS':
  # create sorts facts:
  for (n,d) in sorts.items():
    newProgram.extend('tmp_sort_'+n+'('+c+').' for c in d)
  # add to each objective literal the domain closure, also for its "n_" predicate:
  for (n,ss) in predicates:
    ss = list(ss)
    variables = ['X'+str(i) for i in range(len(ss))]
    newProgram.append('tmp_domain_'+n+'('+','.join(variables)+') :- ' + ', '.join('tmp_sort_'+ss[i]+'('+variables[i]+')' for i in range(len(ss))) + '.')
    newProgram.append('tmp_domain_n_'+n+'('+','.join(variables)+') :- ' + 'tmp_domain_'+n+'('+','.join(variables)+').')
# now replace each epistemic negation $not$ l by "tmp_epnot_l" (tmp_epnot_1_l for positive, tmp_epnot_0_l for default-negated subjective literals) and add guesses "tmp_epnot_l | -tmp_epnot_l :- tmp_domain_l". Additonally, add domain closure atoms for atoms occuring in the default-negated body or the rule head (if we're dealing with a sorts program):
createdGuesses = set() #stings
for r in rules:
  translatedRule = Rule()
  potentiallyUnsafeAtoms = set()
  for clasLit in r.head:
    potentiallyUnsafeAtoms.add(clasLit.atom)
    translatedRule.head.append(clasLit)
  for bodyElement in r.body:
    if not isinstance(bodyElement, str) and not bodyElement.positive:
      potentiallyUnsafeAtoms.add(bodyElement.objLit.clasLit.atom)
    if isinstance(bodyElement, SubjectiveBodyElement): # e.g. "not $not$ not haha(X, Y, joe)"
      newPredName = 'tmp_epnot_'
      if bodyElement.objLit.positive:
        newPredName = newPredName + '1_'
      else:
        newPredName = newPredName + '0_'
      newPredName = newPredName + bodyElement.objLit.clasLit.atom.predName # e.g. "tmp_epnot_0_haha"
      newAtom = Atom(newPredName, bodyElement.objLit.clasLit.atom.arguments) # e.g. "tmp_epnot_0_haha(X, Y, joe)"
      translatedRule.body.append(ObjectiveBodyElement(ObjectiveLiteral(ClassicalLiteral(newAtom, True), bodyElement.positive))) # e.g. "not tmp_epnot_0_haha(X, Y, joe)"
      guessVariables = ['X'+str(i) for i in range(len(newAtom.arguments))] # e.g. 'X0', 'X1', 'X2'
      guessAtom = newPredName + '('+','.join(guessVariables)+')' # e.g. "tmp_epnot_0_haha(X0,X1,X2)"
      if args.syntax == 'ELPS':
        createdGuesses.add(guessAtom + ' | -' + guessAtom + ' :- tmp_domain_' + bodyElement.objLit.clasLit.atom.predName + '('+','.join(guessVariables)+').') # e.g. "tmp_epnot_0_haha(X0,X1,X2) | -tmp_epnot_0_haha(X0,X1,X2) :- tmp_domain_haha(X0, X1, X2)."
      else:
        createdGuesses.add(str(newAtom) + ' | -' + str(newAtom) + ' :- ' + ', '.join(map(lambda e : str(e), filter(lambda e : isinstance(e, str) or (isinstance(e, ObjectiveBodyElement) and e.positive), r.body))) + '.') # e.g. "tmp_epnot_0_haha(X, Y, joe) | -tmp_epnot_0_haha(X, Y, joe) :- posbody1(X, Y), posbody2(joe, 4), Y = 6+0."
    else:
      translatedRule.body.append(bodyElement)
  if args.syntax == 'ELPS':
    for a in potentiallyUnsafeAtoms:
      domClosureAtom = Atom('tmp_domain_' + a.predName, a.arguments)
      translatedRule.body.append(ObjectiveBodyElement(ObjectiveLiteral(ClassicalLiteral(domClosureAtom, True), True)))
  newProgram.append(repr(translatedRule))
newProgram.extend(createdGuesses)

del rules
if args.syntax == 'ELPS':
  del sorts, predicates
  
if args.print_intermediate:
  print('\n'.join(newProgram), file=args.o)
  sys.exit()

#now, let gringo ground:
gringoOutput = subprocess.check_output([args.gringo, '-t', '-W', 'no-atom-undefined'], input='\n'.join(newProgram), universal_newlines=True)
del newProgram

rules = gringoOutput.split('\n')
# remove sort and domain facts and tmp_epnot guesses:
rules = filter(lambda r : not r.startswith(('tmp_', '-tmp_')), rules)
# remove constraints of the form ":-atom,-atom." (generated by gringo for tmp_epnot guesses):
def isTrivialConstraint(rule):
  if not re.match(':-.*\.', rule):
    return False
  rule = rule[2:-1]
  if len(rule) % 2 != 0:
    return False
  firstPart = rule[:int(len(rule)/2)-1]
  mid = rule[int(len(rule)/2)-1 : int(len(rule)/2)+1]
  secondPart = rule[int(len(rule)/2)+1:]
  if firstPart != secondPart:
    return False
  if not re.match('[a-z][A-Za-z0-9_]*(\\(()|([A-Za-z0-9_]*(,[A-Za-z0-9_]*)*)\\))?', firstPart):
    return False
  if mid == ',-':
    return True
  else:
    return False
rules = filter(lambda r : not isTrivialConstraint(r), rules)
# re-substitute tmp_epnot by $not$:
rules = map(lambda r : re.sub('[^a-zA-Z0-9_]tmp_epnot_0_', lambda match : match.group(0)[0] + ' $not$ not ', r), rules)
rules = map(lambda r : re.sub('[^a-zA-Z0-9_]tmp_epnot_1_', lambda match : match.group(0)[0] + ' $not$ ', r), rules)
# substitute disjunction symbol ';' by '|':
rules = map(lambda r : re.sub(';', '|', r), rules)

for l in rules:
  print(l, file=args.o)

if args.i:
  args.i.close()
if args.o:
  args.o.close()
