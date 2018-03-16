from owlready2 import *

onto = get_ontology("http://stanford.edu/~willadu/files/organ_ontology_v2.owl")
onto.load()

class Patient(onto.Person):
  namespace = onto

pt1 = Patient("Bob")
pt2 = Patient("Sally")
pt3 = Patient("John")

class Donor(Thing):
  namespace = onto
 
with onto:
  class waiting_time(DataProperty):
    range = [int] # days
    
  class immune_compatibility(DataProperty):
    range = [str] # Type 'B', 'C'
    
  class prior_donor(DataProperty):
    range = [bool]
    
  class distance(DataProperty):
    range = [int]
    
  class survival_benefit(DataProperty):
    range = [int] # 0-10, correlate later with age
    
  class pediatric_status(DataProperty):
    range = [bool]

# Bob
pt1.waiting_time = [10]
pt1.prior_donor = [True]
pt1.immune_compatibility = ["A"]
pt1.distance = [0]
pt1.survival_benefit = [10] # won nobel prize already
pt1.pediatric_status = [True]
print(pt1)

# Sally
pt2.waiting_time = [5]
pt2.immune_compatibility = ["A"]
pt2.prior_donor = [False]
pt2.distance = [1000000]
pt2.survival_benefit = [1]
pt2.pediatric_status = [False]
print(pt2)


onto.save(file = "crap.owl", format = "rdfxml")