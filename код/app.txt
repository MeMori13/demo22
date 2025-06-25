import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from logic import ProductManager


class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Наш декор")
        self.root.geometry("1000x600")

        self.root.iconbitmap("Наш декор.ico")  # Replace with your icon file path

        self.db = Database()
        self.manager = ProductManager(self.db)

        self.product_frames = []  # To keep track of product frames for updates
        self._setup_ui()
        self._load_products()

    def _setup_ui(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Добавить", command=self._add_product).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Обновить", command=self._load_products).pack(side=tk.LEFT, padx=5)

        # Контейнер с канвасом и скроллбаром
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.products_container = tk.Frame(self.canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Помещаем контейнер в канвас
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.products_container, anchor=tk.NW)

        # Настраиваем скроллбар и канвас
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Обновляем размер канваса при изменении размеров контейнера
        self.products_container.bind("<Configure>",
                                     lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))

    def _load_products(self):
        for frame in self.product_frames:
            frame.destroy()
        self.product_frames.clear()

        products = self.manager.get_all_products()
        for product in products:
            # Создание фрейма для каждого продукта с серым фоном и увеличенным размером
            product_frame = tk.Frame(self.products_container, bd=1, relief=tk.SOLID, bg="#f0f0f0", padx=10, pady=10,
                                     height=140)
            product_frame.pack(fill=tk.X, pady=10, padx=5)

            # Настройка grid для двух колонок
            product_frame.grid_columnconfigure(0, weight=1)  # Левая колонка для текста
            product_frame.grid_columnconfigure(1, weight=0)  # Правая колонка для чисел

            # Метки для отображения данных в вертикальном порядке с шрифтом Gabriola
            tk.Label(product_frame, text=f"{product['type_name']} | {product['name']}",
                     font=("Gabriola", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W)

            # Артикул на одной строке, без перекрытия
            articulo_label = tk.Label(product_frame, text="Артикул:", font=("Gabriola", 14, "bold"))
            articulo_label.grid(row=1, column=0, sticky=tk.W, pady=2)
            tk.Label(product_frame, text=product['article'], font=("Gabriola", 14)).grid(row=1, column=1, sticky=tk.W,
                                                                                         pady=2)

            # Стоимость и ширина с числами справа
            tk.Label(product_frame, text="Минимальная стоимость для партнера (р):", font=("Gabriola", 14, "bold")).grid(
                row=2, column=0, sticky=tk.W, pady=2)
            tk.Label(product_frame, text=f"{product['min_price']:.2f}", font=("Gabriola", 14)).grid(row=2, column=1,
                                                                                                    sticky=tk.E, pady=2)

            tk.Label(product_frame, text="Ширина (м):", font=("Gabriola", 14, "bold")).grid(row=3, column=0,
                                                                                            sticky=tk.W, pady=2)
            tk.Label(product_frame, text=f"{product['width']:.2f}", font=("Gabriola", 14)).grid(row=3, column=1,
                                                                                                sticky=tk.E, pady=2)

            # Bind double-click event to the product frame
            product_frame.bind("<Double-1>", lambda event, p=product: self._edit_product(p))

            self.product_frames.append(product_frame)

    def _add_product(self):
        """Открывает форму добавления продукта"""
        self.root.title("Добавление продукта")  # Change the title when adding a product
        form = ProductForm(self.root, self.db, self.manager, self._load_products)

    def _edit_product(self, product):
        """Открывает форму редактирования продукта"""
        self.root.title("Редактирование продукта")  # Change the title when editing a product
        form = ProductForm(self.root, self.db, self.manager, self._load_products, product)


class ProductForm(tk.Toplevel):
    def __init__(self, parent, db, manager, callback, product=None):
        super().__init__(parent)
        self.db = db
        self.manager = manager
        self.callback = callback
        self.product = product

        self.title("Добавить продукт" if not product else "Редактировать продукт")
        self.geometry("400x300")

        self._setup_ui()
        if product:
            self._load_data()

    def _setup_ui(self):
        """Настраивает форму"""
        ttk.Label(self, text="Артикул:", font=("Gabriola", 14)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.article_entry = ttk.Entry(self, font=("Gabriola", 14))
        self.article_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(self, text="Наименование:", font=("Gabriola", 14)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self, font=("Gabriola", 14))
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(self, text="Тип:", font=("Gabriola", 14)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.type_combobox = ttk.Combobox(self, font=("Gabriola", 14))
        self.type_combobox.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        types = self.db.fetch_all("SELECT name FROM product_types")
        self.type_combobox['values'] = [t['name'] for t in types]

        ttk.Label(self, text="Мин. цена:", font=("Gabriola", 14)).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.price_entry = ttk.Entry(self, font=("Gabriola", 14))
        self.price_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(self, text="Ширина:", font=("Gabriola", 14)).grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.width_entry = ttk.Entry(self, font=("Gabriola", 14))
        self.width_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT)

    def _load_data(self):
        """Загружает данные продукта в форму"""
        self.article_entry.insert(0, self.product['article'])
        self.name_entry.insert(0, self.product['name'])
        self.price_entry.insert(0, str(self.product['min_price']))
        self.width_entry.insert(0, str(self.product['width']))

        type_name = self.db.fetch_one(
            "SELECT name FROM product_types WHERE id = ?",
            (self.product['type_id'],)
        )['name']
        self.type_combobox.set(type_name)

    def _save(self):
        """Сохраняет продукт"""
        try:
            article = self.article_entry.get()
            name = self.name_entry.get()
            type_name = self.type_combobox.get()
            price = float(self.price_entry.get())
            width = float(self.width_entry.get())

            # Validate that price and width are not negative
            if price < 0:
                messagebox.showerror("Ошибка", "Минимальная цена не может быть отрицательной.")
                return
            if width < 0:
                messagebox.showerror("Ошибка", "Ширина не может быть отрицательной.")
                return

            type_id = self.db.fetch_one(
                "SELECT id FROM product_types WHERE name = ?",
                (type_name,)
            )['id']

            if self.product:
                self.manager.update_product(
                    self.product['id'], name, type_id, price, width
                )
                messagebox.showinfo("Успех", "Продукт обновлен")
            else:
                self.manager.add_product(article, name, type_id, price, width)
                messagebox.showinfo("Успех", "Продукт добавлен")

            self.callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperApp(root)
    root.mainloop()
