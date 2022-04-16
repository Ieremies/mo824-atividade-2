from sys import argv

coord = [ [], [] ]


with open("inst/coord", "rb") as f:
    for i in range(int(argv[1])):
        l = f.read().split()
        coord[1].append((int(l[0]), int(l[1])))
        coord[2].append((int(l[2]), int(l[3])))
