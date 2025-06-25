from database import Database

class ProductManager:
    def __init__(self, db):
        self.db = db

    def get_all_products(self):
        """Возвращает список всей продукции"""
        query = """
        SELECT p.*, pt.name as type_name, pt.coefficient 
        FROM products p
        JOIN product_types pt ON p.type_id = pt.id
        """
        return self.db.fetch_all(query)

    def get_product_materials(self, product_id):
        """Возвращает материалы для продукта"""
        query = """
        SELECT m.*, pm.quantity 
        FROM product_materials pm
        JOIN materials m ON pm.material_id = m.id
        WHERE pm.product_id = ?
        """
        return self.db.fetch_all(query, (product_id,))

    def calculate_product_cost(self, product_id):
        """Рассчитывает стоимость продукта"""
        materials = self.get_product_materials(product_id)
        product = self.db.fetch_one("""
            SELECT p.*, pt.coefficient 
            FROM products p
            JOIN product_types pt ON p.type_id = pt.id
            WHERE p.id = ?
        """, (product_id,))
        
        if not product or not materials:
            return 0.0
        
        total = 0.0
        for material in materials:
            total += material['price'] * material['quantity']
        
        return round(total * product['coefficient'], 2)

    def add_product(self, article, name, type_id, min_price, width):
        """Добавляет новый продукт"""
        query = """
        INSERT INTO products (article, name, type_id, min_price, width)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute(query, (article, name, type_id, min_price, width))
        return True

    def update_product(self, product_id, name, type_id, min_price, width):
        """Обновляет данные продукта"""
        query = """
        UPDATE products 
        SET name = ?, type_id = ?, min_price = ?, width = ?
        WHERE id = ?
        """
        self.db.execute(query, (name, type_id, min_price, width, product_id))
        return True