%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% arguments %%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% input: input_length(L).
% input: num_packages(NPL).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% problem description %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

step(0).
step(S+1)   :- step(S), max_length(L), S < L.
stepless(S) :- step(S), not max_length(S).

%%%%% occurs  %%%%%%%
dunk(P,S) :- package(P), stepless(S), not K$ not dunk(P,S).
bot :- dunk(P,S), not executable_dunk(P,S).
:- stepless(S), dunk(A,S), dunk(B,S), A != B.

%%%%% goal  %%%%%%%
goal :- -unsafe(LEN), not bot, max_length(LEN).

:- not K$ goal.

%%%%% defaults and inertia  %%%%%%%
-armed(P,0)   :- not  armed(P,0), package(P).
-dunked(P,0)  :- not  dunked(P,0), package(P).

 armed(P,S+1) :- stepless(S),  armed(P,S), not  -armed(P,S+1).
-armed(P,S+1) :- stepless(S), -armed(P,S), not   armed(P,S+1).

 dunked(P,S+1) :- stepless(S),  dunked(P,S), not  -dunked(P,S+1).
-dunked(P,S+1) :- stepless(S), -dunked(P,S), not   dunked(P,S+1).
