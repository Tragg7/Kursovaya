function filterProducts(category) {
    console.log("Фильтрация по категории:", category);

    const products = document.querySelectorAll('.product');
    products.forEach(product => {
        if (category === 'all' || product.dataset.category === category) {
            product.style.display = '';
        } else {
            product.style.display = 'none';
        }
    });
}
