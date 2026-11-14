/**
 * Buyzone Main JavaScript
 * Amazon & Flipkart Interactive Experience
 */

document.addEventListener('DOMContentLoaded', function () {
    initFlashDealTimer();
    initPDPGallery();
    initPincodeChecker();
    initAjaxCartAndWishlist();
    initCheckoutInteractions();
});

// 1. Flash Deals Countdown Timer
function initFlashDealTimer() {
    const hoursEl = document.getElementById('deal-hours');
    const minsEl = document.getElementById('deal-mins');
    const secsEl = document.getElementById('deal-secs');

    if (!hoursEl || !minsEl || !secsEl) return;

    // Set countdown for 10 hours from current session start
    let remainingSeconds = (10 * 3600) + (45 * 60) + 20;

    function updateTimer() {
        if (remainingSeconds <= 0) {
            remainingSeconds = 12 * 3600; // Reset
        }
        const h = Math.floor(remainingSeconds / 3600);
        const m = Math.floor((remainingSeconds % 3600) / 60);
        const s = remainingSeconds % 60;

        hoursEl.textContent = String(h).padStart(2, '0');
        minsEl.textContent = String(m).padStart(2, '0');
        secsEl.textContent = String(s).padStart(2, '0');

        remainingSeconds--;
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

// 2. Product Detail Page Gallery Thumbnail Switcher & Zoom
function initPDPGallery() {
    const mainImg = document.getElementById('pdp-main-image');
    const thumbBtns = document.querySelectorAll('.bz-thumb-btn');

    if (!mainImg || thumbBtns.length === 0) return;

    thumbBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            thumbBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const targetUrl = this.getAttribute('data-img-url');
            if (targetUrl) {
                mainImg.src = targetUrl;
            }
        });
    });

    // Image Zoom on Hover
    const zoomContainer = document.querySelector('.bz-pdp-main-img');
    if (zoomContainer && mainImg) {
        zoomContainer.addEventListener('mousemove', function (e) {
            const rect = zoomContainer.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width * 100;
            const y = (e.clientY - rect.top) / rect.height * 100;
            mainImg.style.transformOrigin = `${x}% ${y}%`;
            mainImg.style.transform = 'scale(1.5)';
        });

        zoomContainer.addEventListener('mouseleave', function () {
            mainImg.style.transformOrigin = 'center center';
            mainImg.style.transform = 'scale(1)';
        });
    }
}

// 3. Pincode Delivery Estimator
function initPincodeChecker() {
    const checkBtn = document.getElementById('btn-check-pincode');
    const pincodeInput = document.getElementById('input-pincode');
    const resultBox = document.getElementById('pincode-result');

    if (!checkBtn || !pincodeInput || !resultBox) return;

    checkBtn.addEventListener('click', function () {
        const pin = pincodeInput.value.trim();
        if (pin.length !== 6 || isNaN(pin)) {
            resultBox.innerHTML = '<span class="text-danger"><i class="fa-solid fa-circle-exclamation me-1"></i>Please enter a valid 6-digit Indian PIN code.</span>';
            return;
        }

        resultBox.innerHTML = '<span class="text-muted"><i class="fa-solid fa-spinner fa-spin me-1"></i>Checking delivery availability...</span>';

        fetch(`/store/check-pincode/?pincode=${pin}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    resultBox.innerHTML = `
                        <div class="alert alert-success py-2 px-3 mt-2 mb-0" style="font-size: 0.88rem;">
                            <i class="fa-solid fa-truck-fast text-success me-2"></i>
                            <strong>${data.message}</strong>
                        </div>
                    `;
                } else {
                    resultBox.innerHTML = `
                        <div class="alert alert-danger py-2 px-3 mt-2 mb-0" style="font-size: 0.88rem;">
                            <i class="fa-solid fa-triangle-exclamation me-2"></i>${data.message}
                        </div>
                    `;
                }
            })
            .catch(() => {
                resultBox.innerHTML = '<span class="text-danger">Unable to check PIN code right now.</span>';
            });
    });
}

// 4. AJAX Add to Cart & Wishlist with Toast notification
function initAjaxCartAndWishlist() {
    // Add to Cart
    document.querySelectorAll('.bz-ajax-add-cart').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const qtyInput = document.getElementById(`qty-${productId}`);
            const qty = qtyInput ? qtyInput.value : 1;

            const originalHtml = this.innerHTML;
            this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';
            this.disabled = true;

            const formData = new FormData();
            formData.append('quantity', qty);

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                this.innerHTML = '<i class="fa-solid fa-check"></i> Added!';
                setTimeout(() => {
                    this.innerHTML = originalHtml;
                    this.disabled = false;
                }, 1500);

                if (data.cart_count !== undefined) {
                    const badge = document.querySelector('.bz-cart-badge');
                    if (badge) badge.textContent = data.cart_count;
                }
                showBuyzoneToast(data.message, 'success');
            })
            .catch(err => {
                this.innerHTML = originalHtml;
                this.disabled = false;
                showBuyzoneToast('Item added to cart!', 'success');
                setTimeout(() => { window.location.reload(); }, 600);
            });
        });
    });

    // Toggle Wishlist
    document.querySelectorAll('.bz-ajax-wishlist').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');

            fetch(`/cart/wishlist/toggle/${productId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                return res.json();
            })
            .then(data => {
                if (!data) return;
                const icon = this.querySelector('i');
                if (data.action === 'added') {
                    this.classList.add('active');
                    if (icon) {
                        icon.classList.remove('fa-regular');
                        icon.classList.add('fa-solid');
                    }
                } else {
                    this.classList.remove('active');
                    if (icon) {
                        icon.classList.remove('fa-solid');
                        icon.classList.add('fa-regular');
                    }
                }

                const wBadge = document.querySelector('.bz-wishlist-badge');
                if (wBadge && data.wishlist_count !== undefined) {
                    wBadge.textContent = data.wishlist_count;
                }

                showBuyzoneToast(data.message, 'info');
            })
            .catch(() => {
                showBuyzoneToast('Please log in to manage your wishlist.', 'warning');
            });
        });
    });
}

// 5. Checkout Interactions (Address cards & Payment Tabs)
function initCheckoutInteractions() {
    // Address Cards selection
    const addrCards = document.querySelectorAll('.bz-checkout-addr-card');
    const selectedAddrInput = document.getElementById('id_selected_address_id');
    const newAddrCollapse = document.getElementById('newAddressFormCollapse');

    addrCards.forEach(card => {
        card.addEventListener('click', function () {
            addrCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            const addrId = this.getAttribute('data-address-id');
            if (selectedAddrInput) {
                selectedAddrInput.value = addrId;
            }
            if (newAddrCollapse && newAddrCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(newAddrCollapse) || new bootstrap.Collapse(newAddrCollapse);
                bsCollapse.hide();
            }
        });
    });

    // Payment Method Tabs
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
    const paymentPanels = {
        'COD': document.getElementById('panel-cod'),
        'UPI': document.getElementById('panel-upi'),
        'CARD': document.getElementById('panel-card'),
        'NETBANKING': document.getElementById('panel-netbanking')
    };

    function updatePaymentPanels(selectedMethod) {
        Object.keys(paymentPanels).forEach(method => {
            const panel = paymentPanels[method];
            if (panel) {
                if (method === selectedMethod) {
                    panel.classList.remove('d-none');
                } else {
                    panel.classList.add('d-none');
                }
            }
        });
    }

    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            updatePaymentPanels(this.value);
        });
        if (radio.checked) {
            updatePaymentPanels(radio.value);
        }
    });
}

// Helper: Toast alert popup
function showBuyzoneToast(message, type = 'info') {
    let toastContainer = document.getElementById('bz-toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'bz-toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast-' + Math.random().toString(36).substring(2, 9);
    const bgClass = type === 'success' ? 'bg-success text-white' : (type === 'danger' ? 'bg-danger text-white' : 'bg-dark text-white');

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center ${bgClass} border-0 shadow-lg`;
    toastEl.id = toastId;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-info-circle'} fs-5"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
    bsToast.show();

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

// Helper: Read CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
