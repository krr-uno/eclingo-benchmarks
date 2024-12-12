%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% arguments %%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% input: input_length(L).
num_packages(L/2) :- input_length(L).
max_length(L-1)   :- input_length(L).

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

executable_dunk(P, T) :- package(P), -clogged(T), step(T), not dunked(P, T).
executable_flush(T) :- step(T).

%%%%%  direct effects   %%%%%%%
-armed(P,  T+1) :- dunk(P, T), step(T).
 dunked(P, T+1) :- dunk(P, T), step(T).
 clogged(T+1)   :- dunk(P, T), step(T).

-clogged(T+1)   :- flush(T), step(T).

%%%%%  indirect effects   %%%%%%%
 unsafe(T) :- armed(P, T), step(T).
-unsafe(T) :- not unsafe(T), step(T).
