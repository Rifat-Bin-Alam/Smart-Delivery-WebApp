from django.conf import settings


def swift_drop_context(request):
    """
    Global context processor for SwiftDrop branding and navigation helpers.
    """
    cart_item_count = 0
    # Also support session-based cart count if session is used
    session_cart = request.session.get('cart', {})
    if isinstance(session_cart, dict):
        cart_item_count = sum(item.get('quantity', 0) for item in session_cart.values() if isinstance(item, dict))
    elif isinstance(session_cart, list):
        cart_item_count = sum(item.get('quantity', 0) for item in session_cart if isinstance(item, dict))

    return {
        'BRAND_NAME': getattr(settings, 'BRAND_NAME', 'SwiftDrop'),
        'TAGLINE': getattr(settings, 'TAGLINE', 'Your Essentials. Delivered Smarter.'),
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '৳'),
        'CURRENCY_CODE': getattr(settings, 'CURRENCY_CODE', 'BDT'),
        'session_cart_count': cart_item_count,
    }
