from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'dev-secret-key'


# Конфигурация базы данных
def get_db_config():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'warehouse_db')
    }


def get_db_connection():
    """Устанавливает соединение с базой данных"""
    try:
        conn = mysql.connector.connect(**get_db_config())
        return conn
    except Error as e:
        flash(f"Ошибка подключения к базе данных: {str(e)}", 'danger')
        return None


@app.route('/')
def index():
    """Главная страница с общей статистикой"""
    conn = get_db_connection()
    if not conn:
        return render_template('index.html', stats=None)

    try:
        cursor = conn.cursor(dictionary=True)
        stats = {}

        # 1. Количество товаров в каталоге
        cursor.execute("SELECT COUNT(*) as count FROM Products")
        stats['products'] = cursor.fetchone()['count']

        # 2. Общее количество товаров на всех складах
        cursor.execute("SELECT SUM(quantity) as total FROM Inventory")
        total_items = cursor.fetchone()['total']
        stats['total_items'] = total_items if total_items is not None else 0

        # 3. Количество складов
        cursor.execute("SELECT COUNT(*) as count FROM Warehouses WHERE is_active = TRUE")
        stats['warehouses'] = cursor.fetchone()['count']

        # 4. Товары с количеством ниже минимального запаса
        cursor.execute("""
            SELECT COUNT(DISTINCT p.product_id) as count 
            FROM Products p
            JOIN Inventory i ON p.product_id = i.product_id
            WHERE i.quantity <= p.min_stock_level
        """)
        stats['low_stock'] = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        return render_template('index.html', stats=stats)

    except Error as e:
        flash(f"Ошибка при получении данных: {str(e)}", 'danger')
        if 'cursor' in locals(): cursor.close()
        if conn: conn.close()
        return render_template('index.html', stats=None)


@app.route('/products')
def products():
    """Страница со списком всех товаров"""
    conn = get_db_connection()
    if not conn:
        return render_template('products.html', products=[])

    try:
        cursor = conn.cursor(dictionary=True)

        # Получаем список товаров с информацией о категориях и единицах измерения
        cursor.execute("""
            SELECT p.*, c.name as category_name, u.name as unit_name,
                   COALESCE(SUM(i.quantity), 0) as total_quantity
            FROM Products p
            LEFT JOIN Categories c ON p.category_id = c.category_id
            LEFT JOIN Units u ON p.unit_id = u.unit_id
            LEFT JOIN Inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id
            ORDER BY p.name
        """)
        products = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('products.html', products=products)

    except Error as e:
        flash(f"Ошибка при загрузке товаров: {str(e)}", 'danger')
        return render_template('products.html', products=[])


@app.route('/inventory')
def inventory():
    """Страница с инвентаризацией"""
    conn = get_db_connection()
    if not conn:
        return render_template('inventory.html', inventory=[])

    try:
        cursor = conn.cursor(dictionary=True)

        # Получаем данные инвентаря с дополнительной информацией
        cursor.execute("""
            SELECT i.*, 
                   p.name as product_name, p.barcode,
                   l.code as location_code, l.description as location_desc,
                   w.name as warehouse_name
            FROM Inventory i
            JOIN Products p ON i.product_id = p.product_id
            JOIN Locations l ON i.location_id = l.location_id
            JOIN Warehouses w ON l.warehouse_id = w.warehouse_id
            ORDER BY w.name, l.code, p.name
        """)
        inventory = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('inventory.html', inventory=inventory)

    except Error as e:
        flash(f"Ошибка при загрузке инвентаря: {str(e)}", 'danger')
        return render_template('inventory.html', inventory=[])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')