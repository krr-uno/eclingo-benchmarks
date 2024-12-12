fairGPA(mary).
highGPA(mary).
minority(mary).
fairGPA(mike).
highGPA(mike).
highGPA(nancy).
fairGPA(paul).
minority(paul).
student(mike).
student(mary).
student(nancy).
student(paul).
eligible(X) :- highGPA(X), student(X).
eligible(X) :- minority(X), fairGPA(X), student(X).
-eligible(X) :- -fairGPA(X), -highGPA(X), student(X).
interview(X) :- not K$ eligible(X), not K$ -eligible(X), student(X).
