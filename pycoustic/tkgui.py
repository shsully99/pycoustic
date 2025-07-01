import tkinter as tk
from tkinter import filedialog ,Toplevel, IntVar, Checkbutton, Button
from tkinter import ttk
from tkinter import messagebox
from log import Log
from survey import Survey
import os
import pandas as pd
from tkinter import StringVar
import inspect
#import matplotlib
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#from pycoustic import log  # Assuming log is an instance of a class with the required methods
test = 0

class ToolTip:
    """
    Create a tooltip for a given widget with hover and click functionality
    """
    def __init__(self, widget, text='widget info', full_text=None):
        self.widget = widget
        self.text = text
        self.full_text = full_text or text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button-1>", self.on_click)
        self.tipwindow = None
        self.full_window = None

    def on_enter(self, event=None):
        self.show_tooltip()

    def on_leave(self, event=None):
        self.hide_tooltip()

    def on_click(self, event=None):
        self.show_full_docstring()

    def show_tooltip(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"), wraplength=300)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def show_full_docstring(self):
        if self.full_window:
            self.full_window.destroy()
        
        self.full_window = tw = Toplevel(self.widget)
        tw.title("Parameter Documentation")
        tw.geometry("600x400")
        
        # Center the window
        tw.transient(self.widget.winfo_toplevel())
        tw.grab_set()
        
        # Create text widget with scrollbar
        frame = ttk.Frame(tw)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, self.full_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(tw, text="Close", command=tw.destroy)
        close_btn.pack(pady=5)

class Application(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("pycoustic Log Viewer")
        
        # Calculate 2/3 of screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = int(screen_width * 2/3)
        window_height = int(screen_height * 2/3)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        import tkinter as tk

        # Create an instance of Survey
        self.survey = Survey()

        self.create_widgets()

    def create_widgets(self):

        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_columnconfigure((3,4,5), weight=2)
        self.grid_rowconfigure(7, weight=1)  # Make the treeview row expandable

        self.log_label = ttk.Label(self, text="csv file name:")
        self.log_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.log_file = ttk.Label(self, text="Click Browse to select")
        self.log_file.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.browse_button1 = ttk.Button(self, text="Browse", command=self.browse_log)
        self.browse_button1.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.analysis_label = ttk.Label(self, text="Select Analysis Type:")
        self.analysis_label.grid(row=3, column=0, padx=5, pady=10, sticky="e")

        self.analysis_var = StringVar()
        self.analysis_combobox = ttk.Combobox(self, textvariable=self.analysis_var, values=["resi_summary", "modal", "lmax_spectra", "leq_spectra"])
        self.analysis_combobox.set("resi_summary")
        self.analysis_combobox.grid(row=3, column=1, padx=5, pady=10, sticky="w")
        self.analysis_var.trace("w", self.on_analysischange)

        # Function Description button
        self.function_desc_button = ttk.Button(self, text="Function Description", command=self.show_function_description)
        self.function_desc_button.grid(row=3, column=2, padx=5, pady=10, sticky="w")

        # Function Description button
        self.function_desc_button = ttk.Button(self, text="Function Description", command=self.show_function_description)
        self.function_desc_button.grid(row=3, column=2, padx=5, pady=10, sticky="w")

        # Create parameter input frame
        self.create_parameter_inputs()

        self.execute_button = ttk.Button(self, text="Select Columns", command=self.Column_Selection_Modal)
        self.execute_button.grid(row=6, column=0, padx=5, pady=10, sticky="e")

        self.execute_button = ttk.Button(self, text="Execute", command=self.execute_code)
        self.execute_button.grid(row=6, column=2, padx=5, pady=10, sticky="w")

        self.tree = ttk.Treeview(self, show="headings")
        self.tree_scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree_scroll_y.grid(row=7, column=6, sticky="ns")

        self.tree_scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree_scroll_x.grid(row=8, column=0, columnspan=3, sticky="ew")

        self.tree.configure(yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        self.tree.grid(row=7, column=0, columnspan=4, padx=20, pady=20, sticky="nsew")
    """
      # Button to open the modal dialog
        open_dialog_button = ttk.Button(self, text="Show Time Series", command=self.open_modal_dialog)
        open_dialog_button.grid(row=5, column=2, padx=5, pady=10, sticky="w")


    # Commented out section that displays a graph
    def open_modal_dialog(self):
        dialog = Toplevel(self)
        dialog.title("Modal Dialog")

        # Make the dialog modal
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog on the screen
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        window_x = self.winfo_x()
        window_y = self.winfo_y()

        dialog_width = 900
        dialog_height = 600

        position_right = int(window_x + (window_width / 2) - (dialog_width / 2))
        position_down = int(window_y + (window_height / 2) - (dialog_height / 2))

        dialog.geometry(f"{dialog_width}x{dialog_height}+{position_right}+{position_down}")
        import matplotlib.pyplot as plt

        # Create a figure and axis
        fig, ax = plt.subplots()

        # Plot the data
        #print ("----",self.df.columns[1][0],self.df.columns[1][1] )        
        #print ("----",type(self.df.columns[1]))
        
        leq_a_column = [col for col in self.df.columns if isinstance(col, tuple) and col[0] == "Leq" and col[1] == "A"]
        if not leq_a_column:
            messagebox.showerror("Error", "No columns found with ('Leq', 'A') in the header.")
            return

        l90_a_columns = [col for col in self.df.columns if isinstance(col, tuple) and col[0] == "L90" and col[1] == "A"]
        if not l90_a_columns:
            messagebox.showerror("Error", "No columns found with ('L90', 'A') in the header.")
            return


        self.df["Date"] = pd.to_datetime(self.df.index)
        #print(self.df)

        ax.plot(self.df["Date"], self.df[leq_a_column[0]], label='LAeq')
        ax.plot(self.df["Date"], self.df[l90_a_column[0]], label='LA90')
        #ax.plot(self.df['Index'], self.df['L90 A'], label='la90')

        # Format the x-axis to show dates properly
        fig.autofmt_xdate()

        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Values')
        ax.set_title('Time Series Line Chart')
        ax.legend()

        # Create a canvas to display the plot in the Tkinter dialog
        canvas = FigureCanvasTkAgg(fig, master=dialog)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        #else:
        #    messagebox.showerror("Error", "DataFrame does not contain required columns: 'date', 'Laeq', 'la90'")

        # OK button to close the dialog
        ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=20)

    """

    def on_analysischange(self, *args):
        analysis_type = self.analysis_combobox.get()
        if analysis_type == "resi_summary":
            self.params_frame.grid()
        else:
            self.params_frame.grid_remove()
        return
 
  
    def browse_log(self):
        self.logpath = os.getcwd  ()
        file_path = tk.filedialog.askopenfilename(initialdir=self.logpath, filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.logname = os.path.basename(file_path)
            self.logpath = os.path.dirname(file_path)
            self.log_file.config(text=self.logname)

            strPath = self.logpath + "\\" + self.logname
            self.log  = Log(path=strPath)
            self.survey.add_log(data=self.log, name="Position 1")

            self.df = self.log.get_data()

            # Clear the treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Round the dataframe values to 1 decimal place, except for the column headers
            self.df = self.df.round(1)
 
            # Insert new data into the treeview
            self.tree["columns"] = ["Index"] + list(self.df.columns)
            self.tree.heading("Index", text="Index")
            self.tree.column("Index", width=150, stretch=True)

            i = 0 
            for col in self.df.columns:
                self.tree.heading(col, text=col)
                i=i+1
                if i < 12:
                    self.tree.column(col, width=75,stretch=True, anchor="center")
                else:
                    self.tree.column(col, width=0,stretch=False, anchor="center")
          
            for index, row in self.df.iterrows():
                self.tree.insert("", "end", values=[index] + list(row))
            return
 
    def execute_code(self):
        analysis_type = self.analysis_combobox.get()

        try:
            df = pd.DataFrame()
            if analysis_type == "resi_summary":
                # Get parameters from individual input fields
                leq_measurement = self.leq_cols_measurement.get().strip()
                leq_weighting = self.leq_cols_weighting.get().strip()
                max_measurement = self.max_cols_measurement.get().strip()
                max_weighting = self.max_cols_weighting.get().strip()
                lmax_n = int(self.lmax_n_entry.get().strip())
                lmax_t_value = self.lmax_t_entry.get().strip()
                lmax_t = f"{lmax_t_value}min"
                
                # Create tuples for leq_cols and max_cols
                leq_cols = [(leq_measurement, leq_weighting)] if leq_measurement and leq_weighting else None
                max_cols = [(max_measurement, max_weighting)] if max_measurement and max_weighting else None
                print (f"leq_cols: {leq_cols}, max_cols: {max_cols}, lmax_n: {lmax_n}, lmax_t: {lmax_t}")
                df = self.survey.resi_summary(leq_cols=leq_cols, max_cols=max_cols, lmax_n=lmax_n, lmax_t=lmax_t)

            elif analysis_type == "modal":
                df = self.survey.modal()
            elif analysis_type == "lmax_spectra":
                df = self.survey.lmax_spectra()
            elif analysis_type == "leq_spectra":
                df = self.survey.leq_spectra()
            else:
                messagebox.showerror("Error", "Please select an analysis type.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return
        
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Set new column headers based on the dataframe
        #self.tree["columns"] = list(df.columns)

        # Insert new data into the treeview
        self.tree["columns"] = ["Index"] + list(df.columns)
        self.tree.heading("Index", text="Index")
        self.tree.column("Index", width=150, anchor="center", stretch=True)
        

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=75, anchor="center", stretch=True)
   
        # Insert new data into the treeview
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=[index] + list(row))

        # Copy the DataFrame to the clipboard
        df.to_clipboard(index=True)
        messagebox.showinfo("Success", "DataFrame copied to clipboard.")


    def Column_Selection_Modal(self):   
        # Create a modal dialog
        #print ("def Column_Selection_Modal(self):")

        dialog = Toplevel(self)
        dialog.title("Select Columns")

        # Make the dialog modal
        dialog.transient(self)
        dialog.grab_set()

        #self.window.update_idletasks()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        window_x = self.winfo_x()
        window_y = self.winfo_y()

        dialog_width = 300
        dialog_height = 600

        position_right = int(window_x + (window_width / 2) - (dialog_width / 2))
        position_down = int(window_y + (window_height / 2) - (dialog_height / 2))

        dialog.geometry(f"{dialog_width}x{dialog_height}+{position_right}+{position_down}")

        # Configure grid rows and columns
        for i in range(12):  # Adjust the range as needed
            dialog.rowconfigure(i,weight =1,uniform = 'a')

        for i in range(3):  # Adjust the range as needed
            dialog.grid_columnconfigure(i,  weight =1,minsize = 20,uniform = 'a')

        # Get the column identifiers
        column_ids = self.tree["columns"]
        #print ("col ids",column_ids)

        # Get the column headers
        column_headers = [self.tree.heading(col)["text"] for col in column_ids]

        # Get the column widths
        column_widths = [self.tree.column(col)["width"] for col in column_ids]


        self.column_vars = {}
        for i, column in enumerate(column_headers):
            # Check if the column is visible in self.tree
            self.column_vars[column] = IntVar(master=dialog, value=1 if column_widths[i] > 0 else 0)
        self.cb = []

        # Create checkboxes for each column
        for i, column in enumerate(column_headers):
            #print(f"Column: {column}, Value: {self.column_vars[column].get()}")            
            self.cb.append( Checkbutton(dialog, text=column, variable=self.column_vars[column]))
            #self.cb[i].grid(row=i+1, column=(i-1)/10, sticky='w')
            self.cb[i].grid(row=i%10, column=i//10, sticky='w')

        for i, column in enumerate(column_headers):
            self.column_vars[column].set(1 if column_widths[i] > 0 else 0)

        # OK button to apply the selection
        ttk.Button(dialog, text="OK", command=lambda: self.apply_column_selection(dialog)).grid(row=13, column=1, ipady=10)
       # Cancel button
        def on_cancel():
            #print("Cancel clicked")
            dialog.destroy()

        cancel_button = ttk.Button(dialog, text="Cancel", command=on_cancel)
        cancel_button.grid(row=13,column = 2, sticky = "w",ipady = 10)   

        return     

    def apply_column_selection(self, dialog):

        #print("def apply_column_selection")

        # Get the selected columns
        selected_columns = [column for column, var in self.column_vars.items() if var.get() == 1]

        # Set the column widths based on the selection
        for column in self.tree["columns"]:
            column_text = self.tree.heading(column)["text"]
            if column_text in selected_columns:
                self.tree.column(column, width=250,stretch=True, anchor="center")  # Set to a default width
            else:
                self.tree.column(column, width=0,stretch=False, anchor="center")  # Hide the column

        # Display the selected columns in the listbox
        #for item in self.tree:
        #    display_text = " | ".join(str(item[column]) for column in selected_columns)
        #    self.listbox.insert(END, display_text)
        # Close the dialog
        dialog.destroy()

    def create_parameter_inputs(self):
        """Create parameter input fields for different analysis types"""
        
        # Get docstring information
        param_docs = self.get_resi_summary_docstring_info()
        
        # Parameters frame
        self.params_frame = ttk.LabelFrame(self, text="Analysis Parameters", padding="15")
        self.params_frame.grid(row=4, column=0, columnspan=6, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights for even spacing - each section gets equal space
        self.params_frame.grid_columnconfigure(0, weight=1, uniform="param_group")  # LEQ section
        self.params_frame.grid_columnconfigure(1, weight=1, uniform="param_group")  # MAX section  
        self.params_frame.grid_columnconfigure(2, weight=1, uniform="param_group")  # LMAX_N section
        self.params_frame.grid_columnconfigure(3, weight=1, uniform="param_group")  # LMAX_T section
        
        # LEQ_COLS section
        leq_frame = ttk.LabelFrame(self.params_frame, text="LEQ Columns", padding="10")
        leq_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Label(leq_frame, text="Measurement:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.leq_cols_measurement = ttk.Entry(leq_frame, width=12)
        self.leq_cols_measurement.insert(0, "Leq")
        self.leq_cols_measurement.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Add tooltip for LEQ measurement
        if 'leq_cols' in param_docs:
            ToolTip(self.leq_cols_measurement, 
                   param_docs['leq_cols']['short'], 
                   param_docs['leq_cols']['full'])
        
        ttk.Label(leq_frame, text="Weighting:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.leq_cols_weighting = ttk.Entry(leq_frame, width=12)
        self.leq_cols_weighting.insert(0, "A")
        self.leq_cols_weighting.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Add tooltip for LEQ weighting
        if 'leq_cols' in param_docs:
            ToolTip(self.leq_cols_weighting, 
                   param_docs['leq_cols']['short'], 
                   param_docs['leq_cols']['full'])
        
        leq_frame.grid_columnconfigure(1, weight=1)
        
        # MAX_COLS section
        max_frame = ttk.LabelFrame(self.params_frame, text="MAX Columns", padding="10")
        max_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        ttk.Label(max_frame, text="Measurement:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.max_cols_measurement = ttk.Entry(max_frame, width=12)
        self.max_cols_measurement.insert(0, "Lmax")
        self.max_cols_measurement.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Add tooltip for MAX measurement
        if 'max_cols' in param_docs:
            ToolTip(self.max_cols_measurement, 
                   param_docs['max_cols']['short'], 
                   param_docs['max_cols']['full'])
        
        ttk.Label(max_frame, text="Weighting:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.max_cols_weighting = ttk.Entry(max_frame, width=12)
        self.max_cols_weighting.insert(0, "A")
        self.max_cols_weighting.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Add tooltip for MAX weighting
        if 'max_cols' in param_docs:
            ToolTip(self.max_cols_weighting, 
                   param_docs['max_cols']['short'], 
                   param_docs['max_cols']['full'])
        
        max_frame.grid_columnconfigure(1, weight=1)
        
        # LMAX_N section
        lmax_n_frame = ttk.LabelFrame(self.params_frame, text="Lmax N", padding="10")
        lmax_n_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        ttk.Label(lmax_n_frame, text="nth highest:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.lmax_n_entry = ttk.Entry(lmax_n_frame, width=12)
        self.lmax_n_entry.insert(0, "10")
        self.lmax_n_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Add tooltip for LMAX_N
        if 'lmax_n' in param_docs:
            ToolTip(self.lmax_n_entry, 
                   param_docs['lmax_n']['short'], 
                   param_docs['lmax_n']['full'])
        
        lmax_n_frame.grid_columnconfigure(1, weight=1)
        
        # LMAX_T section
        lmax_t_frame = ttk.LabelFrame(self.params_frame, text="Lmax T", padding="10")
        lmax_t_frame.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        ttk.Label(lmax_t_frame, text="Time period:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Create a frame for the time input and "min" label
        time_input_frame = ttk.Frame(lmax_t_frame)
        time_input_frame.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        self.lmax_t_entry = ttk.Entry(time_input_frame, width=8)
        self.lmax_t_entry.insert(0, "2")
        self.lmax_t_entry.pack(side="left", fill="x", expand=True)
        
        # Add tooltip for LMAX_T
        if 'lmax_t' in param_docs:
            ToolTip(self.lmax_t_entry, 
                   param_docs['lmax_t']['short'], 
                   param_docs['lmax_t']['full'])
        
        ttk.Label(time_input_frame, text="min").pack(side="left", padx=(3, 0))
        
        lmax_t_frame.grid_columnconfigure(1, weight=1)
        
        # Initially hide parameters (will be shown when resi_summary is selected)
        self.params_frame.grid_remove()
        
        # Show parameters if resi_summary is already selected
        if self.analysis_var.get() == "resi_summary":
            self.params_frame.grid()
    
    def get_resi_summary_docstring_info(self):
        """Extract parameter information from resi_summary docstring"""
        try:
            docstring = inspect.getdoc(self.survey.resi_summary)
            if not docstring:
                return {}
            
            # Extract parameter information from docstring
            param_info = {
                'leq_cols': {
                    'short': 'List of tuples for Leq calculations',
                    'full': 'List of tuples. The columns on which to perform Leq calculations. This can include L90 columns, or spectral values. e.g. leq_cols = [("Leq", "A"), ("L90", "125")]'
                },
                'max_cols': {
                    'short': 'List of tuples for nth-highest values',
                    'full': 'List of tuples. The columns on which to get the nth-highest values. Default max_cols = [("Lmax", "A")]'
                },
                'lmax_n': {
                    'short': 'The nth-highest value (default: 10)',
                    'full': 'Int. The nth-highest value for max_cols. Default 10 for 10th-highest.'
                },
                'lmax_t': {
                    'short': 'Time period for Lmax computation (e.g., "2min")',
                    'full': 'String. This is the time period over which to compute nth-highest Lmax values. e.g. "2min" computes the nth-highest Lmaxes over 2-minute periods. Note that the chosen period must be equal to or more than the measurement period. So you cannot measure in 5-minute periods and request 2-minute Lmaxes.'
                }
            }
            
            # Add full docstring context
            full_docstring = f"resi_summary() Method Documentation:\n\n{docstring}"
            for param in param_info:
                param_info[param]['full'] = f"{full_docstring}\n\nParameter Details:\n{param_info[param]['full']}"
            
            return param_info
        except:
            return {}

    def show_function_description(self):
        """Show a popup window with the docstring for the currently selected analysis function."""
        analysis_type = self.analysis_var.get()
        
        # Get the docstring from the survey module
        try:
            from pycoustic.survey import Survey
            survey_instance = Survey()
            
            if hasattr(survey_instance, analysis_type):
                method = getattr(survey_instance, analysis_type)
                docstring = method.__doc__ or "No documentation available for this function."
            else:
                docstring = f"Function '{analysis_type}' not found in the Survey class."
                
        except ImportError:
            docstring = "Could not import Survey class to retrieve documentation."
        except Exception as e:
            docstring = f"Error retrieving documentation: {str(e)}"
        
        # Create popup window
        popup = tk.Toplevel(self)
        popup.title(f"Function Description: {analysis_type}")
        popup.geometry("600x400")
        popup.resizable(True, True)
        
        # Center the popup on the main window
        popup.transient(self)
        popup.grab_set()
        
        # Create scrollable text widget
        frame = ttk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert the docstring
        text_widget.insert(tk.END, docstring)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Add close button
        close_button = ttk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=5)
        
        # Focus on the popup
        popup.focus_set()

    # ...existing code...
        
if __name__ == "__main__":
    app = Application()
    app.mainloop()