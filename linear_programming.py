import tkinter as tk
from tkinter import ttk, messagebox
import pulp

class LinearProgrammingGUI:
    def __init__(self, master):
        self.master = master
        master.title("Linear Programming Solver")

        # Style configurations for a sleek UI
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11), background="#4CAF50", foreground="white")
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("TCombobox", font=("Helvetica", 11))
        master.configure(bg="#f5f5f5")

        self.variables_count = 5  # default number of variables

        # Frames
        self.top_frame = ttk.Frame(master, padding=10)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.objective_frame = ttk.LabelFrame(master, text="Objective Function", padding=(10,10))
        self.objective_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.constraints_frame = ttk.LabelFrame(master, text="Constraints", padding=(10,10))
        self.constraints_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.solve_frame = ttk.Frame(master, padding=(10,10))
        self.solve_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Top frame: Variable count and objective direction
        ttk.Label(self.top_frame, text="Number of variables:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_vars_var = tk.IntVar(value=self.variables_count)
        self.num_vars_entry = ttk.Entry(self.top_frame, textvariable=self.num_vars_var, width=5)
        self.num_vars_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top_frame, text="Objective:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.obj_direction_var = tk.StringVar(value="Maximize")
        direction_cb = ttk.Combobox(self.top_frame, textvariable=self.obj_direction_var, values=["Maximize", "Minimize"], width=10)
        direction_cb.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        set_vars_btn = ttk.Button(self.top_frame, text="Set Variables", command=self.update_variables)
        set_vars_btn.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # Objective function inputs will be built dynamically
        self.obj_entries = []
        self.build_objective_inputs()

        # Constraints input
        ttk.Label(self.constraints_frame, text="Number of constraints:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_constraints_var = tk.IntVar(value=3)
        self.num_constraints_entry = ttk.Entry(self.constraints_frame, textvariable=self.num_constraints_var, width=5)
        self.num_constraints_entry.grid(row=0, column=1, padx=5, pady=5)

        update_constraints_btn = ttk.Button(self.constraints_frame, text="Update Constraints", command=self.build_constraint_inputs)
        update_constraints_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Constraint rows will be built dynamically
        self.constraint_rows_frame = ttk.Frame(self.constraints_frame)
        self.constraint_rows_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.constraint_entries = []
        self.build_constraint_inputs()

        # Solve button and result display
        solve_btn = ttk.Button(self.solve_frame, text="Solve", command=self.solve_lp)
        solve_btn.grid(row=0, column=0, padx=10, pady=10)

        self.result_text = tk.Text(self.solve_frame, height=8, width=70, font=("Helvetica", 11))
        self.result_text.grid(row=1, column=0, padx=10, pady=10)

    def update_variables(self):
        # Update the number of variables
        try:
            new_var_count = self.num_vars_var.get()
            if new_var_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive integer for the number of variables.")
            return

        self.variables_count = new_var_count
        self.build_objective_inputs()
        self.build_constraint_inputs()

    def build_objective_inputs(self):
        # Clear existing objective frame widgets except the frame
        for widget in self.objective_frame.winfo_children():
            widget.destroy()

        # Label for objective direction
        direction = self.obj_direction_var.get()
        dir_text = "Maximize:" if direction == "Maximize" else "Minimize:"
        ttk.Label(self.objective_frame, text=dir_text).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.obj_entries = []
        for i in range(self.variables_count):
            ttk.Label(self.objective_frame, text=f"x{i+1} coefficient:").grid(row=0, column=2*i+1, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(self.objective_frame, width=5)
            entry.grid(row=0, column=2*i+2, padx=5, pady=5, sticky="w")
            self.obj_entries.append(entry)

    def build_constraint_inputs(self):
        # Clear existing constraint rows
        for widget in self.constraint_rows_frame.winfo_children():
            widget.destroy()

        self.constraint_entries = []

        num_constraints = self.num_constraints_var.get()

        # Headers
        headers = [f"x{i+1}" for i in range(self.variables_count)] + ["Relation", "RHS"]
        for j, h in enumerate(headers):
            ttk.Label(self.constraint_rows_frame, text=h).grid(row=0, column=j, padx=5, pady=5)

        # Build entries for constraints
        for i in range(num_constraints):
            row_entries = []
            for var_col in range(self.variables_count):
                e = ttk.Entry(self.constraint_rows_frame, width=5)
                e.grid(row=i+1, column=var_col, padx=5, pady=5)
                row_entries.append(e)

            relation_cb = ttk.Combobox(self.constraint_rows_frame, values=["<=", "=", ">="], width=3)
            relation_cb.set("<=")
            relation_cb.grid(row=i+1, column=self.variables_count, padx=5, pady=5)
            row_entries.append(relation_cb)

            rhs_entry = ttk.Entry(self.constraint_rows_frame, width=6)
            rhs_entry.grid(row=i+1, column=self.variables_count+1, padx=5, pady=5)
            row_entries.append(rhs_entry)

            self.constraint_entries.append(row_entries)

    def solve_lp(self):
        # Clear previous results
        self.result_text.delete("1.0", tk.END)

        # Determine objective direction
        direction = self.obj_direction_var.get()
        if direction == "Maximize":
            problem = pulp.LpProblem("LP_Problem", pulp.LpMaximize)
        else:
            problem = pulp.LpProblem("LP_Problem", pulp.LpMinimize)

        # Define variables: x1,...xN >= 0
        x = [pulp.LpVariable(f"x{i+1}", lowBound=0) for i in range(self.variables_count)]

        # Objective
        try:
            obj_coefs = [float(e.get()) if e.get().strip() != "" else 0.0 for e in self.obj_entries]
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all objective coefficients are numeric.")
            return

        problem += pulp.lpSum([obj_coefs[i]*x[i] for i in range(self.variables_count)]), "Objective"

        # Constraints
        for row in self.constraint_entries:
            try:
                coefs = [float(e.get()) if e.get().strip() != "" else 0.0 for e in row[:self.variables_count]]
                relation = row[self.variables_count].get().strip()
                rhs = float(row[self.variables_count+1].get())
            except ValueError:
                messagebox.showerror("Input Error", "Please ensure all constraint values are numeric.")
                return

            lhs = pulp.lpSum([coefs[i]*x[i] for i in range(self.variables_count)])
            if relation == "<=":
                problem += (lhs <= rhs)
            elif relation == "=":
                problem += (lhs == rhs)
            elif relation == ">=":
                problem += (lhs >= rhs)

        # Solve the problem
        problem_status = problem.solve(pulp.PULP_CBC_CMD(msg=0))

        # Display Results
        status_str = pulp.LpStatus[problem_status]
        self.result_text.insert(tk.END, f"Status: {status_str}\n")

        if pulp.LpStatus[problem_status] == "Optimal":
            self.result_text.insert(tk.END, "Optimal Solution Found:\n")
            for var in x:
                self.result_text.insert(tk.END, f"{var.name} = {pulp.value(var)}\n")
            self.result_text.insert(tk.END, f"Objective Value: {pulp.value(problem.objective)}\n")
        else:
            self.result_text.insert(tk.END, "No optimal solution found.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgrammingGUI(root)
    root.mainloop()
