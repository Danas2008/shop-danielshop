from .models import CartItem


def cart_count(request):
    if not request.session.session_key:
        return {"cart_count": 0}
    count = CartItem.objects.filter(session_key=request.session.session_key).count()
    return {"cart_count": count}
