#!/usr/bin/env python3

from lark import Lark
from lark import Transformer
import collections
import itertools
import sys
import argparse
import subprocess

argumentParser = argparse.ArgumentParser(description='Reduces a ground EASP-not program into a non-ground ASP program (in ASP-Core-2 syntax) in a structure-preserving way.')
argumentParser.add_argument('-i', metavar='FILE', type=argparse.FileType('r'), default=sys.stdin, help='ground EASP-not input file (default standard input)')
argumentParser.add_argument('-o', metavar='FILE', type=argparse.FileType('w'), default=sys.stdout, help='non-ground ASP output file (default standard output)')
argumentParser.add_argument('-p', '--produce-show', choices=['0', 'phi', 'as', 'wit'], default='0', help='output Potassco-style #show meta-statements. 0: none (default); phi: show epistemic guess; as: also show answer/believe set; wit: also show witnesses for literals in the guess')
argumentParser.add_argument('-t', '--htd_main', metavar='PATH', default='htd_main', help='path to the htd_main executable. (default: htd_main)')
argumentParser.add_argument('-s', '--seed', type=int, metavar='SEED', default=0, help='seed for the random number generator used for hypertree decomposition')
argumentParser.add_argument('--no-arith', action='store_true', help='do not produce arithmetic terms, but instead use additional extensional predicates')
args = argumentParser.parse_args()

# some class definitions for representing EASP syntax: (atoms are just represented by strings)
class ObjectiveLiteral:
  def __init__(self, atom, positive):
    self.atom = atom
    self.positive = positive
  def __repr__(self):
    if self.positive:
      return self.atom
    else:
      return 'not ' + self.atom
class BodyElement:
  def __init__(self, positive):
    self.positive = positive
class ObjectiveBodyElement(BodyElement):
  def __init__(self, objLit):
    super(ObjectiveBodyElement, self).__init__(objLit.positive)
    self.literal = objLit
  def __repr__(self):
    return repr(self.literal)
class SubjectiveBodyElement(BodyElement):
  def __init__(self, positive, objLit):
    super(SubjectiveBodyElement, self).__init__(positive)
    self.innerLiteral = objLit
  def __repr__(self):
    if self.positive:
      return '$not$ ' + repr(self.innerLiteral)
    else:
      return 'not $not$ ' + repr(self.innerLiteral)
class Rule:
  def __init__(self, head=None, body=None):
    if head is None:
      head = []
    if body is None:
      body = []
    self.head = head
    self.body = body
  def __repr__(self):
    return ' | '.join(map(lambda e : repr(e), self.head)) + ' :- ' + ', '.join(map(lambda e : repr(e), self.body)) + '.'

# transformer that transforms the parsed syntax tree into our representation, that is, a list of Rule objects:
class EaspSyntaxTreeTransformer(Transformer):
  def term(self, s):
    return s[0].value
  def terms(self, terms):
    return ', '.join(terms)
  def atom(self, children):
    ret = children.pop(0).value
    for c in children:
      ret += '(' + c + ')'
    return ret
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
  def body(self, children):
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
  def program(self, children):
    return list(children)

# ground EASP grammar parser:
easpParser = Lark(r'''
  
  program: rule*
    
  rule: ":-" "."           -> emptyrule
      | ":-" body "."      -> constraint
      | head "."           -> fact
      | head ":-" "."      -> fact
      | head ":-" body "." -> regularrule
  
  head: atom ("|" atom)*
  
  body: bodyelement ("," bodyelement)*
    
  bodyelement: objectiveliteral              -> bo
             | EPNEG objectiveliteral        -> bs_pos
             | DEFNEG EPNEG objectiveliteral -> bs_neg
  
  objectiveliteral: atom        -> poslit
                  | DEFNEG atom -> neglit
  
  atom : ID ("(" terms? ")")?
  
  terms: term ("," term)*

  term: ID
      | NUMBER
      
  EPNEG: "$not$"
  
  DEFNEG: "not"
       
  ID: /[a-z][A-Za-z0-9_]*/
  
  COMMENT: "%" ( /[^*\n]/ /[^\n]/* )? NEWLINE

  MULTILINE_COMMENT: "%*" ( /[^*]/ | /\*[^%]/ )* "*%"

  %import common.INT -> NUMBER
  %import common.WS
  %import common.NEWLINE
  %ignore COMMENT
  %ignore MULTILINE_COMMENT
  %ignore WS
  %ignore NEWLINE
  
  ''', start='program', parser='lalr', transformer=EaspSyntaxTreeTransformer())

# parser for htd's output format "td":
tdParser = Lark(r'''
  program: s_line bag_lines edge_lines
  s_line: "s" "td" INT INT INT NEWLINE
  bag_lines: bag_line*
  bag_line: "b" INT+ NEWLINE
  edge_lines: edge_line*
  edge_line: INT INT NEWLINE
  COMMENT_LINE: "c" /[^\n]/* NEWLINE
  
  %import common.INT
  %import common.WS
  %import common.WS_INLINE
  %import common.NEWLINE
  %ignore WS_INLINE
  %ignore COMMENT_LINE
  ''', start='program', parser='lalr')

# transformer that transforms the parsed syntax tree into a RootedBagTree, subtracting 1 from each number contained in a bag
class TdSyntaxTreeTransformer(Transformer):
  def __init__(self):
    self.td = BagGraph()
  def edge_line(self, children):
    self.td.addEdge(int(children[0].value), int(children[1].value))
  def bag_line(self, children):
    self.td.setBag(int(children[0].value), frozenset(map(lambda c : int(c)-1, children[1:-1])))
  def program(self, children):
    return RootedBagTree.anyRoot(self.td)
  
class BagGraph(dict):
  # this dict maps bag ids to bags. A bag is a tuple (A, N), where A is a frozenset of all the things that are in the bag, and N is a set of the ids of the bag's neighbours. Thus, this represents a graph where the nodes are bags containing things.
  def __init__(self):
    super(BagGraph, self).__init__()
  def setBag(self, bagNumber, contents): #contents is a frozenset
    self[bagNumber] = (contents, set())
  def addEdge(self, bagId1, bagId2): #adds an edge between the two bags
    self[bagId2][1].add(bagId1)
    self[bagId1][1].add(bagId2)

class RootedBagTree(dict):
  # this dict maps bag ids to bags. A bag is a tuple (A, P, C), where A is a frozenset of all the things that are in the bag, P is the id of the parent's bag (-1 if this bag is the root), and C is a frozenset of the ids of the bag's children. Objects of this class thus represent a rooted tree where the nodes are bags containing things.
  def __init__(self, td, rootBag): #td is a BagGraph which must be a tree (i.e., cycle-free and connected), rootBag is the id of the bag to use as the root of the tree
    super(RootedBagTree, self).__init__()
    self._root=rootBag
    self[rootBag] = (td[rootBag][0], -1, frozenset(td[rootBag][1]))
    self._extendBags(rootBag, td)
  @classmethod
  def anyRoot(cls, td): #like the constructor, but chooses a root node. td must be a tree.
    for e in td.keys():
      anyObject = e
      break
    return cls(td, anyObject)
  def _extendBags(self, currentBag, td): #adds subtree under currentBag from td to this.
    if (self[currentBag][1] != -1 and len(td[currentBag][1]) == 1) or (self[currentBag][1] == -1 and len(td[currentBag][1]) == 0):
      return #we are a leave bag. Nothing left to do.
    else:
      for n in td[currentBag][1]:
        if n != self[currentBag][1]: #not parent
          self[n] = (td[n][0], currentBag, frozenset(nn for nn in td[n][1] if nn != currentBag))
          self._extendBags(n, td)
  def contents(self, bagNumber): #returns a frozenset of the contents of the given bag
    return self[bagNumber][0]
  def parent(self, bagNumber): #returns the parent of the given bag, or -1 if it is the root
    return self[bagNumber][1]
  def children(self, bagNumber): #returns the children of the given bag as a frozenset
    return self[bagNumber][2]
  def introduced(self, bagNumber):
    "returns those contents of the bag which do not occur in the parent"
    if self.isRoot(bagNumber):
      return self.contents(bagNumber)
    else:
      return self.contents(bagNumber) - self.contents(self.parent(bagNumber))
  def isLeaf(self, bagNumber):
    return len(self[bagNumber][2]) == 0
  def root(self):
    "returns the root bag"
    return self._root
  def isRoot(self, bagNumber):
    return bagNumber == self._root
  def _perform(self, function, currentBag):
    "pre-order traverses the subtree under the given bag (including the bag itself) and calls the given function once for each bag. The function must take a single argument, which is the bag id."
    function(currentBag)
    for c in self[currentBag][2]:
      self._perform(function, c)
  def perform(self, function):
    "pre-order traverses the tree and calls the given function once for each bag. The function must take a single argument, which is the bag."
    self._perform(function, self._root)

def quoteAtom(a): # puts quotes around an atom from the EASP program s.t. it becomes a constant in ASP-Core-2 syntax
  return '"' + a + '"'

def bClassical(rule, context, atomsOrder, noArith): # context is an iterable of strings, atomsOrder an analyzation of an EASP program, noArith a flag to not produce arithmetic terms. Returns a deque of strings (atoms) that is B_{classical}^rule(context) as defined in paper. Time: O(rulelength * size of context)
  returnDeque = collections.deque()
  returnDeque.extend(['assign(' + ', '.join(context + [quoteAtom(a), '0']) + ')' for a in rule.head])
  for e in rule.body:
    if isinstance(e, ObjectiveBodyElement):
      a = e.literal.atom
      if e.positive:
        returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), '1']) + ')')
      else:
        returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), '0']) + ')')
    else: #e is SubjectiveBodyLiteral
      a = e.innerLiteral.atom
      if e.positive:
        if e.innerLiteral.positive:
          returnDeque.append('phi(' + quoteAtom(a) + ', 1, N_' + str(atomsOrder[a]) + ')')
          returnDeque.append('or(N_' + str(atomsOrder[a]) + ', M_' + str(atomsOrder[a]) + ')')
          if noArith:
            returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), 'NegM_'+str(atomsOrder[a])]) + ')')
            returnDeque.append('inv(M_'+str(atomsOrder[a])+', NegM_'+str(atomsOrder[a])+')')
          else:
            returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), '1-M_'+str(atomsOrder[a])]) + ')')
        else:
          returnDeque.append('phi(' + quoteAtom(a) + ', 0, N_n' + str(atomsOrder[a]) + ')')
          returnDeque.append('or(N_n' + str(atomsOrder[a]) + ', M_n' + str(atomsOrder[a]) + ')')
          returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), 'M_n'+str(atomsOrder[a])]) + ')')
      else: #not e.positive
        if e.innerLiteral.positive:
          returnDeque.append('phi(' + quoteAtom(a) + ', 1, 0)')
          returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), '1']) + ')')
        else: 
          returnDeque.append('phi(' + quoteAtom(a) + ', 0, 0)')
          returnDeque.append('assign(' + ', '.join(context + [quoteAtom(a), '0']) + ')')
  return returnDeque

def bSubset(context, atoms, atomsOrder): #context is an iterable of strings, atoms and atomsOrder an analyzation of an EASP program. Returns a list of strings (atoms) that is B_{subset}^easpProgram(context) as defined in paper. Time: O(#atoms * size of context)
  assigns = ['assign(' + ', '.join(context + [quoteAtom(a), 'X'+str(atomsOrder[a])]) + ')' for a in atoms]
  leqs = ['leq(Y'+str(atomsOrder[a])+', X'+str(atomsOrder[a]) +')' for a in atoms]
  return assigns+leqs

def bNeq(decomp, noArith): # decomp is an ELP's tree decomposition, noArith a flag to not produce arithmetic terms. Returns a deque of strings (atoms) that is B_{neq}^easpProgram as defined in paper. Time: O(size of decomp)
  b_neq = collections.deque()
  def handleBag(bag):
    nStr = 'N' + str(bag) #variable stating that the atom variables introduced in this bag's subtree are neq
    cStr = nStr + '_c' #variable stating that the children account for neq-uality
    iStr = nStr + '_i' #variable stating that the atoms introduced in this bag account for neq-uality
    # first, disjoin childrens' N:
    childList = list(decomp.children(bag))
    b_neq.append(nStr + 'c0 = 0')
    for i in range(len(childList)):
      c = childList[i]
      ccStr = nStr + 'c' + str(i)
      nextCStr = nStr + 'c' + str(i+1)
      b_neq.append('or(' + ccStr + ', N' + str(c) + ', '  + nextCStr + ')')
    b_neq.append(nStr + 'c' + str(len(childList)) + ' = ' + cStr)
    del childList
    #now, disjoin new bag contents:
    introduceList = list(decomp.introduced(bag))
    b_neq.append(nStr + 'i0 = 0')
    for i in range(len(introduceList)):
      a = introduceList[i]
      aStr = nStr + 'i' + str(i)
      nextAStr = nStr + 'i' + str(i+1)
      xVar = 'X'+str(a)
      yVar = 'Y'+str(a)
      if noArith:
        neqVar = 'Neq'+str(a)
        b_neq.append('or(' + aStr + ', ' + neqVar + ', '  + nextAStr + ')')
        b_neq.append('or(' + neqVar + ', ' + yVar + ', '  + xVar + ')')
      else:
        b_neq.append('or(' + aStr + ', ' + xVar+'-'+yVar + ', '  + nextAStr + ')')
    b_neq.append(nStr + 'i' + str(len(introduceList)) + ' = ' + iStr)
    del introduceList
    # put them together:
    b_neq.append('or(' + cStr + ',' + iStr + ', ' + nStr + ')')
    if decomp.isRoot(bag):
      b_neq.append(nStr + ' = 1')
  decomp.perform(handleBag)
  return b_neq

def bModel(easpProgram, atoms, atomsOrder, noArith): #easpProgram is a set of easp rules, noArith a flag to not produce arithmetic terms. the other arguments are an analyzation of easpProgram. Returns a deque of strings (atoms) that is B_{model}^easpProgram as defined in paper. Time: O(size of easpProgram)
  returnDeque = collections.deque()
  ruleNumber=0
  for r in easpProgram:
    rIndex=0
    returnDeque.append('R_0_' + str(ruleNumber) + '=0')
    for a in r.head:
      returnDeque.append('or(R_'+str(rIndex)+'_'+str(ruleNumber)+', Y'+str(atomsOrder[a])+', R_'+str(rIndex+1)+'_'+str(ruleNumber)+')')
      rIndex=rIndex+1
    for e in r.body:
      if isinstance(e, ObjectiveBodyElement):
        a = e.literal.atom
        if e.positive:
          yVar = 'Y'+str(atomsOrder[a])
          if noArith:
            negyVar = 'Neg'+yVar
            returnDeque.append('or(R_'+str(rIndex)+'_'+str(ruleNumber)+', '+negyVar+', R_'+str(rIndex+1)+'_'+str(ruleNumber)+')')
            returnDeque.append('inv('+yVar+', '+negyVar+')')
          else:
            returnDeque.append('or(R_'+str(rIndex)+'_'+str(ruleNumber)+', 1-'+yVar+', R_'+str(rIndex+1)+'_'+str(ruleNumber)+')')
        else:
          returnDeque.append('or(R_'+str(rIndex)+'_'+str(ruleNumber)+', X'+str(atomsOrder[a])+', R_'+str(rIndex+1)+'_'+str(ruleNumber)+')')
      else: #e is SubjectiveBodyLiteral
        a = e.innerLiteral.atom
        if e.positive:
          if e.innerLiteral.positive:
            returnDeque.append('phi(' + quoteAtom(a) + ', 1, N_' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ')')
            xVar = 'X'+str(atomsOrder[a])
            mVar = 'M_' + str(atomsOrder[a]) + 'p_' + str(ruleNumber)
            if noArith:
              negxVar = 'Neg'+xVar
              negmVar = 'Neg'+mVar
              returnDeque.append('or(N_' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ', '+negxVar + ', ' + mVar + ')')
              returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', '+negmVar + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
              returnDeque.append('inv(' + xVar + ', ' + negxVar + ')')
              returnDeque.append('inv(' + mVar + ', ' + negmVar + ')')
            else:
              returnDeque.append('or(N_' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ', 1-'+xVar + ', ' + mVar + ')')
              returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', 1-'+mVar + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
          else:
            mVar = 'M_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber)
            if noArith:
              negmVar = 'Neg'+mVar
              returnDeque.append('phi(' + quoteAtom(a) + ', 0, N_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ')')
              returnDeque.append('or(N_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ', X'+str(atomsOrder[a]) + ', M_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ')')
              returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', ' + negmVar + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
              returnDeque.append('inv(' + mVar + ', ' + negmVar + ')')
            else:
              returnDeque.append('phi(' + quoteAtom(a) + ', 0, N_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ')')
              returnDeque.append('or(N_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ', X'+str(atomsOrder[a]) + ', M_n' + str(atomsOrder[a]) + 'p_' + str(ruleNumber) + ')')
              returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', 1-' + mVar + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
        else: #not e.positive
          if e.innerLiteral.positive:
            xVar = 'X'+str(atomsOrder[a])
            if noArith:
              negxVar = 'Neg'+xVar
              returnDeque.append('phi(' + quoteAtom(a) + ', 1, N_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ')')
              returnDeque.append('or(N_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ', '+negxVar + ', M_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ')')
              returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', M_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
              returnDeque.append('inv(' + xVar + ', ' + negxVar + ')')
            else:
              returnDeque.append('phi(' + quoteAtom(a) + ', 1, N_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ')')
              returnDeque.append('or(N_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ', 1-'+xVar + ', M_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ')')
              returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', M_' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
          else: 
            returnDeque.append('phi(' + quoteAtom(a) + ', 0, N_n' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ')')
            returnDeque.append('or(N_n' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ', X'+str(atomsOrder[a]) + ', M_n' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ')')
            returnDeque.append('or(R_' + str(rIndex) + '_' + str(ruleNumber) + ', M_n' + str(atomsOrder[a]) + 'n_' + str(ruleNumber) + ', R_' + str(rIndex+1) + '_' + str(ruleNumber) + ')')
      rIndex=rIndex+1
    returnDeque.append('R_'+str(rIndex)+'_' + str(ruleNumber) + '=1')
    ruleNumber=ruleNumber+1
  return returnDeque

def bReduct(context, atoms, atomsOrder, b_neq, b_model): #context is an iterable of strings, atoms and atomsOrder an analyzation of an EASP program, b_neq and b_model already iterables of B_{neq} and B_{model}, respectively. Returns an iterator of strings (atoms) that is B_{reduct}^easpProgram(context) as defined in paper. Time: O(#atoms * size of context)
  return itertools.chain(bSubset(context, atoms, atomsOrder), b_neq, b_model)

def analyzeEasp(easpProgram): # returns a tuple (epistemicNegations, atoms, atomsOrder) of a tuple of ObjectiveLiterals which occur in an epistemic negation, a tuple of all atoms occuring in the program, and a dictionary assigning each atom its position in the "atoms" tuple (for constant-time lookup). the order of the elements in "epistemicNegations" and "atoms" is the same as in the given program. Time: O(size of easpProgram)
  # first, find all epistemic negations and all atoms occurring in the program:
  epistemicNegations = set()
  epistemicNegationsList = collections.deque()
  atoms = set()
  atomsList = collections.deque()
  for r in easpProgram:
    for a in r.head:
      if a not in atoms:
        atoms.add(a)
        atomsList.append(a)
    for be in r.body:
      if isinstance(be, SubjectiveBodyElement):
        if be.innerLiteral not in epistemicNegations:
          epistemicNegations.add(be.innerLiteral)
          epistemicNegationsList.append(be.innerLiteral)
        if be.innerLiteral.atom not in atoms:
          atoms.add(be.innerLiteral.atom)
          atomsList.append(be.innerLiteral.atom)
      else:
        if be.literal.atom not in atoms:
          atoms.add(be.literal.atom)
          atomsList.append(be.literal.atom)
  del epistemicNegations, atoms
  epistemicNegationsList = tuple(epistemicNegationsList) # consists of objects of type ObjectiveLiteral
  atomsList = tuple(atomsList) # consists of strings
  atomsOrder = {}
  n = 0
  for a in atomsList:
      atomsOrder[a] = n
      n=n+1
  return epistemicNegationsList, atomsList, atomsOrder

def atoms(r): #returns an iterable of all atoms occuring in the rule r
  return itertools.chain(r.head, [e.literal.atom for e in r.body if isinstance(e, ObjectiveBodyElement)], [e.innerLiteral.atom for e in r.body if isinstance(e, SubjectiveBodyElement)])  

def decompose(easpProgram, atomsOrder, htd_main, seed=0):
  "performs a tree decomposition on the hypergraph of the given program and returns it as a RootedBagTree object. htd_main is the path to the executable."
  graphDescription = '\n'.join(itertools.chain(['p tw ' + str(len(atomsOrder)) + ' ' + str(len(easpProgram))], itertools.chain(' '.join(map(lambda a : str(atomsOrder[a]+1), atoms(r))) for r in easpProgram)))
  # atoms/vertices begin with 1. graphDescription contains a hyperedge for each rule
  output = subprocess.check_output([htd_main, '--input', 'hgr', '--output', 'td', '-s', str(seed)], input=graphDescription, universal_newlines=True)
  return TdSyntaxTreeTransformer().transform(tdParser.parse(output))
  
def reduceToAsp(easpProgram): # returns an iterable of all ASP rules of the reduction, each rule in ASP-Core-2 syntax. Time: O(size of easpProgram)
    epistemicNegations, atoms, atomsOrder = analyzeEasp(easpProgram) #O(size of easpProgram)
    decomp = decompose(easpProgram, atomsOrder, args.htd_main, args.seed)
    b_neq = bNeq(decomp, args.no_arith) #O(size of decomp)
    del decomp
    b_model = bModel(easpProgram, atoms, atomsOrder, args.no_arith) #O(size of easpProgram)
    
    asp = collections.deque()
    #facts:
    asp.extend(['atom(' + quoteAtom(a) + ').' for a in atoms])
    asp.extend(['ep(' + quoteAtom(l.atom) + ', 1).' for l in epistemicNegations if l.positive])
    asp.extend(['ep(' + quoteAtom(l.atom) + ', 0).' for l in epistemicNegations if not l.positive])
    asp.extend(['leq(' + str(x) + ', ' + str(y) + ').' for x in range(2) for y in range(2) if x <= y])
    asp.extend(['or(' + str(x) + ', ' + str(y) + ').' for x in range(2) for y in range(2) if x + y > 0])
    asp.extend(['or(' + str(x) + ', ' + str(y) + ', ' + str(x or y) + ').' for x in range(2) for y in range(2)])
    if args.no_arith:
      asp.extend(['inv(' + str(x) + ', ' + str(1-x) + ').' for x in range(2)])

    # guess phi:
    asp.append('phi(A, N, 0) | phi(A, N, 1) :- ep(A, N).')

    # check AS-existence:
    asp.append('assign(ex, A, 0) | assign(ex, A, 1) :- atom(A).')
    for r in easpProgram:
      asp.append(':- ' + ', '.join(bClassical(r, ['ex'], atomsOrder, args.no_arith)) + '.')
    asp.append(':- ' + ', '.join(bReduct(['ex'], atoms, atomsOrder, b_neq, b_model)) + '.')
    
    # check in-guesses:
    asp.append('assign(P, N, A, 0) | assign(P, N, A, 1) :- phi(P, N, 1), atom(A).')
    if args.no_arith:
      asp.append('assign(A, N, A, NegN) :- phi(A, N, 1), atom(A), inv(N, NegN).')
    else:
      asp.append('assign(A, N, A, 1-N) :- phi(A, N, 1), atom(A).')
    for r in easpProgram:
      asp.append(':- ' + ', '.join(bClassical(r, ['P', 'N'], atomsOrder, args.no_arith)) + '.')
    asp.append(':- ' + ', '.join(bReduct(['P', 'N'], atoms, atomsOrder, b_neq, b_model)) + '.')
    
    # check out-guesses:
    asp.append('assign(A, 0) | assign(A, 1) :- atom(A).')
    asp.append('assign(A, 0) :- sat, atom(A).')
    asp.append('assign(A, 1) :- sat, atom(A).')
    asp.append(':- not sat.')
    if args.no_arith:
      asp.append('sat :- ' + ', '.join(itertools.chain(['phi(' + quoteAtom(l.atom) + ', 1, N_' + str(atomsOrder[l.atom]) + '), assign(' + quoteAtom(l.atom) + ', M_' + str(atomsOrder[l.atom]) + '), or(N_' + str(atomsOrder[l.atom]) + ', M_' + str(atomsOrder[l.atom]) + ')' for l in epistemicNegations if l.positive], ['phi(' + quoteAtom(l.atom) + ', 0, N_n' + str(atomsOrder[l.atom]) + '), assign(' + quoteAtom(l.atom) + ', M_n' + str(atomsOrder[l.atom]) + '), or(N_n' + str(atomsOrder[l.atom]) + ', NegM_n' + str(atomsOrder[l.atom]) + '), inv(M_n' + str(atomsOrder[l.atom]) + ', NegM_n' + str(atomsOrder[l.atom]) + ')' for l in epistemicNegations if not l.positive])) + '.')
    else:
      asp.append('sat :- ' + ', '.join(itertools.chain(['phi(' + quoteAtom(l.atom) + ', 1, N_' + str(atomsOrder[l.atom]) + '), assign(' + quoteAtom(l.atom) + ', M_' + str(atomsOrder[l.atom]) + '), or(N_' + str(atomsOrder[l.atom]) + ', M_' + str(atomsOrder[l.atom]) + ')' for l in epistemicNegations if l.positive], ['phi(' + quoteAtom(l.atom) + ', 0, N_n' + str(atomsOrder[l.atom]) + '), assign(' + quoteAtom(l.atom) + ', M_n' + str(atomsOrder[l.atom]) + '), or(N_n' + str(atomsOrder[l.atom]) + ', 1-M_n' + str(atomsOrder[l.atom]) + ')' for l in epistemicNegations if not l.positive])) + '.')
    for r in easpProgram:
      asp.append('sat :- ' + ', '.join(bClassical(r, [], atomsOrder, args.no_arith)) + '.')
    asp.append('sat :- ' + ', '.join(bReduct([], atoms, atomsOrder, b_neq, b_model)) + '.')
    
    return asp

easpProgram = easpParser.parse(args.i.read())
aspProgram = reduceToAsp(easpProgram)
for l in aspProgram:
  print(l, file=args.o)
if args.produce_show != '0':
  print('#show.', file=args.o)
  print('#show phi/3.', file=args.o)
  if args.produce_show != 'phi':
    print('#show assign/3.', file=args.o)
    if args.produce_show == 'wit':
      print('#show assign/4.', file=args.o)

if args.i:
  args.i.close()
if args.o:
  args.o.close()
