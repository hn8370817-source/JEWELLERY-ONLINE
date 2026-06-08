document.addEventListener('DOMContentLoaded', function() {
    // Quick View button click
    document.querySelectorAll('.quick-view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const prodId = this.dataset.productId;
            fetch(`/quick_view/${prodId}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('qvName').textContent = data.name;
                    document.getElementById('qvDescription').textContent = data.description;
                    document.getElementById('qvPrice').textContent = '₹' + data.price;
                    document.getElementById('qvCategory').textContent = data.category;

                    // Stock badges
                    if (data.stock > 0) {
                        document.getElementById('qvStockIn').style.display = '';
                        document.getElementById('qvStockOut').style.display = 'none';
                        document.getElementById('qvAddCartBtn').disabled = false;
                    } else {
                        document.getElementById('qvStockIn').style.display = 'none';
                        document.getElementById('qvStockOut').style.display = '';
                        document.getElementById('qvAddCartBtn').disabled = true;
                    }

                    // Set Add to Cart form action
                    document.getElementById('qvAddCartForm').action = `/add_to_cart/${prodId}`;

                    // Build image carousel
                    const inner = document.getElementById('qvCarouselInner');
                    inner.innerHTML = '';
                    data.images.forEach((img, idx) => {
                        const div = document.createElement('div');
                        div.className = `carousel-item ${idx === 0 ? 'active' : ''}`;
                        div.innerHTML = `<img src="${img.url}" class="d-block w-100" alt="${img.alt}">`;
                        inner.appendChild(div);
                    });

                    // Open modal
                    new bootstrap.Modal(document.getElementById('quickViewModal')).show();
                });
        });
    });
});

// Wishlist toggle from quick view (you can extend with API call; currently just placeholder)
function toggleWishlistFromQV() {
    alert('Login to add to wishlist.');
}
