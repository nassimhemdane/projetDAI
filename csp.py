import math
import random
import itertools

N = 14
K = 3
sets = []

l = list(range(1, N+1))
random.shuffle(l)

for i in range(0, K):
    sets.append([])

set_counter = 0
current_set = 0
per_set = math.floor(N/K)
for i in range(0, per_set*K):
    sets[current_set].append(l[i])
    set_counter += 1
    if set_counter == per_set:
        current_set += 1
        set_counter = 0

for i in range(per_set*K, N):
    sets[len(sets)-1].append(l[i])

for i in range(len(sets)):
    sets[i] = sorted(sets[i])

def check_valid_subset(l):
    sum_inf_n = [sum(x) for x in list(itertools.combinations_with_replacement(l, 2)) if sum(x) < N]
    for i in l:
        if i in sum_inf_n:
            return False
    return True

def critere_arret(sets):
    for i in range(len(sets)):
        if not check_valid_subset(sets[i]):
            return False
    return True

def transition(sets):
    l1 = list(range(0, K))
    random.shuffle(l1)
    s1 = l1[0]
    s2 = l1[1]
    l1_ = list(range(0, len(sets[s1])))
    l2_ = list(range(0, len(sets[s2])))
    random.shuffle(l1_)
    random.shuffle(l2_)
    s1_ = l1_[0]
    s2_ = l2_[1]
    tmp = sets[s1][s1_]
    sets[s1][s1_] = sets[s2][s2_]
    sets[s2][s2_] = tmp
    return sets


while not critere_arret(sets):
    sets = transition(sets)
    for i in range(len(sets)):
        sets[i] = sorted(sets[i])

p = 0
for s in sets:
    print("P"+str(p+1)+" :", end=" ")
    print(" ".join([str(s_) for s_ in s]), end=" ")
    print("[", end="")
    print(" ".join([str(x) for x in [sum(x) for x in list(itertools.combinations_with_replacement(s, 2)) if sum(x) < N]]), end="")
    print("]")
    p += 1