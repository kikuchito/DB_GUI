from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import psycopg2

DB_NAME = "fpga_ip_database"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

primary_keys = {
    "fpga_ip_cores": "core_id",
    "fpga_ip_versions": "version_id",
    "fpga_ip_features": "feature_id",
    "fpga_ip_developers": "developer_id",
    "fpga_projects": "project_id",
    "project_ip_assignments": "assignment_id"
}

column_names = {
    "fpga_ip_cores": ["core_id", "core_name", "type", "version", "vendor", "description"],
    "fpga_ip_versions": ["version_id", "core_id", "version_number", "release_date", "compatible_fpga", "notes"],
    "fpga_ip_features": ["feature_id", "core_id", "feature_name", "feature_type", "details"],
    "fpga_ip_developers": ["developer_id", "core_id", "first_name", "last_name", "email", "specialization"],
    "fpga_projects": ["project_id", "project_name", "description", "start_date", "end_date", "status"],
    "project_ip_assignments": ["assignment_id", "project_id", "core_id", "assigned_date", "status"]
}

def load_data():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = f"SELECT * FROM {table_var.get()}"
        filter_value = filter_var.get()
        if filter_value:  
            try:
                int(filter_value)
                query += f" WHERE {filter_column_var.get()} = %s"
                cursor.execute(query, (filter_value,))
            except ValueError:
                query += f" WHERE {filter_column_var.get()} ILIKE %s"
                cursor.execute(query, (f"%{filter_value}%",))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        clear_table()
        for row in rows:
            tree.insert("", END, values=row)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        conn.close()

def clear_table():
    for item in tree.get_children():
        tree.delete(item)

def clear_entries():
    for entry in entries:
        entry.delete(0, END)

def update_record():
    selected = tree.focus()
    values = tree.item(selected, "values")
    if not values:
        messagebox.showwarning("Предупреждение", "Выберите запись для обновления.")
        return
    table = table_var.get()
    data = [entry.get() for entry in entries]
    if any(not value.strip() for value in data):  
       messagebox.showwarning("Предупреждение", "Все поля должны быть заполнены.")
       return
    key_column = primary_keys[table]
    query = f"UPDATE {table} SET {', '.join(f'{col} = %s' for col in column_names[table])} WHERE {key_column} = %s"
    try:
        execute_query(query, tuple(data + [values[0]]))
        messagebox.showinfo("Успех", "Запись обновлена!")
        clear_entries()
        load_data()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def delete_record():
    selected = tree.focus()
    values = tree.item(selected, "values")
    if not values:
        messagebox.showwarning("Предупреждение", "Выберите запись для удаления.")
        return
    table = table_var.get()
    key_column = primary_keys[table]
    query = f"DELETE FROM {table} WHERE {key_column} = %s"
    execute_query(query, (values[0],))
    messagebox.showinfo("Успех", "Запись удалена!")
    load_data()

def add_record():
    table = table_var.get()
    data = [entry.get() for entry in entries]
    if any(not value.strip() for value in data):  
        messagebox.showwarning("Предупреждение", "Все поля должны быть заполнены.")
        return
    query = f"INSERT INTO {table} ({', '.join(column_names[table])}) VALUES ({', '.join('%s' for _ in data)})"
    try:
        execute_query(query, tuple(data))
        messagebox.showinfo("Успех", "Запись добавлена!")
        clear_entries()
        load_data()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def execute_query(query, params=()):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        conn.close()

def update_columns(*args):
    table = table_var.get()
    columns = column_names[table]

    tree["columns"] = columns
    for col in columns:
        tree.heading(col, text=col)

    for widget in fields_frame.winfo_children():
        widget.destroy()
    entries.clear()
    for col in columns:
        lbl = Label(fields_frame, text=col)
        lbl.pack(side=LEFT)
        ent = Entry(fields_frame)
        ent.pack(side=LEFT)
        entries.append(ent)

    filter_column_var.set(columns[0])  
    menu = filter_column_menu["menu"]
    menu.delete(0, "end")  
    for col in columns:
        menu.add_command(label=col, command=lambda value=col: filter_column_var.set(value))

    load_data()

# Соединение функций с GUI...................................................................

root = Tk()
root.title("IP-ядра")

# Список выбора таблицы
table_var = StringVar(value="fpga_ip_cores")
table_var.trace("w", update_columns)
table_menu = ttk.OptionMenu(root, table_var, table_var.get(), *primary_keys.keys())
table_menu.pack(pady=10)

# Кнопка фильтрации
filter_frame = Frame(root)
filter_frame.pack(pady=10)
filter_var = StringVar()
filter_column_var = StringVar()
filter_column_var.set("core_name")
filter_label = Label(filter_frame, text="Фильтр:")
filter_label.pack(side=LEFT)
filter_entry = Entry(filter_frame, textvariable=filter_var)
filter_entry.pack(side=LEFT, padx=5)
filter_column_menu = ttk.OptionMenu(filter_frame, filter_column_var, filter_column_var.get(), *column_names[table_var.get()])
filter_column_menu.pack(side=LEFT, padx=5)
filter_btn = Button(filter_frame, text="Применить фильтр", command=load_data)
filter_btn.pack(side=LEFT, padx=5)

# Общая таблица
tree = ttk.Treeview(root, columns=[], show="headings")
tree.pack(pady=10, fill=BOTH, expand=True)

# Поля для записи
fields_frame = Frame(root)
fields_frame.pack(pady=10)
entries = []

# Кнопки для работы с БД
buttons_frame = Frame(root)
buttons_frame.pack(pady=10)
btn_add = Button(buttons_frame, text="Добавить запись", command=add_record)
btn_add.pack(side=LEFT, padx=5)
btn_update = Button(buttons_frame, text="Обновить запись", command=update_record)
btn_update.pack(side=LEFT, padx=5)
btn_delete = Button(buttons_frame, text="Удалить запись", command=delete_record)
btn_delete.pack(side=LEFT, padx=5)

# Init
update_columns()
root.mainloop()
