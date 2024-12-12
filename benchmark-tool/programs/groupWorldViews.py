#!/usr/bin/env python3

import sys
import json
import itertools
import re
import argparse

argumentParser = argparse.ArgumentParser(description='reads from stdin the output of "easp2asp.py -pas | clingo -n0 --outf=2 --project", groups the answer sets into world views and outputs the grouping. Also works if clingo is not called with -n0, but then it cannot enumerate the world views. Also works if lpopt is put in between easp2asp and clingo. Also works if -pphi is passed to easp2asp.py, but then the world views will be enumerated without their respective believe sets. If -p0 or no -p is passed to easp2asp.py, then this program just prints some beleive set of some world view. If -pwit is passed to easp2asp.py, then this program will list every beleive set several times, each with different wittness atoms.')
argumentParser.add_argument('-a', '--answersets', type=int, choices=[0, 1], default=1, help='whether or not to print each world view\'s answer/beleive sets (default 1)')
argumentParser.add_argument('-c', '--cautious', type=int, choices=[0, 1], default=1, help='whether or not to print each world views\'s cautious consequences (default 1)')
argumentParser.add_argument('-b', '--brave', type=int, choices=[0, 1], default=0, help='whether or not to print each world views\'s brave consequences (default 0)')
args = argumentParser.parse_args()

jsonData = json.load(sys.stdin)
if jsonData['Result'] != 'SATISFIABLE':
  print('NO WORLD VIEW')
  sys.exit(1)
if jsonData['Models']['More'] == 'yes':
  print('SATISFIABLE')
  # pretty-format the calculated witness:
  witness = jsonData['Call'][0]['Witnesses'][0]['Value']
  #pprint(jsonData['Call'][0]['Witnesses'][0]['Value']) -- would be easy formatting
  inGuesses = set('$not$ ' + phiAtom[5:-6] for phiAtom in witness if phiAtom.startswith('phi(') and phiAtom.endswith('1,1)'))
  inGuesses |= set('$not$ not ' + phiAtom[5:-6] for phiAtom in witness if phiAtom.startswith('phi(') and phiAtom.endswith('0,1)'))
  outGuesses = set('$not$ ' + phiAtom[5:-6] for phiAtom in witness if phiAtom.startswith('phi(') and phiAtom.endswith('1,0)'))
  outGuesses |= set('$not$ not ' + phiAtom[5:-6] for phiAtom in witness if phiAtom.startswith('phi(') and phiAtom.endswith('0,0)'))
  print('Some World View: in=' + repr(inGuesses) + ', out=' + repr(outGuesses))
  print('  Some Answer Set of this World View:')
  for atom in sorted(assignAtom[11:-4] for assignAtom in witness if assignAtom.startswith('assign(ex,') and assignAtom.endswith(',1)')):
    print('    ' + atom)
  sys.exit(0)
listOfWitnesses = jsonData['Call'][0]['Witnesses']
witnesses=map(lambda w: w['Value'], listOfWitnesses) #an iterable of lists of atoms (strings)
frozenWitnesses=frozenset(map(lambda w:frozenset(w), witnesses)) # deletes duplicates. reults in a frozenset of frozensets of atoms (strings)
del listOfWitnesses, witnesses
grouping={} #key: epistemic guess; value: set of answer sets of this ep. guess
for w in frozenWitnesses:
  guessFilter = lambda a: a.startswith('phi')
  guess = frozenset(filter(guessFilter, w))
  answerSet = frozenset(itertools.filterfalse(guessFilter, w))
  if guess not in grouping:
    grouping[guess] = set()
  grouping[guess].add(answerSet)
# TODO in order to have guess-maximal world views (Shen, Eiter 2016), remove guesses that are not maximal here. TODO this is actually clasp's job (via heuristics)

anyInterestInWorldViewContents = args.answersets | args.cautious | args.brave
#easy format: pprint(grouping)
# pretty formatting:
for guess in grouping:
  inGuesses = set('$not$ ' + phiAtom[5:-6] for phiAtom in guess if phiAtom.endswith('1,1)'))
  inGuesses |= set('$not$ not ' + phiAtom[5:-6] for phiAtom in guess if phiAtom.endswith('0,1)'))
  outGuesses = set('$not$ ' + phiAtom[5:-6] for phiAtom in guess if phiAtom.endswith('1,0)'))
  outGuesses |= set('$not$ not ' + phiAtom[5:-6] for phiAtom in guess if phiAtom.endswith('0,0)'))
  print('World View: in=' + repr(inGuesses) + ', out=' + repr(outGuesses))
  if anyInterestInWorldViewContents:
    cautiousConsequences = None
    braveConsequences = set()
    for answerSet in grouping[guess]:
      pureAnswerSet = set()
      for atom in (assignAtom[11:-4] for assignAtom in answerSet if assignAtom.startswith('assign(ex,') and assignAtom.endswith(',1)')):
        pureAnswerSet.add(atom)
      if args.answersets:
        print('  Answer Set:')
        for atom in sorted(pureAnswerSet):
          print('    ' + atom)
      if args.cautious:
        if cautiousConsequences:
          cautiousConsequences &= pureAnswerSet
        else:
          cautiousConsequences = pureAnswerSet
      if args.brave:
        braveConsequences |= pureAnswerSet
    if args.cautious:
      print('  Cautious consequences of this World View:')
      for c in sorted(cautiousConsequences):
        print('    ' + c)
    if args.brave:
      print('  Brave consequences of this World View:')
      for c in sorted(braveConsequences):
        print('    ' + c)
