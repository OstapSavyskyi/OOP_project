from datetime import date, datetime
import json
import time
import ast

class Product:
    def __init__(self, name, description, price, quantity, manufacture_date, expiry_date, category):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.manufacture_date = manufacture_date
        self.expiry_date = expiry_date
        self.category = category
        self.sales = []

    def update_price(self, new_price):
        self.price = new_price

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

class InventoryManagementSystem:
    def __init__(self):
        self.products = []
        self.language = 'en'

    def set_language(self, language):
        self.language = language
        print(f"Language set to {language}")

    def add_product(self, product):
        for existing_product in self.products:
            if existing_product.name == product.name and existing_product.category == product.category:
                existing_product.quantity += product.quantity
                break
        else:
            self.products.append(product)

    def remove_product(self, product_name):
        self.products = [p for p in self.products if p.name != product_name]

    def sell_product(self, product_name, quantity):
        for product in self.products:
            if product.name == product_name:
                if product.quantity >= quantity:
                    product.quantity -= quantity
                    sale_date_time = datetime.now().isoformat()
                    product.sales.append(Sale(sale_date_time, quantity))
                    return {"quantity": quantity, "product_name": product.name}
                else:
                    return None
        return None

    def update_product(self, product_name, new_quantity, new_price):
        for product in self.products:
            if product.name == product_name:
                product.update_quantity(new_quantity)
                product.update_price(new_price)
                return get_string('product_updated', self.language)
        return get_string('product_not_found', self.language)

    def parse_search_criteria(input_string):
        pattern = r"(\w+)=([\w\d]+)"
        matches = re.findall(pattern, input_string)
        criteria = {}
        for match in matches:
            key, value = match
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
            criteria[key] = value
        return criteria

    def generate_report(self, start_date, end_date):
        report = {}
        for product in self.products:
            if start_date <= product.expiry_date <= end_date:
                report[product.name] = product.quantity
        return report

    def generate_sales_report(self, start_date_time, end_date_time):
        report = {}
        start_date = datetime.fromisoformat(start_date_time)
        end_date = datetime.fromisoformat(end_date_time)

        for product in self.products:
            sales_quantity = 0
            for sale in product.sales:
                if isinstance(sale.date, str):
                    try:
                        sale_date = datetime.fromisoformat(sale.date)
                    except ValueError:
                        sale_date = datetime.strptime(sale.date, '%Y-%m-%d %H:%M:%S')
                elif isinstance(sale.date, datetime):
                    sale_date = sale.date
                else:
                    continue

                if start_date <= sale_date <= end_date:
                    sales_quantity += sale.quantity

            report[product.name] = {"Quantity": product.quantity, "Sales Quantity": sales_quantity}

        return report

    def sort_products_by_price(self):
        category_order = {"Fruit": 1, "Drinks": 2, "Sweets": 3, "Other": 4}
        self.products.sort(key=lambda x: (category_order.get(x.category, float('inf')), x.price))

    def sort_products_by_quantity(self):
        category_order = {"Fruit": 1, "Drinks": 2, "Sweets": 3, "Other": 4}
        self.products.sort(key=lambda x: (category_order.get(x.category, float('inf')), x.quantity))

    def sort_products_by_category(self):
        category_order = {"Fruit": 1, "Drinks": 2, "Sweets": 3, "Other": 4}
        self.products.sort(key=lambda x: category_order.get(x.category, float('inf')))

class Sale:
    def __init__(self, date, quantity):
        self.date = date
        self.quantity = quantity

def save_inventory_to_file(inventory, filename):
    def default(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    current_date_time = datetime.now().isoformat()

    data = {
        "products": [
            {
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "quantity": product.quantity,
                "manufacture_date": product.manufacture_date.isoformat() if isinstance(product.manufacture_date, (datetime, date)) else None,
                "expiry_date": product.expiry_date.isoformat() if isinstance(product.expiry_date, (datetime, date)) else None,
                "category": product.category,
                "sales": [
                    {
                        "date": current_date_time if sale.date is None else (sale.date.isoformat() if isinstance(sale.date, (datetime, date)) else sale.date),
                        "quantity": sale.quantity
                    }
                    for sale in product.sales
                ]
            }
            for product in inventory.products
        ]
    }

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, default=default, ensure_ascii=False)

def load_inventory_from_file(filename):
    today = date.today()
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            inventory = InventoryManagementSystem()
            for product_data in data['products']:
                expiry_date_str = product_data['expiry_date']
                expiry_date = datetime.fromisoformat(expiry_date_str)
                manufacture_date_str = product_data.get('manufacture_date', today.isoformat())
                manufacture_date = datetime.fromisoformat(manufacture_date_str)
                product = Product(product_data['name'], product_data['description'],
                                 product_data['price'], product_data['quantity'],
                                 manufacture_date.date(), expiry_date.date(), product_data['category'])
                if 'sales' in product_data:
                    for sale_data in product_data['sales']:
                        sale_date_str = sale_data.get('date', None)
                        if sale_date_str:
                            sale_date = datetime.fromisoformat(sale_date_str)
                            sale_quantity = sale_data['quantity']
                            product.sales.append(Sale(sale_date, sale_quantity))
                inventory.add_product(product)
            return inventory
    except FileNotFoundError:
        return InventoryManagementSystem()

def get_string(key, language='en'):
    return Strings[key][language]

Strings = {
    'product_added': {'en': 'Product added successfully.', 'uk': 'Продукт успішно додано.'},
    'product_removed': {'en': 'Product removed successfully.', 'uk': 'Продукт успішно видалено.'},
    'sold_product': {'en': 'Sold {quantity} units of {product_name}.', 'uk': 'Продано {quantity} одиниць {product_name}.'},
    'not_enough_quantity': {'en': 'Not enough quantity available for sale.', 'uk': 'Недостатньо кількості для продажу.'},
    'product_not_found': {'en': 'Product not found.', 'uk': 'Продукт не знайдено.'},
    'product_updated': {'en': 'Updated product {product_name} quantity and price.', 'uk': 'Оновлено кількість та ціну продукту {product_name}.'},
}

def main():
    inventory_filename = "inventory.json"
    inventory = load_inventory_from_file(inventory_filename)

    inventory.set_language('uk')

    while True:
        print("1. Add product")
        print("2. Remove product")
        print("3. Sell product")
        print("4. Update product")
        print("5. Search product")
        print("6. Generate report")
        print("7. Generate sales report")
        print("8. Sort products")
        print("9. Save and exit")
        command = input("Enter command: ")

        if command == '1':
            product_name = input("Enter product name: ")
            description = input("Enter product description: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            manufacture_date = input("Enter manufacture date (YYYY-MM-DD): ")
            expiry_date = input("Enter expiry date (YYYY-MM-DD): ")
            category = input("Enter product category: ")
            product = Product(product_name, description, price, quantity, datetime.strptime(manufacture_date, '%Y-%m-%d').date(), datetime.strptime(expiry_date, '%Y-%m-%d').date(), category)
            inventory.add_product(product)
            save_inventory_to_file(inventory, inventory_filename)
            print(get_string('product_added', inventory.language))

        elif command == '2':
            product_name = input("Enter product name: ")
            inventory.remove_product(product_name)
            save_inventory_to_file(inventory, inventory_filename)
            print(get_string('product_removed', inventory.language))

        elif command == '3':
            product_name = input("Enter product name: ")
            quantity = int(input("Enter quantity to sell: "))
            result = inventory.sell_product(product_name, quantity)
            if result:
                print(f"Продано {result['quantity']} одиниць {result['product_name']}.")
            else:
                print("Недостатньо кількості для продажу або продукт не знайдено.")


        elif command == '4':
            product_name = input("Enter product name: ")
            new_quantity = int(input("Enter new quantity: "))
            new_price = float(input("Enter new price: "))
            inventory.update_product(product_name, new_quantity, new_price)
            save_inventory_to_file(inventory, inventory_filename)
            print(get_string('product_updated', inventory.language))

        elif command == '5':
            print("Enter search criteria (e.g., 'Fruit', 'Apple'):")
            criteria_string = input("> ")
            try:
                criteria_string = criteria_string.lower()
                results = []
                for product in inventory.products:
                    if criteria_string in product.name.lower() or criteria_string in product.category.lower():
                        results.append(product)
        
                for product in results:
                    print(f"{product.name} - {product.category} - {product.quantity} - {product.price}")
            except Exception as e:
                print(f"Invalid criteria: {e}")


        elif command == '6':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            report = inventory.generate_report(datetime.strptime(start_date, '%Y-%m-%d').date(), datetime.strptime(end_date, '%Y-%m-%d').date())
            for product, quantity in report.items():
                print(f"{product}: {quantity}")

        elif command == '7':
            start_date_time = input("Enter start date and time (YYYY-MM-DD HH:MM:SS): ")
            end_date_time = input("Enter end date and time (YYYY-MM-DD HH:MM:SS): ")
            report = inventory.generate_sales_report(start_date_time, end_date_time)
            for product, details in report.items():
                print(f"{product}: Quantity: {details['Quantity']}, Sales Quantity: {details['Sales Quantity']}")

        elif command == '8':
            print("Sort by:")
            print("1. Price")
            print("2. Quantity")
            print("3. Category")
            sort_by = input("Enter number: ")
            if sort_by == '1':
                inventory.sort_products_by_price()
            elif sort_by == '2':
                inventory.sort_products_by_quantity()
            elif sort_by == '3':
                inventory.sort_products_by_category()
            else:
                print("Invalid option.")

        elif command == '9':
            save_inventory_to_file(inventory, inventory_filename)
            print("Inventory saved and exiting.")
            break

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
