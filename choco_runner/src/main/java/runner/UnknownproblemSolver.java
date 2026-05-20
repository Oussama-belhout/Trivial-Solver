package runner;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.exception.SolverException;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.ResolutionOrder;
import org.chocosolver.util.tools.ArrayUtils;

public class UnknownproblemSolver {

    public static void main(String[] args) {
        Model model = new Model("UnknownProblem");
        
        // Item weights: [2, 3, 6, 7, 5]
        // Item values: [6, 5, 8, 9, 6]
        int[] weights = {2, 3, 6, 7, 5};
        int[] values = {6, 5, 8, 9, 6};
        
        IntVar[] vars = model.intVarArray("x", 5, 0, 1);
        
        // Weight constraint: sum(weights[i] * x[i]) <= 10
        model.sum(weights, vars, "=", 10).post();
        
        // Value maximization
        IntVar totalValue = model.intVar("totalValue", 0, 30);
        model.sum(values, vars, "=", totalValue).post();
        model.maximize(totalValue, Search.MINIMIZE);
        
        Solver solver = model.getSolver();
        
        // Add monitor
        solver.plugMonitor(new org.chocosolver.solver.search.limits.MonitorSolution() {
            @Override
            public void onSolution() {
                System.out.println("MONITOR_SOLUTION: ");
                for (int i = 0; i < vars.length; i++) {
                    System.out.print("x" + (i+1) + "=" + vars[i].getValue() + " ");
                }
                System.out.println();
            }
        });
        
        try {
            boolean solutionFound = solver.solve();
            if (solutionFound) {
                System.out.println("SOLUTION: ");
                for (int i = 0; i < vars.length; i++) {
                    System.out.print("x" + (i+1) + "=" + vars[i].getValue() + " ");
                }
                System.out.println();
                System.out.println("Total Value: " + totalValue.getValue());
            } else {
                System.out.println("NO_SOLUTION_FOUND");
            }
            solver.printStatistics();
        } catch (SolverException e) {
            e.printStackTrace();
        }
    }
}