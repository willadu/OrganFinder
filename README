# OrganFinder

The scarcity of organs in the United States and the time urgency of the organ matching process given a recently available organ motivate the problem we tackle in this paper. We are further motivated by the fact that the United Network for Organ Sharing (UNOS) does not make their organ matching process transparent, choosing to cite the Organ Procurement and Transplantation Network (OPTN)\cite{optn} documentation instead of providing a fleshed out explanation of their matching model. As such, we endeavor to build an ontology-based model that specifies the players active in our scenario and their data properties -- donors and patients -- and produces a ranking of patients when a donor organ is inputted into our system. The ontology interfaces with the Owlready2 Python API, where the majority of our matching algorithm resides. Given either a kidney or liver, we score, classify, and rank the organs based on the OPTN standard and display the result on a user interface that plots the donor and the patients on a map of the US. For evaluation purposes, we randomly generate a set of 10,000 patients on the continental US as well as a smaller handful of donor organs to allocate. We have additionally consulted a physician, the BMI 210 course TA Husham Sharifi, who was given a sample list of donors and their associated patient matches and was asked to evaluate the plausibility of our ranking without specific knowledge of the OPTN standard. We have received a positive evaluation and hope that our investigation into the process of organ allocation increases awareness of the importance of UNOS’ work and methodology, which could benefit tremendously with increased transparency and a higher amount of participation from the scientific community.

## Ontology
Our ontology is available in:
```
currweb.owl
```

## Problem Solving Methods

Our PSMs modules and ontology + randomized patient generator module are available in:
```
organized.py
```

## Randomized Name Generator

Our randomized patient generator is available in:
```
namegen.py
```
It requires the name files in this repository to function.

## Running the Flask App
```
export FLASK_DEBUG=1
export FLASK_APP=hello.py
lask run
```


