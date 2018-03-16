"""
might need to:
pip install owlready2
pip install geopy

- init()
- find_matching_patients(donor)
    input: donor in the form
      donor = {
        'kidney': boolean,
        'liver': boolean,
        'blood_type': BLOOD_TYPES[rand.randint(0, len(BLOOD_TYPES)-1)],
        'hla_dr': rand.randint(0, MAX_HLA_DR),
        'latitude': rand.randint(MIN_LAT, MAX_LAT),
        'longitude': rand.randint(MIN_LONG, MAX_LONG)
      }
    output: {
      'kidney': kidney_matches,
      'liver': liver_matches
    }
    where kidney_matches is a list of tuples (onto.Patient instance, kidney points)
    and liver_matches is a list of tuples (onto.Patient instance, wait time)
"""

# !pip install owlready2
# !pip install geopy
from owlready2 import *

import random as rand
import string
import math
import geopy.distance as geodis
import namegen

NUM_PATIENTS = 10000

MAX_HLA_DR = 78
MAX_CPRA_SCORE = 100
MAX_WAIT_TIME = 365*5
MAX_AGE = 100
MIN_LAT = 30
MAX_LAT = 48
MIN_LONG = -123
MAX_LONG = -75

NUM_MATCHES = 10

NUM_KIDNEY_BUCKETS = 14
NUM_LIVER_BUCKETS = 25
EPTS_THRESHOLD = 4

def init():
  names = set()
  onto = get_ontology("http://stanford.edu/~willadu/files/organ_ontology_v2.owl")
  onto.load()
  first_dict, last_dict = namegen.buildNameDictionaries()

  class Patient(onto.Person):
    namespace = onto
    
  class Donor(onto.Person):
    namespace = onto

  for i in range(NUM_PATIENTS):
    #name = ''.join([rand.choice(string.ascii_letters + string.digits) for n in range(10)])
    name = namegen.nameGenerator(first_dict, last_dict)
    #while name in names:
    #  name = ''.join([rand.choice(string.ascii_letters + string.digits) for n in range(10)])
    names.add(name)

    Patient(name)

  with onto:
    class organ(DataProperty):
      range = [str] # 'kidney', 'liver'
    
    class blood_type(DataProperty):
      range = [str]
      
    class hla_dr(DataProperty):
      range = [int] # 0-78
      
    class cpra(DataProperty):
      range = [int] # 0-100
      
    class wait_time(DataProperty):
      range = [int] # days
      
    class age(DataProperty):
      range = [int] # years
    
    class latitude(DataProperty):
      range = [float]
         
    class longitude(DataProperty):
      range = [float]
      
    # kidney properties
    class dialysis_time(DataProperty):
      range = [int] # years
      
    class is_prior_donor(DataProperty):
      range = [int]
      
    class has_diabetes(DataProperty):
      range = [int]
      
    class has_prior_transplant(DataProperty):
      range = [int]
    
    # additional liver properties
    class sodium_value(DataProperty):
      range = [float] # mmol/L usually range(125, 137)
      
    class creatinine_value(DataProperty):
      range = [float] # mg/dL usually range(0, 4)
      
    class bilirubin_value(DataProperty):
      range = [float] # mg/dL
      
    class INR_value(DataProperty):
      range = [float] # ratio usually <= 1.1 or range(2, 3)
      
    class albumin_value(DataProperty):
      range = [float] # g/dL, for pediatric cases
      
    class has_growth_failure(DataProperty):
      range = [bool] # for pediatric cases

    class has_status_1A(DataProperty):
      range = [bool] # for liver status 1A

  ORGAN_TYPES = ['kidney', 'liver']
  BLOOD_TYPES = ['A', 'B', 'O', 'AB']

  f = open("cat", "w")
  for pt in onto.Patient.instances():
    pt.organ = [ORGAN_TYPES[rand.randint(0, len(ORGAN_TYPES)-1)]]
    pt.blood_type = [BLOOD_TYPES[rand.randint(0, len(BLOOD_TYPES)-1)]]
    pt.hla_dr = [rand.randint(0, MAX_HLA_DR)]
    pt.cpra = [rand.randint(0, MAX_CPRA_SCORE)]
    
    pt.wait_time = [rand.randint(0, MAX_WAIT_TIME)]
    pt.age = [rand.randint(0, MAX_AGE)]
    pt.latitude = [rand.uniform(MIN_LAT, MAX_LAT)]
    pt.longitude = [rand.uniform(MIN_LONG, MAX_LONG)]

    # kidney properties
    pt.dialysis_time = [rand.randint(0, MAX_AGE)]
    pt.is_prior_donor = [rand.randint(0, 1)]
    pt.has_diabetes = [rand.randint(0, 1)]
    pt.has_prior_transplant = [rand.randint(0, 1)]
    
    # liver properties
    # random.random() Return the next random floating point number in the range [0.0, 1.0).
    pt.sodium_value = [rand.randint(125, 136) + rand.random()]
    pt.creatinine_value = [rand.randint(1, 3) + rand.random()]
    pt.bilirubin_value = [rand.randint(1, 3) + rand.random()]
    pt.INR_value = [rand.randint(1, 2) + rand.random()]
    pt.albumin_value = [rand.randint(1, 8) + rand.random()]
    pt.has_growth_failure = [rand.randint(0, 1)]
    pt.has_status_1A = [rand.choice([1]*1 + [0]*500)]

  #f = open("cat", "w")
  #for pt in onto.Patient.instances():
  #  f.write(pt.latitude, pt.longitude)
  f.close()

  return onto

# expects two tuples d1, d2 as (latitude, longitude)
def is_same_dsa(d1, d2):
  return geodis.vincenty(d1, d2).km < 200

def calculate_kidney_pts(pt, dn):
  kidney_pts = pt.wait_time[0] / 365
  if pt.hla_dr[0] == dn['hla_dr']:
    kidney_pts += 2
    if pt.age[0] <= 10:
      kidney_pts += 4
    elif pt.age[0] <= 17:
      kidney_pts += 3
  else:
    kidney_pts += 1
  if pt.is_prior_donor[0]:
    kidney_pts += 4
  if pt.cpra[0] >= 20:
    kidney_pts += pt.cpra[0] / 5

  adj_age = max(pt.age[0] - 25, 0)
  adj_dialysis = math.log(pt.dialysis_time[0] + 1)
  epts = 0.047 * adj_age
  epts += -0.015 * pt.has_diabetes[0] * adj_age
  epts += 0.398 * pt.has_prior_transplant[0]
  epts += -0.237 * pt.has_diabetes[0] * pt.has_prior_transplant[0]
  epts += 0.315 * adj_dialysis
  epts += -0.099 * pt.has_diabetes[0] * adj_dialysis
  epts += 0.130 * (1 if pt.dialysis_time[0] == 0 else 0)
  epts += -0.348 * pt.has_diabetes[0] * (1 if pt.dialysis_time[0] == 0 else 0)
  epts += 1.262 * pt.has_diabetes[0]
  
  return kidney_pts, epts

def classify_kidney_pt(pt, dn):
  same_dsa = is_same_dsa((pt.latitude[0], pt.longitude[0]), (dn['latitude'], dn['longitude']))
  same_hla_dr = pt.hla_dr[0] == dn['hla_dr']
  cpra = pt.cpra[0]
      
  kidney_pts, epts = calculate_kidney_pts(pt, dn)
  
  clears_epts_threshold = epts > EPTS_THRESHOLD
  
  idx = -1;
  if same_dsa and same_hla_dr and cpra == 100:
    idx = 0;
  elif same_dsa and cpra == 100:
    idx = 1;
  elif same_hla_dr and cpra == 100:
    idx = 2;
  elif cpra == 100:
    idx = 3;
  elif same_dsa and same_hla_dr and cpra >= 98:
    idx = 4;
  elif same_dsa and cpra >= 98:
    idx = 5;
  elif same_hla_dr and cpra >= 98:
    idx = 6;
  elif same_dsa and same_hla_dr and cpra >= 80 and clears_epts_threshold:
    idx = 7;
  elif same_hla_dr and cpra >= 80 and clears_epts_threshold:
    idx = 8;
  elif same_dsa and same_hla_dr and cpra >= 40 and clears_epts_threshold:
    idx = 9;
  elif same_hla_dr and cpra >= 40 and clears_epts_threshold:
    idx = 10;
  elif same_dsa and same_hla_dr and cpra >= 20 and clears_epts_threshold:
    idx = 11;
  elif same_hla_dr and cpra >= 20 and clears_epts_threshold:
    idx = 12;
  else:
    idx = 13;
  
  return idx, kidney_pts
  
def clean_kidney_matches(matches):
  result = []
  for i in range(len(matches)):
    cur = matches[i]
    cur_result = []
    for j in range(len(cur)):
      if len(result) > NUM_MATCHES:
        break;
      cur_result.append(cur[j])
    result.append(sorted(cur_result, key=lambda x: -x[1]))
  return sum(result, [])

def calculate_liver_pts(pt, donor):
  score = 0
  blood_score = 0
  if pt.age[0] >= 12:
    MELD = 0.957*math.log(pt.creatinine_value[0]) + 0.378*math.log(pt.bilirubin_value[0]) + 1.120*math.log(pt.INR_value[0]) + 0.643
    if MELD <= 11:
      MELD = round(MELD*10)
    else:
      MELD = MELD + 1.32*(137-pt.sodium_value[0])-0.033*MELD*(137-pt.sodium_value[0])
    score = MELD
  else: # child
    PELD = 0.48*math.log(pt.bilirubin_value[0]) + 1.857*math.log(pt.INR_value[0]) + 0.667*pt.has_growth_failure[0] - 0.687*math.log(pt.albumin_value[0])
    if pt.age[0] < 1:
      PELD += 0.436
    score = PELD
  if (pt.blood_type[0] == donor['blood_type']):
    blood_score = 10
  elif ((donor['blood_type'] == 'A') and (pt.blood_type[0] == 'AB' or pt.blood_type[0] == 'O')):
    blood_score = 5
  elif ((donor['blood_type'] == 'B') and (pt.blood_type[0] == 'AB')):
    blood_score = 5
  elif ((donor['blood_type'] == 'O') and (pt.blood_type[0] != 'O')):
    blood_score = 5
  
  if score > 40:
    score = 40    
  return score, blood_score

def classify_liver(pt, dn):
  same_dsa = is_same_dsa((pt.latitude[0], pt.longitude[0]), (dn['latitude'], dn['longitude']))
  has_1A = pt.has_status_1A[0]
      
  liver_pts, blood_score = calculate_liver_pts(pt, dn)
  
  if same_dsa and blood_score == 10 and has_1A:
    return 0;
  elif same_dsa and blood_score == 10 and liver_pts == 40:
    return 1;
  elif same_dsa and blood_score == 10 and liver_pts == 39:
    return 2;
  elif same_dsa and blood_score == 10 and liver_pts == 38:
    return 3;
  elif same_dsa and blood_score == 10 and liver_pts == 37:
    return 4;
  elif same_dsa and blood_score == 10 and liver_pts == 36:
    return 5;
  elif same_dsa and blood_score == 10 and liver_pts == 35:
    return 6;
  elif same_dsa and blood_score == 10 and liver_pts >= 15:
    return 7;
  elif (not same_dsa) and blood_score == 10 and has_1A:
    return 8;
  elif (not same_dsa) and blood_score == 10 and liver_pts >= 15:
    return 9;
  elif same_dsa and blood_score == 10 and liver_pts < 15:
    return 10;
  elif (not same_dsa) and blood_score == 10 and liver_pts < 15:
    return 11;
  elif same_dsa and blood_score == 5 and has_1A:
    return 12;
  elif same_dsa and blood_score == 5 and liver_pts == 40:
    return 13;
  elif same_dsa and blood_score == 5 and liver_pts == 39:
    return 14;
  elif same_dsa and blood_score == 5 and liver_pts == 38:
    return 15;
  elif same_dsa and blood_score == 5 and liver_pts == 37:
    return 16;
  elif same_dsa and blood_score == 5 and liver_pts == 36:
    return 17;
  elif same_dsa and blood_score == 5 and liver_pts == 35:
    return 18;
  elif same_dsa and blood_score == 5 and liver_pts >= 15:
    return 19;
  elif (not same_dsa) and blood_score == 5 and has_1A:
    return 20;
  elif (not same_dsa) and blood_score == 5 and liver_pts >= 15:
    return 21;
  elif same_dsa and blood_score == 5 and liver_pts < 15:
    return 22;
  elif (not same_dsa) and blood_score == 5 and liver_pts < 15:
    return 23;
  else:
    return 24;

def clean_liver_matches(matches):
  result = []
  for i in range(len(matches)):
    cur = matches[i]
    sorted_cur = sorted(cur, key = lambda x: -x[1])
    for j in range(len(sorted_cur)):
      if len(result) > NUM_MATCHES:
        break;
      result.append([sorted_cur[j]])
  return sum(result, [])

def print_pt(pt):
  print(pt.name)
  print('organ:', pt.organ[0], '; blood type:', pt.blood_type[0], '; HLA-DR:', pt.hla_dr[0])
  print('\tCPRA:', pt.cpra[0], '; wait time:', pt.wait_time[0], '; age:', pt.age[0], '; latitude:', pt.latitude[0], '; longitude:', pt.longitude[0])
  if (pt.organ[0] == 'kidney'):
    print('\tdialysis time:', pt.dialysis_time[0], '; is prior donor:', pt.is_prior_donor, '; has diabetes:', pt.has_diabetes[0], '; has prior transplant:', pt.has_prior_transplant[0])  
  else:
    print('\tsodium:', round(pt.sodium_value[0], 2), '; creatinine:', round(pt.creatinine_value[0], 2), '; bilirubin:', round(pt.bilirubin_value[0], 2), '; INR:', pt.INR_value[0], '; albumin:', round(pt.albumin_value[0], 2), '; has growth failure:', pt.has_growth_failure[0], '; has status 1A:', pt.has_status_1A[0])
  
def print_dn(dn):
  organ = ('kidney' if dn['kidney'] else 'liver')
  print('organ:', organ, '; blood type:', dn['blood_type'], '; HLA-DR:', dn['hla_dr'], '; latitude:', dn['latitude'], '; longitude:', dn['longitude'])

def find_matching_patients(onto, dn):
  
  kidney_matches = [[] for _ in range(NUM_KIDNEY_BUCKETS)]
  liver_matches = [[] for _ in range(NUM_LIVER_BUCKETS)]
      
  for pt in onto.Patient.instances():
    
    if 'kidney' in pt.organ:
      if pt.blood_type[0] != dn['blood_type']:
        continue
      
      bucket_idx, kidney_pts = classify_kidney_pt(pt, dn)
      kidney_matches[bucket_idx].append((pt, kidney_pts))
      
    elif 'liver' in pt.organ:
      liver_bucket_idx = classify_liver(pt, dn)
      liver_matches[liver_bucket_idx].append((pt, pt.wait_time[0]))     
      
  kidney_matches = clean_kidney_matches(kidney_matches)
  liver_matches = clean_liver_matches(liver_matches)
      
  return {
      'kidney': kidney_matches,
      'liver': liver_matches
  }

# def generate_donors(is_kidney):
#   result = []
#   for _ in range(5):
#     donor = {
#       'kidney': is_kidney,
#       'liver': not is_kidney,
#       'blood_type': BLOOD_TYPES[rand.randint(0, len(BLOOD_TYPES)-1)],
#       'hla_dr': rand.randint(0, MAX_HLA_DR),
#       'latitude': rand.randint(MIN_LAT, MAX_LAT),
#       'longitude': rand.randint(MIN_LONG, MAX_LONG)
#     }
#     result.append(donor)
#   return result

# kidney_donors = generate_donors(True)
# liver_donors = generate_donors(False)