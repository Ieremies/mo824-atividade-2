import gurobipy as gp
from gurobipy import GRB

# tested with Python 3.7 & Gurobi 9.0.0
m = gp.Model()

# Variables: is city 'i' adjacent to city 'j' on the tour?
vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='x')

# TODO adicionar o segundo tuor
# TODO adicionar as variáveis D_e

# Symmetric direction: Copy the object
for i, j in vars.keys():
    vars[j, i] = vars[i, j]  # edge in opposite direction

# Constraints: two edges incident to each city
cons = m.addConstrs(vars.sum(c, '*') == 2 for c in capitals)

# TODO adicionar as restrições de D_e

# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                             if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(capitals):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                         <= len(tour)-1)

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
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle # New shortest subtour
    return cycle

m._vars = vars
m.Params.lazyConstraints = 1
m.optimize(subtourelim)

# Retrieve solution

vals = m.getAttr('x', vars)
selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

tour = subtour(selected)
assert len(tour) == len(capitals)
