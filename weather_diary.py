import tkinter as tk
from tkinter import ttk, messagebox, Menu
from tkcalendar import DateEntry
import json
import os

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x500")

        # Список для хранения записей (загружается из JSON)
        self.records = []
        self.filename = "weather_data.json"

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # --- Фрейм ввода ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись")
        input_frame.pack(pady=10, fill="x", padx=10)

        # Дата
        ttk.Label(input_frame, text="Дата:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.temp_entry = ttk.Entry(input_frame, width=12)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=5)

        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Осадки (Да/Нет)
        ttk.Label(input_frame, text="Осадки:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.rain_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Да", variable=self.rain_var).grid(row=3, column=1, padx=5, pady=5)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=3, pady=10)

        # --- Фрейм фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(pady=10, fill="x", padx=10)

        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date = DateEntry(filter_frame, width=12)
        self.filter_date.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по температуре (выше)
        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp = ttk.Entry(filter_frame, width=8)
        self.filter_temp.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10)

        # --- Таблица записей ---
        columns = ("date", "temp", "desc", "rain")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("rain", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temp", width=120)
        self.tree.column("desc", width=300)
        self.tree.column("rain", width=80)
        
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

    def add_record(self):
        """Добавляет новую запись после валидации."""
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        
        try:
            temp = float(self.temp_entry.get())
            if temp < -100 or temp > 100:
                raise ValueError("Температура вне диапазона.")
            description = self.desc_entry.get().strip()
            if not description:
                raise ValueError("Описание не может быть пустым.")
            rain = "Да" if self.rain_var.get() else "Нет"
            
            record = {"date": date, "temp": temp, "desc": description, "rain": rain}
            self.records.append(record)
            self.update_table()
            self.save_data()
            
            # Очистка полей после добавления
            self.temp_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.rain_var.set(False)
            
            messagebox.showinfo("Успех", "Запись добавлена!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def update_table(self):
        """Обновляет таблицу Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for rec in self.records:
            self.tree.insert("", tk.END, values=(rec["date"], rec["temp"], rec["desc"], rec["rain"]))

    def apply_filter(self):
        """Фильтрует записи по дате и/или температуре."""
        filtered_records = self.records.copy()
        
        filter_date_str = self.filter_date.get_date().strftime("%Y-%m-%d")
        
        try:
            filter_temp_val = float(self.filter_temp.get())
            filtered_records = [r for r in filtered_records if r["temp"] > filter_temp_val]
            
            filtered_records = [r for r in filtered_records if r["date"] == filter_date_str]
            
            self.update_table_with_list(filtered_records)
            
            if not filtered_records:
                messagebox.showinfo("Фильтр", "Нет записей по заданным критериям.")
                
            self.filter_temp.delete(0, tk.END)  # Сброс поля температуры

        except ValueError:
            # Если температура не введена — фильтруем только по дате
            filtered_records = [r for r in filtered_records if r["date"] == filter_date_str]
            self.update_table_with_list(filtered_records)
            
    def update_table_with_list(self, record_list):
        """Обновляет таблицу из переданного списка."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for rec in record_list:
            self.tree.insert("", tk.END, values=(rec["date"], rec["temp"], rec["desc"], rec["rain"]))

    def save_data(self):
        """Сохраняет записи в JSON."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

    def load_data(self):
        """Загружает записи из JSON."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
                self.update_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
