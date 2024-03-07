from itertools import product

p = product("ГИПЕРБОЛА", repeat=6)

s = map(lambda x: "".join(x), p)
c = 0
for i in s:
    if i[0] in "ИЕОА" and i[-1] in "ИЕОА":
        for l in range(1, 5):
            if i[l] in "ИЕОА":
                if i[l-1] in "ГПРБЛ" or i[l+1] in "ГПРБЛ":
                    break
                else:
                    c += 1
print(c)
