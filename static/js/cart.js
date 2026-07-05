function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

function addToCart(payload) {
  const body = new URLSearchParams(payload);
  return fetch('/cart/add/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
  })
    .then((res) => res.json())
    .then((data) => {
      const badge = document.querySelector('.cart-badge');
      const link = document.querySelector('.cart-link');
      if (data.cart_count) {
        if (badge) {
          badge.textContent = data.cart_count;
        } else if (link) {
          const span = document.createElement('span');
          span.className = 'cart-badge';
          span.textContent = data.cart_count;
          link.appendChild(span);
        }
      }
      return data;
    });
}
