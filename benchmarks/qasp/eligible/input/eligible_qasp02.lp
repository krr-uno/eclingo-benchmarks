highGPA(mary).
fairGPA(mary).
minority(mary).
highGPA(mike).
fairGPA(mike).
student(mike).
student(mary).
eligible(X) :- highGPA(X), student(X).
eligible(X) :- minority(X), fairGPA(X), student(X).
-eligible(X) :- -fairGPA(X), -highGPA(X), student(X).
interview(X) :- not K$ eligible(X), not K$ -eligible(X), student(X).
