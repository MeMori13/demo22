import openpyxl
from database import Database

def import_products(db):
    """Импортирует продукты из Excel"""
    wb = openpyxl.load_workbook('data/Products_import.xlsx')
    sheet = wb.active
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        type_name, name, article, min_price, width = row
        
        # Получаем или создаем тип продукта
        type_id = db.fetch_one(
            "SELECT id FROM product_types WHERE name = ?", 
            (type_name,)
        )
        if not type_id:
            db.execute(
                "INSERT INTO product_types (name, coefficient) VALUES (?, 1.0)",
                (type_name,)
            )
            type_id = db.fetch_one(
                "SELECT id FROM product_types WHERE name = ?", 
                (type_name,)
            )
        
        # Добавляем продукт
        db.execute(
            """INSERT OR IGNORE INTO products 
            (article, name, type_id, min_price, width)
            VALUES (?, ?, ?, ?, ?)""",
            (article, name, type_id['id'], min_price, width)
        )

def import_materials(db):
    """Импортирует материалы из Excel"""
    wb = openpyxl.load_workbook('data/Materials_import.xlsx')
    sheet = wb.active
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        name, type_name, price, stock, min_qty, pkg_qty, unit = row
        
        db.execute(
            """INSERT OR IGNORE INTO materials 
            (name, type, price, unit)
            VALUES (?, ?, ?, ?)""",
            (name, type_name, price, unit)
        )

def import_product_materials(db):
    """Импортирует состав продукции"""
    wb = openpyxl.load_workbook('data/Product_materials_import.xlsx')
    sheet = wb.active
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        product_name, material_name, quantity = row
        
        product = db.fetch_one(
            "SELECT id FROM products WHERE name = ?", 
            (product_name,)
        )
        material = db.fetch_one(
            "SELECT id FROM materials WHERE name = ?", 
            (material_name,)
        )
        
        if product and material:
            db.execute(
                """INSERT OR REPLACE INTO product_materials 
                (product_id, material_id, quantity)
                VALUES (?, ?, ?)""",
                (product['id'], material['id'], quantity)
            )

if __name__ == "__main__":
    db = Database()
    
    print("Импорт типов продукции...")
    import_products(db)
    
    print("Импорт материалов...")
    import_materials(db)
    
    print("Импорт состава продукции...")
    import_product_materials(db)
    
    print("Импорт завершен успешно!")
    db.close()