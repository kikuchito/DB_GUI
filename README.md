# DB_GUI

### Подключение библиотек, с помощью которых реализуется подключение к 	базеданных и графический интерфейс
```python
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import psycopg2
```
#
### Эта функция создает и возвращает соединение с базой данных PostgreSQL с 	использованием библиотеки psycopg2. Параметры подключения (имя базы данных, 	пользователь, пароль, хост и порт) заданы как переменные.

```python
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
```
#
### 1. Переменная primary_keys это словарь, где ключами являются имена таблиц 	базы данных, а значениями имена столбцов, которые являются первичными 	ключами для этих таблиц.

### 2. Переменная column_names это так же словарь, в котором ключи  это имена 	таблиц, а значения  списки строк, представляющие имена столбцов каждой 	таблицы. 	Этот словарь используется для отображения всех столбцов данных таблицы в GUI, а 	также для работы с фильтрацией и отображением данных.

```python
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
```
#

### Эта функция загружает данные из выбранной таблицы в базе данных и отображает их 	в графическом интерфейсе (в Treeview). Она поддерживает фильтрацию записей по 	выбранной колонке. Если фильтр задан, функция проверяет, является ли он числом 	(для различных id), и применяет соответствующий SQL-запрос (ILIKE для строк, = 	для чисел). После выполнения запроса данные загружаются в Treeview, 	предварительно очистив его.

```python
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
```
#

### Эта функция очищает все текущие данные в Treeview перед загрузкой новых. Вызов 	tree.delete(item) удаляет каждую запись из таблицы (Не из БД, а с 	интерфейса).

```python
def clear_table():
    for item in tree.get_children():
        tree.delete(item)
```
#
### Функция очищает все поля ввода (виджеты Entry), сбрасывая их значения. То есть 	если поля заполнены, после нажатия кнопки, они будут сброшены.
```python
def clear_entries():
    for entry in entries:
        entry.delete(0, END)
```
#
### Эта функция обновляет выбранную запись в базе данных. Для этого она проверяет, 	была ли выбрана запись в Treeview, извлекает данные из полей ввода, и формирует 	SQL-запрос для обновления записи в выбранной таблице. Если все поля заполнены, 	выполняется запрос обновления, после чего отображается сообщение об успешном 	обновлении.
```python
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
```
#
### Эта функция удаляет выбранную запись из базы данных. После того как запись 	выбрана в Treeview, создается SQL-запрос для удаления записи по её первичному 	ключу. После удаления данных вызывается load_data(), чтобы обновить 	отображаемую таблицу.
```python
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
```
#
### Эта функция добавляет новую запись в выбранную таблицу. Сначала проверяются 	значения всех полей ввода, затем создается SQL-запрос на вставку новых данных в 	таблицу. После успешного добавления записи, вызываются функции для очистки 	полей ввода и перезагрузки данных в Treeview.
```python
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
```
#
### Эта функция выполняет SQL-запрос с переданными параметрами. Она подключается 	к базе данных, выполняет запрос и подтверждает изменения с помощью commit(). В 	случае ошибки выводится сообщение об ошибке.
```python
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
```
#
### Эта функция обновляет интерфейс в зависимости от выбранной таблицы. Она 	обновляет список колонок в Treeview, очищает и создает новые поля ввода для 	редактирования, а также обновляет список доступных колонок для фильтрации.
```python
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
```
#
### Создаётся основное окно приложения с помощью Tk(). Это окно будет служить 	контейнером для всех виджетов. Название окна устанавливается с помощью 	root.title().
```python
root = Tk()
root.title("IP-ядра")
```
#
### table_var = StringVar(value="fpga_ip_cores") — создаётся переменная 	для хранения выбранной таблицы. По умолчанию это fpga_ip_cores.
### table_var.trace("w", update_columns) — устанавливает отслеживание 	изменений этой переменной. Каждый раз, когда значение в table_var изменяется, 	вызывается функция update_columns.
### table_menu = ttk.OptionMenu(...) — создаётся выпадающее меню для 	выбора таблицы. В качестве возможных значений для меню используются ключи из 	словаря primary_keys.
### table_menu.pack(pady=10) — добавляет это меню на экран, с отступом по 	вертикали.
```python
table_var = StringVar(value="fpga_ip_cores")
table_var.trace("w", update_columns)
table_menu = ttk.OptionMenu(root, table_var, table_var.get(), *primary_keys.keys())
table_menu.pack(pady=10)
```
#
### filter_frame = Frame(root) — создаётся контейнер для элементов 	фильтрации.
### filter_var = StringVar() — переменная для хранения введённого значения фильтра.
### filter_column_var = StringVar() — переменная для выбора столбца, по которому будет происходить фильтрация.
### filter_column_var.set("core_name") — устанавливается значение по умолчанию для фильтрации  (core_name).
### filter_label = Label(...) — метка с текстом "Фильтр:", поясняющая, что это поле для фильтрации.
### filter_entry = Entry(...) — поле ввода для текста фильтра.
### filter_column_menu = ttk.OptionMenu(...) — выпадающее меню для выбора столбца, по которому будет фильтроваться.
### filter_btn = Button(...) — кнопка, при нажатии на которую вызывается функция load_data. Эта функция загружает данные с применённым фильтром.
```python
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
```
#
### tree = ttk.Treeview(...) — создаётся виджет для отображения данных в 	табличном виде. Он будет отображать данные, загруженные из базы данных.
### tree.pack(pady=10, fill=BOTH, expand=True) — размещает таблицу в окне и настраивает её размеры.
```python
tree = ttk.Treeview(root, columns=[], show="headings")
tree.pack(pady=10, fill=BOTH, expand=True)
```
#
### fields_frame = Frame(root) — создаётся контейнер для полей ввода.
### entries = [] — список для хранения полей ввода для редактирования данных.
```python
fields_frame = Frame(root)
fields_frame.pack(pady=10)
entries = []
```
#
### Добавить запись: вызывает функцию add_record для добавления новой записи 	в таблицу.
### Обновить запись: вызывает функцию update_record для обновления выбранной записи.
### Удалить запись: вызывает функцию delete_record для удаления выбранной записи.
```python
buttons_frame = Frame(root)
buttons_frame.pack(pady=10)
btn_add = Button(buttons_frame, text="Добавить запись", command=add_record)
btn_add.pack(side=LEFT, padx=5)
btn_update = Button(buttons_frame, text="Обновить запись", command=update_record)
btn_update.pack(side=LEFT, padx=5)
btn_delete = Button(buttons_frame, text="Удалить запись", command=delete_record)
btn_delete.pack(side=LEFT, padx=5)
```
#
### update_columns() — функция, которая обновляет отображаемые данные в 	зависимости от выбранной таблицы. Она вызывается при запуске приложения, 	чтобы сразу загрузить данные для выбранной таблицы.
### root.mainloop() — запускает главный цикл обработки событий. Это необходимый шаг для работы GUI, чтобы приложение ожидало взаимодействия с пользователем.
```python
update_columns()
root.mainloop()
```
