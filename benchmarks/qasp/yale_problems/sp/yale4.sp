sorts
#s1 = 0..4.
#s2 = {pull_trigger, load}.
#s3 = {alive, loaded, is_impossible}.

predicates

holds(#s3, #s1).
occurs(#s2, #s1).
goal(#s1).
success().

rules

-holds(alive, S+1) :- occurs(pull_trigger, S), holds(loaded, S), not holds(is_impossible, S+1).
-holds(loaded, S+1) :- occurs(pull_trigger, S), not holds(is_impossible, S+1).
holds(loaded, S+1) :- occurs(load, S), not holds(is_impossible, S+1).
holds(is_impossible, S+1) :- occurs(load, S), holds(loaded, S).

holds(F, S+1) :- holds(F, S), not -holds(F, S+1).
-holds(F, S+1) :- -holds(F, S), not holds(F, S+1).
holds(F, 0) | -holds(F, 0).

holds(alive, 0).
-holds(is_impossible, 0).

goal(S) :- -holds(alive, S), -holds(is_impossible, S).

occurs(A, S) :- M$ occurs(A, S), S<4.
-occurs(A2, S) :- occurs(A1, S), A1 != A2.
success :- goal(4).
:- success, not M$ k_success.
k_success :- K$ success, success.
:- not M$ success.
