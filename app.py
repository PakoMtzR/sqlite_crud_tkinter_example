import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

class App(tk.Tk):

    # Nombre de nuestra base de datos
    database = "database.db"

    def __init__(self):
        super().__init__()
        self.geometry("360x420")
        self.resizable(False, False)
        self.title("SQL App")

        #self.tk.call("source", "azure.tcl")
        #self.tk.call("set_theme", "light")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.create_widgets()   # Creamos los widgets de la app
        self.create_table()     # En caso de no existir la tabla "Alumnos", entonces la creamos
        self.get_students()     # Actualizamos la tabla

    def create_widgets(self):
        # Creamos frame para el formulario
        self.form = ttk.LabelFrame(master=self, text="Formulario")
        self.form.grid(column=0, row=0, columnspan=2, sticky="nesw", padx=10, pady=10)

        self.form.columnconfigure(0, weight=0)
        self.form.columnconfigure(1, weight=1)

        # Labels del formulario
        ttk.Label(master=self.form, text="Nombre:").grid(column=0, row=0, padx=10, pady=5, sticky="e")
        ttk.Label(master=self.form, text="Edad:").grid(column=0, row=1, padx=10, pady=5, sticky="e")

        # Creamos los campos de entrada
        self.entry_name = ttk.Entry(master=self.form)
        self.entry_name.grid(column=1, row=0, sticky="nesw", padx=10, pady=10)
        self.entry_age = ttk.Spinbox(master=self.form, from_=0, to=100)
        self.entry_age.grid(column=1, row=1, sticky="nesw", padx=10, pady=10)
        
        # Label para mensajes 
        self.label_message = ttk.Label(master=self.form, text="")
        self.label_message.grid(column=0, row=3, columnspan=2, padx=10, pady=10)
        
        # Creamos la tabla para visualisar los datos de la DB
        self.table = ttk.Treeview(master=self, height=6, columns=2)
        self.table.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        self.table.heading("#0", text="Nombre", anchor="w")
        self.table.heading("#1", text="Edad", anchor="w")   # center

        # Creamos los botones
        ttk.Button(master=self.form, text="GUARDAR", command=self.add_student).grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        ttk.Button(master=self, text="ELIMINAR", command=self.delete_student).grid(column=0, row=3, padx=10, pady=10, sticky="we")
        ttk.Button(master=self, text="EDITAR", command=self.open_edit_window).grid(column=1, row=3, padx=10, pady=10, sticky="we")

    # Funcion que nos permite correr los querys
    def run_query(self, query, parameters=()):
        try:
            with sqlite3.connect(self.database) as connector:
                cursor = connector.cursor()
                result = cursor.execute(query, parameters)
                connector.commit()
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Exception in _query: {e}")
    
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS Alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )"""
        self.run_query(query)

    def get_students(self):
        query = "SELECT * FROM Alumnos"
        db_rows = self.run_query(query)

        # Limpiamos la tabla
        table_rows = self.table.get_children()
        for element in table_rows:
            self.table.delete(element)

        # Insertar datos de la DB en la tabla
        for row in db_rows:
            self.table.insert("", 0, text=row[1], values=row[2])

    def validate_form(self):
        name = self.entry_name.get()
        age = self.entry_age.get()

        if not name:
            self.label_message["text"] = "El campo de nombre no puede estar vacío"
            return False

        try:
            int(age)
        except ValueError:
            self.label_message["text"] = "La edad debe ser un número entero"
            return False

        return True

    def add_student(self):
        if  self.validate_form():
            query = "INSERT INTO Alumnos VALUES(NULL, ?, ?)"
            parameters = (self.entry_name.get().upper(), self.entry_age.get())
            self.run_query(query, parameters)

            # Mostramos mensaje de que se ha agregago el alumno
            self.label_message["text"] = f"{self.entry_name.get()} fue agregad@"

            # Limpiamos los campos del formulario
            self.entry_name.delete(0, tk.END)
            self.entry_age.delete(0, tk.END)
        
        # Actualizamos la tabla
        self.get_students()

    def delete_student(self):
        row_selected = self.table.item(self.table.selection())
        if not row_selected["text"]:
            self.label_message['text'] = "Seleccione un registro"
        else:
            name = row_selected["text"]
            age = row_selected["values"][0]

            if messagebox.askokcancel("Eliminar Registro", f"¿Estas segur@ de eliminar a {name} de la BD?"):
                query = "DELETE FROM Alumnos WHERE nombre = ? AND edad = ?"
                self.run_query(query, (name, age))
                self.label_message['text'] = f"{name} ha sido eliminad@ de la BD"
                self.get_students()

    def open_edit_window(self):
        row_selected = self.table.item(self.table.selection())
        if not row_selected["text"]:
            self.label_message['text'] = "Seleccione un registro"
        else:
            old_name = row_selected["text"]
            old_age = row_selected["values"][0]

            # Creamos la ventana para editar el registro
            self.edit_window = tk.Toplevel()
            self.edit_window.title("Editar Registro")
            self.edit_window.geometry("360x160")
            self.edit_window.resizable(False, False)
            self.edit_window.columnconfigure(0, weight=0)
            self.edit_window.columnconfigure(1, weight=1)

            # Creamos los labels
            ttk.Label(master=self.edit_window, text="Nombre:").grid(column=0, row=0, padx=10, pady=5, sticky="e")
            ttk.Label(master=self.edit_window, text="Edad:").grid(column=0, row=1, padx=10, pady=5, sticky="e")

            # Creamos los campos de entrada
            self.entry_new_name = ttk.Entry(master=self.edit_window)
            self.entry_new_name.grid(column=1, row=0, sticky="nesw", padx=10, pady=10)
            self.entry_new_name.insert(0, old_name)
            self.entry_new_age = ttk.Spinbox(master=self.edit_window, from_=0, to=100)
            self.entry_new_age.grid(column=1, row=1, sticky="nesw", padx=10, pady=10)
            self.entry_new_age.insert(0, old_age)

            ttk.Button(master=self.edit_window, text="Editar", command= lambda: self.edit_student_info(old_name, old_age)).grid(column=0, row=2, columnspan=2, padx=10, pady=10)
            
    def edit_student_info(self, old_name, old_age):
        new_name = self.entry_new_name.get()
        new_age = self.entry_new_age.get()

        query = "UPDATE Alumnos SET nombre = ?, edad = ? WHERE nombre = ? AND edad = ?"
        self.run_query(query, (new_name, new_age, old_name, old_age))
        self.edit_window.destroy()
        self.get_students()
        return

if __name__ == "__main__":
    app = App()
    app.mainloop()