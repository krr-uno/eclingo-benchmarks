#!/usr/bin/env python3

from lark import Lark
from lark import Transformer

import argparse
import sys

argumentParser = argparse.ArgumentParser(description='transforms epistemic logic programs into ASP(Q).')

argumentParser.add_argument('-s', '--semantics', choices=['g94','g11','k14'], default='g94', help='semantics. Currently g94 (Gelfond 1994/Baral&Gelfond 1994), g11 (Gelfond 2011), k14 (Kahl 2014).')

args = argumentParser.parse_args()

elpGrammar = r'''

    program: rule*

    rule: ":-" "."           -> emptyrule
        | ":-" body "."      -> constraint
        | head "."           -> fact
        | head ":-" "."      -> fact
        | head ":-" body "." -> regularrule
    
    head: classical_literal ("|" classical_literal)*

    body: bodyelement ("," bodyelement)*

    bodyelement: objectiveliteral              -> obj_lit
              | K objectiveliteral             -> subj_k_lit
              | M objectiveliteral             -> subj_m_lit
              | DEFNEG K objectiveliteral      -> subj_not_k_lit
              | DEFNEG M objectiveliteral      -> subj_not_m_lit
              | arithterm BINOP arithterm      -> builtin_atom
    
    objectiveliteral: classical_literal        -> poslit
                    | DEFNEG classical_literal -> neglit
    
    classical_literal: atom     -> pos_clas_lit
                    | "-" atom -> neg_clas_lit
    
    atom : ID ("(" terms? ")")?
    
    terms: term ("," term)*

    term: ID        -> term_id
        | arithterm -> term_arithterm
        | ID "(" terms? ")" -> term_func
        | STRING    -> term_id
        
    arithterm: NUMBER                      -> arithterm
            | "(" arithterm ")"           -> arithterm_paren
            | "-" arithterm               -> arithterm_minus
            | arithterm ARITHOP arithterm -> arithterm_arithop
            | arithterm "-" arithterm     -> arithterm_minusop
        
    K: "K$"

    M: "M$"
    
    DEFNEG: "not"
        
    ID: /[a-z][A-Za-z0-9_]*/

    STRING: /"[^"]*"/

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


class Atom:
  def __init__(self, predName, arguments): # arguments is a collection of strings
    self.predName = predName
    self.arguments = arguments
  def __repr__(self):
    if len(self.arguments) == 0:
      return self.predName
    else:
      return self.predName + '(' + ','.join(self.arguments) + ')'
  def prefix(self, p):
    return p +  repr(self)

class ClassicalLiteral:
  def __init__(self, atom, positive):
    self.atom = atom
    self.positive = positive
  def __repr__(self):
    if self.positive:
      return repr(self.atom)
    else:
      return '-' + repr(self.atom)
  def prefix(self, p):
    if self.positive:
      return self.atom.prefix(p)
    else:
      return '-' + self.atom.prefix(p)

class ObjectiveLiteral:
  def __init__(self, clasLit, positive):
    self.clasLit = clasLit
    self.positive = positive
  def __repr__(self):
    if self.positive:
      return repr(self.clasLit)
    else:
      return 'not ' + repr(self.clasLit)
  def prefix(self, p):
    if self.positive:
      return self.clasLit.prefix(p)
    else:
      return 'not ' + self.clasLit.prefix(p)
  def collapse(self):
    if self.positive:
      return repr(self.clasLit)
    else:
      return 'not' + repr(self.clasLit)
  def complementary(self):
    return ObjectiveLiteral(self.clasLit,not self.positive)

class ObjectiveBodyElement:
  def __init__(self, objLit):
    self.objLit = objLit
  def __repr__(self):
    return repr(self.objLit)
  def prefix(self, p):
    return self.objLit.prefix(p)
  def g11(self, p):
    return self.prefix(p)

class SubjectiveBodyElement:
  def __init__(self, negative, km, objLit):
    self.negative = negative
    self.km = km
    self.objLit = objLit
    subjlitdict[self.collapseandprefix('')]=self
  def __repr__(self):
    if self.negative:
      s = 'not '
    else:
      s = ''
    if self.km:
      return s + 'K ' + repr(self.objLit)
    else:
      return s + 'M ' + repr(self.objLit)
  def prefix(self,p):
    if self.negative:
      s = 'not '
    else:
      s = ''
    return s + self.collapseandprefix('')
  def g11(self,p):
    if (self.negative and self.km):
      return 'not ' + self.collapseandprefix('')
    elif (not self.negative and not self.km):
      return self.collapseandprefix('')
    else:
      return self.collapseandprefix('') + ', ' + self.objLit.prefix(p)
  def k14(self,p):
    return self.collapseandprefix('') + ', ' + self.objLit.prefix(p)
  def collapseandprefix(self,p):
    if self.km:
      return p + 'k' + self.objLit.collapse().replace('(', '_').replace(')', '_').replace(',', '_')
    else:
      return p + 'm' + self.objLit.collapse().replace('(', '_').replace(')', '_').replace(',', '_')

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
  def prefix(self, p):
    return ' | '.join(map(lambda e : e.prefix(p), self.head)) + ' :- ' + ', '.join(map(lambda e : e if isinstance(e, str) else e.prefix(p), self.body)) + '.'
  def transform(self,semantics,p):
    if semantics == 'g94':
      return self.prefix(p)
    elif semantics == 'g11':
      return self.g11(p)
    elif semantics == 'k14':
      return self.k14(p)
    else:
      return self.prefix(p)
  def g94(self,p):
    return self.prefix(p)
  def g11(self,p):
    return ' | '.join(map(lambda e : e.prefix(p), self.head)) + ' :- ' + ', '.join(map(lambda e : e if isinstance(e, str) else e.g11(p), self.body)) + '.'
  def k14(self,p):
    return ' | '.join(map(lambda e : e.prefix(p), self.head)) + ' :- ' + ', '.join(map(lambda e : e if isinstance(e, str) else e.k14(p), self.body)) + '.'
  
class ElpsSyntaxTreeTransformer(Transformer):
  def term_id(self, children): #string
    return children[0].value
  def term_arithterm(self, children): #string
    return children[0]
  def term_func(self, children): #string
    return children[0].value + '(' + ','.join(children[1]) + ')'
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
  def terms(self, children): # iterable of strings
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
  def obj_lit(self, children):
    return ObjectiveBodyElement(children[0])
  def subj_k_lit(self, children):
    return SubjectiveBodyElement(False, True, children[1])
  def subj_m_lit(self, children):
    return SubjectiveBodyElement(False, False, children[1])
  def subj_not_k_lit(self, children):
    return SubjectiveBodyElement(True, True, children[2])
  def subj_not_m_lit(self, children):
    return SubjectiveBodyElement(True, False, children[2])
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
  def program(self, children): # iterable of rules
    return children

subjlitdict = dict()

parser = Lark(elpGrammar, start='program', parser='lalr', transformer=ElpsSyntaxTreeTransformer())

rules = parser.parse(sys.stdin.read())

#prefixgeneral = "internalelp2qasp"
prefixgeneral = ""
prefixexists = prefixgeneral + "exists"
prefixforall = prefixgeneral + "forall"

def printelp(semantics):
  print("%@exists")
  # choices for subjlits
  for stringrep,s in subjlitdict.items():
    print('{' + s.collapseandprefix(prefixgeneral) + '}.')
  for stringrep,s in subjlitdict.items():
    print("%@exists")
    for l in rules:
      print(l.transform(semantics,prefixexists + s.collapseandprefix(prefixgeneral)))
  print("%@forall")
  for l in rules:
    print(l.transform(semantics,prefixforall))
  print ("%@constraint")
  for stringrep,s in subjlitdict.items():
    if s.km:
      print(':- ' +  s.collapseandprefix(prefixgeneral) + ', ' + s.objLit.complementary().prefix(prefixforall) + '.')
      print(':- not ' +  s.collapseandprefix(prefixgeneral) + ', ' + s.objLit.prefix(prefixexists + s.collapseandprefix(prefixgeneral)) + '.')
    else:
      print(':- ' +  s.collapseandprefix(prefixgeneral) + ', ' + s.objLit.complementary().prefix(prefixexists + s.collapseandprefix(prefixgeneral)) + '.')
      print(':- not ' +  s.collapseandprefix(prefixgeneral) + ', ' + s.objLit.prefix(prefixforall) + '.')

printelp(args.semantics)
      
#for l in rules:
#  print(l)

#for l in rules:
#  print(l.prefix("internalelp2qasp"))
