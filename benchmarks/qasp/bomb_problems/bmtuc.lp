%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% arguments %%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% input: input_length(L).
% input: input_toilet(T).
num_packages(L/2) :- input_length(L).
max_length(L-1)   :- input_length(L).

toilet(1).
toilet(N+1) :- toilet(N), input_toilets(T), N < T.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% initial states %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

package(1).
package(N+1) :- package(N), num_packages(NP), N < NP.

armed(P,0) | -armed(P,0) :- package(P).
:- not some_armed.
some_armed :- armed(P,0).
:- armed(P1,0), armed(P2,0), P1 != P2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% problem description %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%  executable  %%%%%%%
executable_dunk(P, L, S) :- package(P), toilet(L), step(S), not clogged(L, S).
executable_flush(L, S) :- toilet(L), step(S).

%%%%%  direct effects   %%%%%%%
-armed(P, T+1) :- dunk(P, L, T), step(T).
dunked(P, T+1) :- dunk(P, L, T), step(T).
clogged(L, T+1) :- dunk(P, L, T), step(T).

-clogged(L, T+1) :- flush(L, T), step(T).

%%%%%  indirect effects   %%%%%%%
unsafe(T) :- armed(P, T), step(T).
-unsafe(T) :- not unsafe(T), step(T).

