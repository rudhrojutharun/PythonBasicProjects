import tkinter as tk
import math

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Scientific Calculator")
        master.configure(bg="#222")  # Dark background for a sleek look
        
        # --- Display Screen ---
        self.display = tk.Entry(master, width=30, borderwidth=5, font=('Arial', 24),
                                justify='right', bg="#444", fg="#fff")
        self.display.grid(row=0, column=0, columnspan=5, padx=10, pady=10, ipady=10)
        
        # --- Button Layout ---
        # Numbers and basic operators
        buttons = [
            '7', '8', '9', '/', 'C',
            '4', '5', '6', '*', 'sqrt',
            '1', '2', '3', '-', 'sin',
            '0', '.', '=', '+', 'cos',
            '(', ')', 'log', 'tan', 'pi'
        ]
        
        # Grid layout for buttons
        row_val = 1
        col_val = 0
        for button in buttons:
            if button == '=':
                tk.Button(master, text=button, padx=20, pady=20, font=('Arial', 18),
                          command=self.calculate, bg="#555", fg="#fff").grid(row=row_val, column=col_val, sticky="nsew")
            elif button == 'C':
                 tk.Button(master, text=button, padx=20, pady=20, font=('Arial', 18),
                          command=self.clear_display, bg="#c33", fg="#fff").grid(row=row_val, column=col_val, sticky="nsew")
            else:
                tk.Button(master, text=button, padx=20, pady=20, font=('Arial', 18),
                          command=lambda b=button: self.add_to_display(b), bg="#555", fg="#fff").grid(row=row_val, column=col_val, sticky="nsew")
            
            col_val += 1
            if col_val > 4:
                col_val = 0
                row_val += 1
                
        # Configure grid to expand with window size
        for i in range(5):
            master.grid_columnconfigure(i, weight=1)
        for i in range(1, 6):
            master.grid_rowconfigure(i, weight=1)

    def add_to_display(self, value):
        self.display.insert(tk.END, value)
        
    def clear_display(self):
        self.display.delete(0, tk.END)
        
    def calculate(self):
        try:
            expression = self.display.get()
            # Replace scientific function names with Python's math module
            expression = expression.replace('sqrt', 'math.sqrt')
            expression = expression.replace('sin', 'math.sin')
            expression = expression.replace('cos', 'math.cos')
            expression = expression.replace('tan', 'math.tan')
            expression = expression.replace('log', 'math.log10')
            expression = expression.replace('pi', 'math.pi')

            # Use eval() to calculate the result of the expression
            result = str(eval(expression))
            self.clear_display()
            self.display.insert(0, result)
        except Exception as e:
            self.clear_display()
            self.display.insert(0, "Error")

# --- Main Application Loop ---
if __name__ == "__main__":
    root = tk.Tk()
    my_calculator = Calculator(root)
    root.mainloop()