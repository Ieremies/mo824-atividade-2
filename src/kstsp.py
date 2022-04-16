import gurobipy as gp
from gurobipy import GRB
from itertools import combinations
import math
from sys import argv

# Read
coordinates = [ [], [] ]
capitals = []
with open("coord", "r", encoding="utf-8") as f:
    for i in range(int(argv[1])):
        linha = f.readline().split()
        capitals.append(i)
        coordinates[0].append((int(linha[0]), int(linha[1])))
        coordinates[1].append((int(linha[2]), int(linha[3])))

def distance(city1, city2, tuor):
    c1 = coordinates[tuor][city1]
    c2 = coordinates[tuor][city2]
    diff = (c1[0]-c2[0], c1[1]-c2[1])
    return math.ceil(math.sqrt(diff[0]*diff[0]+diff[1]*diff[1]))

dist = []
dist.append({(c1,c2): distance(c1,c2,0) for c1, c2 in combinations(capitals,2)})
dist.append({(c1,c2): distance(c1,c2,1) for c1, c2 in combinations(capitals,2)})

# tested with Python 3.7 & Gurobi 9.0.0
m = gp.Model()

# Variables: is city 'i' adjacent to city 'j' on the tour?
vars0 = m.addVars(dist[0].keys(), obj=dist[0], vtype=GRB.BINARY, name='x_0')
vars1 = m.addVars(dist[1].keys(), obj=dist[1], vtype=GRB.BINARY, name='x_1')
dup = m.addVars([(c1,c2) for c1 in capitals for c2 in capitals], obj=0, vtype=GRB.BINARY, name="D")

# Symmetric direction: Copy the object
for i, j in vars0.keys():
    vars0[j, i] = vars0[i, j]  # edge in opposite direction
for i, j in vars1.keys():
    vars1[j, i] = vars1[i, j]  # edge in opposite direction

# Constraints: two edges incident to each city
cons0 = m.addConstrs(vars0.sum(c, '*') == 2 for c in capitals)
cons1 = m.addConstrs(vars1.sum(c, '*') == 2 for c in capitals)

# restrições de D_e
m.addConstrs(vars0[k] >= dup[k] for k in vars0.keys())
m.addConstrs(vars1[k] >= dup[k] for k in vars1.keys())
m.addConstr(dup.sum("*") >= int(argv[2])) # mudar para K


# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars0)
        selected = gp.tuplelist((i, j) for i, j in model._vars0.keys() if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(capitals):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(gp.quicksum(model._vars0[i, j] for i, j in combinations(tour, 2)) <= len(tour)-1)

# Given a tuplelist of edges, find the shortest subtour

def subtour(edges):
    unvisited = capitals[:]
    cycle = capitals[:] # Dummy - guaranteed to be replaced
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*') if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle # New shortest subtour
    return cycle

m._vars0 = vars0
m._vars1 = vars1
m.Params.lazyConstraints = 1
m.optimize(subtourelim)

# Retrieve solution

# vals0 = m.getAttr('x_0', vars0)
# vals1 = m.getAttr('x_1', vars1)
# selected0 = gp.tuplelist((i, j) for i, j in vals0.keys() if vals[i, j] > 0.5)
# selected1 = gp.tuplelist((i, j) for i, j in vals1.keys() if vals[i, j] > 0.5)

# tour0 = subtour(selected0)
# tour1 = subtour(selected1)
# #assert len(tour) == len(capitals)
