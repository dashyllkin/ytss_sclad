document.addEventListener('DOMContentLoaded', function() {
    // Инициализация бокового меню
    const menuItems = document.querySelectorAll('.sidebar nav li');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Обработка кнопки выхода
    const logoutBtn = document.querySelector('.logout-btn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите выйти?')) {
                // Здесь должна быть логика выхода
                alert('Вы успешно вышли из системы');
            }
        });
    }
    
    // Обработка кнопок заказа в таблице "Заканчивающиеся товары"
    const orderButtons = document.querySelectorAll('.low-stock .small-btn');
    
    orderButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const productName = this.closest('tr').querySelector('td:first-child').textContent;
            alert(`Заказ на товар "${productName}" оформлен`);
        });
    });
    
    // Здесь можно добавить другие интерактивные элементы
});