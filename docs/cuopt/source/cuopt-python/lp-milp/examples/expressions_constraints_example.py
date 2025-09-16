from cuopt.linear_programming.problem import Problem, MAXIMIZE
from cuopt.linear_programming.solver_settings import SolverSettings

problem = Problem("Expression Example")

# Create variables
x = problem.addVariable(lb=0, name="x")
y = problem.addVariable(lb=0, name="y")
z = problem.addVariable(lb=0, name="z")

# Create complex expressions
expr1 = 2 * x + 3 * y - z
expr2 = x + y + z

# Add constraints using expressions
problem.addConstraint(expr1 <= 100, name="Complex_Constraint_1")
problem.addConstraint(expr2 >= 20, name="Complex_Constraint_2")

# Add constraint with different senses
problem.addConstraint(x + y == 50, name="Equality_Constraint")
problem.addConstraint(1 * x <= 30, name="Upper_Bound_X")
problem.addConstraint(1 * y >= 10, name="Lower_Bound_Y")
problem.addConstraint(1 * z <= 100, name="Upper_Bound_Z")

# Set objective
problem.setObjective(x + 2 * y + 3 * z, sense=MAXIMIZE)

settings = SolverSettings()
settings.set_parameter("time_limit", 20)

problem.solve(settings)

if problem.Status.name == "Optimal":
    print("=== Expression Example Results ===")
    print(f"x = {x.getValue()}")
    print(f"y = {y.getValue()}")
    print(f"z = {z.getValue()}")
    print(f"Objective value = {problem.ObjValue}")
