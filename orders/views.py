from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid
import json

from .models import ProductService, Order, OrderItem, OrderStatusHistory
from .forms import OrderForm, OrderItemForm, OrderCancellationForm, OrderSearchForm, ProductSearchForm
from payments.models import Payment, PaymentMethod, PaymentTransaction
from delivery.models import DeliveryArea, DeliveryAssignment, DeliveryStatus
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return bool(self.request.user.is_authenticated and (
            self.request.user.is_staff or
            self.request.user.is_superuser or
            getattr(self.request.user, 'user_type', None) == 'admin'
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Administrative access required.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class ProductListView(ListView):
    """
    Public catalog of essentials and products.
    """
    model = ProductService
    template_name = 'orders/products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = ProductService.objects.filter(is_available=True)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(category__icontains=q)
            )

        category = self.request.GET.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)

        sort = self.request.GET.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductService.CATEGORY_CHOICES
        context['selected_category'] = self.request.GET.get('category', 'all')
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_sort'] = self.request.GET.get('sort', 'newest')
        return context


class ProductDetailView(DetailView):
    """
    Product detail page with stock status and related items.
    """
    model = ProductService
    template_name = 'orders/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = ProductService.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(pk=self.object.pk)[:4]
        return context


class ProductCategoryView(ListView):
    """
    Filtered view by category.
    """
    model = ProductService
    template_name = 'orders/products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return ProductService.objects.filter(
            category=self.kwargs['category'],
            is_available=True
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductService.CATEGORY_CHOICES
        context['selected_category'] = self.kwargs['category']
        return context


class CartView(LoginRequiredMixin, TemplateView):
    """
    Customer shopping cart view.
    """
    template_name = 'orders/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Server-side delivery areas for estimation
        context['delivery_areas'] = DeliveryArea.objects.filter(is_active=True).order_by('delivery_fee')
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    """
    Multi-step checkout view with verified areas and payment channels.
    """
    template_name = 'orders/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['delivery_areas'] = DeliveryArea.objects.filter(is_active=True).order_by('delivery_fee')
        context['payment_methods'] = PaymentMethod.objects.filter(is_active=True).order_by('id')

        # Customer prefill data
        context['customer_name'] = user.get_full_name() or user.username
        context['customer_email'] = user.email
        context['customer_phone'] = user.phone_number
        context['customer_address'] = user.address or ''
        context['customer_city'] = user.city or ''

        # Instructions from profile if available
        instructions = ''
        if hasattr(user, 'customer_profile') and user.customer_profile:
            instructions = user.customer_profile.delivery_instructions or ''
        context['customer_instructions'] = instructions

        return context


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    """
    Order confirmation view.
    """
    template_name = 'orders/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_num = self.request.GET.get('order_number')
        if order_num:
            context['order'] = Order.objects.filter(
                order_number=order_num,
                customer=self.request.user
            ).first()
        return context


class OrderListView(LoginRequiredMixin, ListView):
    """
    Customer or admin order history list.
    """
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin':
            queryset = Order.objects.all().order_by('-created_at')
        else:
            queryset = Order.objects.filter(customer=user).order_by('-created_at')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(order_number__icontains=q) |
                Q(delivery_address__icontains=q) |
                Q(delivery_city__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = bool(
            self.request.user.is_staff or
            self.request.user.is_superuser or
            getattr(self.request.user, 'user_type', None) == 'admin'
        )
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Order detail view with strict ownership verification.
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin':
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        context['items'] = order.items.select_related('product').all()
        context['payments'] = order.payments.all()
        context['status_history'] = order.status_history.select_related('created_by').order_by('-created_at')
        context['can_cancel'] = order.can_be_cancelled()
        context['is_delivered'] = (order.status == 'delivered')
        return context


class OrderTrackView(LoginRequiredMixin, DetailView):
    """
    Visual delivery progress timeline.
    """
    model = Order
    template_name = 'orders/order_track.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin':
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        context['history'] = order.status_history.order_by('created_at')
        if hasattr(order, 'delivery_assignment') and order.delivery_assignment:
            context['assignment'] = order.delivery_assignment
            context['updates'] = order.delivery_assignment.status_updates.order_by('timestamp')
        return context


class InvoiceView(LoginRequiredMixin, DetailView):
    """
    Clean, printable invoice document for customer orders.
    """
    model = Order
    template_name = 'orders/invoice.html'
    context_object_name = 'order'

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        user = self.request.user
        try:
            if user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin':
                return Order.objects.get(order_number=order_id)
            return Order.objects.get(order_number=order_id, customer=user)
        except Order.DoesNotExist:
            return None


class OrderEditView(LoginRequiredMixin, UpdateView):
    """
    Customer edit view for pending orders.
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_edit.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin':
            return Order.objects.all()
        return Order.objects.filter(customer=user, status='pending')

    def get_success_url(self):
        messages.success(self.request, 'Order details updated successfully.')
        return reverse('orders:order_detail', kwargs={'pk': self.object.pk})


class OrderCancelView(LoginRequiredMixin, TemplateView):
    """
    Order cancellation with stock restoration and audit history.
    """
    template_name = 'orders/order_cancel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        order = get_object_or_404(Order, pk=kwargs['pk'])

        if order.customer != user and not (user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin'):
            context['error'] = 'You are not authorized to cancel this order.'
            return context

        if not order.can_be_cancelled():
            context['error'] = 'This order has progressed beyond the cancellation window.'
            context['order'] = order
            return context

        context['order'] = order
        context['form'] = OrderCancellationForm()
        context['cancellation_deadline'] = order.get_cancellation_deadline()
        context['can_cancel'] = True
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        order = get_object_or_404(Order, pk=kwargs['pk'])

        if order.customer != user and not (user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin'):
            messages.error(request, 'You are not authorized to cancel this order.')
            return redirect('orders:order_list')

        if not order.can_be_cancelled():
            messages.error(request, 'This order cannot be cancelled at this stage.')
            return redirect('orders:order_detail', pk=order.pk)

        form = OrderCancellationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order.status = 'cancelled'
                order.cancellation_reason = form.cleaned_data['reason']
                order.cancellation_notes = form.cleaned_data.get('additional_notes', '')
                order.cancelled_at = timezone.now()
                order.cancelled_by = user
                order.refund_preference = form.cleaned_data.get('refund_preference', 'no_refund')
                order.save()

                # Restore stock for ordered items
                for item in order.items.all():
                    item.product.restore_stock(item.quantity)

                # Update any associated pending delivery assignment
                if hasattr(order, 'delivery_assignment') and order.delivery_assignment:
                    DeliveryStatus.objects.create(
                        delivery_assignment=order.delivery_assignment,
                        status='failed',
                        notes=f"Order cancelled by {user.get_full_name() or user.username}."
                    )

                # Record audit history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='cancelled',
                    notes=f"Cancelled by {user.get_full_name() or user.username}. Reason: {order.cancellation_reason}",
                    created_by=user
                )

            messages.success(request, f'Order #{order.order_number} has been cancelled.')
            return redirect('orders:order_detail', pk=order.pk)

        return render(request, self.template_name, {
            'order': order,
            'form': form,
            'can_cancel': True,
        })


# ============================================================================
# REAL-TIME SECURE ORDER CREATION API
# ============================================================================

@require_http_methods(["POST"])
def create_order_from_cart(request):
    """
    Server-side order creation from cart payload.
    Recalculates all pricing, stock, delivery fees, and records payment.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required. Please sign in.'}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid JSON request payload.'}, status=400)

    cart_items = data.get('cart_items', [])
    if not cart_items:
        return JsonResponse({'success': False, 'message': 'Your shopping cart is empty.'}, status=400)

    delivery_address = str(data.get('delivery_address', '')).strip()
    delivery_city = str(data.get('delivery_city', '')).strip() or 'Dhaka'
    special_instructions = str(data.get('special_instructions', '')).strip()
    payment_method_code = str(data.get('payment_method', 'cash_on_delivery')).strip()
    payment_phone = str(data.get('payment_phone', '')).strip()
    transaction_id_input = str(data.get('transaction_id', '')).strip()

    if not delivery_address:
        return JsonResponse({'success': False, 'message': 'Please provide a valid delivery address.'}, status=400)

    # 1. Server-side delivery fee calculation
    matched_area = DeliveryArea.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=delivery_city) | Q(name__iexact=delivery_city)
    ).first()

    delivery_fee = matched_area.delivery_fee if matched_area else Decimal('50.00')

    # 2. Server-side product price & stock verification
    subtotal = Decimal('0.00')
    verified_items = []
    out_of_stock_errors = []

    for item in cart_items:
        item_id = item.get('id') or item.get('product_id')
        try:
            quantity = int(item.get('quantity', 1))
            if quantity <= 0:
                continue
        except (ValueError, TypeError):
            continue

        try:
            product = ProductService.objects.get(id=item_id, is_available=True)
        except ProductService.DoesNotExist:
            return JsonResponse({'success': False, 'message': f'Item ID {item_id} is unavailable or was removed.'}, status=400)

        if not product.is_in_stock(quantity):
            out_of_stock_errors.append(f"{product.name} (requested {quantity}, available {product.stock_quantity})")
            continue

        item_total = product.price * Decimal(str(quantity))
        subtotal += item_total
        verified_items.append((product, quantity, product.price, item_total))

    if out_of_stock_errors:
        return JsonResponse({
            'success': False,
            'message': 'Insufficient stock for items:\n' + '\n'.join(out_of_stock_errors)
        }, status=400)

    if not verified_items:
        return JsonResponse({'success': False, 'message': 'No valid items found in order.'}, status=400)

    # Calculate final server total
    total_amount = subtotal + delivery_fee

    # Validate digital wallet payment specifics if selected
    if payment_method_code in ('bkash', 'nagad', 'rocket'):
        if not transaction_id_input:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required for mobile wallet payments.'}, status=400)

        if Payment.objects.filter(transaction_id=transaction_id_input).exists():
            return JsonResponse({'success': False, 'message': 'This Transaction ID has already been submitted.'}, status=400)

    # 3. Atomic Order Placement
    try:
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                delivery_address=delivery_address,
                delivery_city=delivery_city,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                status='pending',
                special_instructions=special_instructions,
            )

            for product, quantity, unit_price, item_total in verified_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=item_total,
                )
                product.reduce_stock(quantity)

            # Record status history
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                notes='Order placed successfully via web checkout.',
                created_by=request.user
            )

            # Record Payment
            if payment_method_code == 'cash_on_delivery':
                Payment.objects.create(
                    order=order,
                    payment_method='cash_on_delivery',
                    amount=total_amount,
                    status='pending',
                    payment_details={
                        'channel': 'Cash on Delivery',
                        'notes': 'Collect full cash upon delivery.',
                    }
                )
            else:
                # Digital wallet development flow
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method_code,
                    amount=total_amount,
                    status='completed',
                    transaction_id=transaction_id_input,
                    paid_at=timezone.now(),
                    payment_details={
                        'channel': payment_method_code.upper(),
                        'phone': payment_phone,
                        'transaction_id': transaction_id_input,
                        'mode': 'Verified Gateway / Sandbox',
                    }
                )
                PaymentTransaction.objects.create(
                    payment=payment,
                    action='WALLET_VERIFIED',
                    status='SUCCESS',
                    message=f"Received transaction {transaction_id_input} from {payment_phone}",
                    response_data={'amount': str(total_amount), 'phone': payment_phone}
                )

            # 4. Optional Automatic Delivery Assignment to an Available Rider
            available_agent = User.objects.filter(
                user_type='delivery_agent',
                delivery_agent_profile__is_available=True
            ).first()

            if available_agent:
                assignment = DeliveryAssignment.objects.create(
                    order=order,
                    delivery_agent=available_agent,
                    assigned_by=request.user,
                    delivery_notes=f"Auto-assigned for {delivery_city} zone."
                )
                DeliveryStatus.objects.create(
                    delivery_assignment=assignment,
                    status='assigned',
                    location='SwiftDrop Dispatch Center',
                    notes='Rider notified for pickup.'
                )

            # Clear session cart if present
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Server error creating order: {str(e)}'}, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Order placed successfully!',
        'order_id': order.id,
        'order_number': order.order_number,
        'subtotal': str(subtotal),
        'delivery_fee': str(delivery_fee),
        'total_amount': str(total_amount),
        'redirect_url': reverse('orders:order_detail', kwargs={'pk': order.id})
    })


# ============================================================================
# ADMIN ORDER & CATALOG MANAGEMENT VIEWS
# ============================================================================

class AdminOrderListView(AdminRequiredMixin, ListView):
    """
    Administrative list of all customer orders.
    """
    model = Order
    template_name = 'orders/admin_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.all().select_related('customer').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(order_number__icontains=q) |
                Q(customer__username__icontains=q) |
                Q(customer__email__icontains=q) |
                Q(customer__phone_number__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.ORDER_STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    """
    Administrative detail view for an order.
    """
    model = Order
    template_name = 'orders/admin_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        context['items'] = order.items.select_related('product').all()
        context['payments'] = order.payments.all()
        context['status_history'] = order.status_history.select_related('created_by').order_by('-created_at')
        context['delivery_agents'] = User.objects.filter(user_type='delivery_agent').select_related('delivery_agent_profile')
        context['status_choices'] = Order.ORDER_STATUS_CHOICES
        return context


class AssignDeliveryAgentView(AdminRequiredMixin, TemplateView):
    """
    Assign or reassign delivery partner to an order.
    """
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        agent_id = request.POST.get('delivery_agent_id')
        agent = get_object_or_404(User, pk=agent_id, user_type='delivery_agent')

        assignment, created = DeliveryAssignment.objects.get_or_create(
            order=order,
            defaults={
                'delivery_agent': agent,
                'assigned_by': request.user,
                'delivery_notes': request.POST.get('delivery_notes', '')
            }
        )
        if not created:
            assignment.delivery_agent = agent
            assignment.assigned_by = request.user
            assignment.delivery_notes = request.POST.get('delivery_notes', '')
            assignment.save()

        # Update order status to confirmed / processing if pending
        if order.status == 'pending':
            order.status = 'confirmed'
            order.save()

        DeliveryStatus.objects.create(
            delivery_assignment=assignment,
            status='assigned',
            location='SwiftDrop Fulfillment Hub',
            notes=f"Assigned to {agent.get_full_name() or agent.username} by Admin."
        )

        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,
            notes=f"Delivery assigned to {agent.get_full_name() or agent.username}.",
            created_by=request.user
        )

        messages.success(request, f"Order #{order.order_number} assigned to {agent.get_full_name() or agent.username}.")
        return redirect('orders:admin_order_detail', pk=order.pk)


class AdminOrderStatusUpdateView(AdminRequiredMixin, TemplateView):
    """
    Direct status change by administrator.
    """
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            old_status = order.status
            order.status = new_status

            if new_status == 'delivered':
                # Mark pending cash payment as completed
                for payment in order.payments.filter(status='pending'):
                    payment.status = 'completed'
                    payment.paid_at = timezone.now()
                    payment.save()

            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes or f"Status changed from {old_status} to {new_status} by Admin.",
                created_by=request.user
            )

            messages.success(request, f"Order #{order.order_number} status updated to {order.get_status_display()}.")
        else:
            messages.error(request, "Invalid status choice selected.")

        return redirect('orders:admin_order_detail', pk=order.pk)


@require_http_methods(["POST"])
def admin_update_order_status(request):
    """
    AJAX endpoint for quick admin status toggle.
    """
    if not request.user.is_authenticated or not (request.user.is_staff or getattr(request.user, 'user_type', None) == 'admin'):
        return JsonResponse({'success': False, 'message': 'Admin privileges required.'}, status=403)

    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')

        order = Order.objects.get(id=order_id)
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return JsonResponse({'success': False, 'message': 'Invalid status choice.'})

        old_status = order.status
        order.status = new_status
        if new_status == 'delivered':
            for payment in order.payments.filter(status='pending'):
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.save()
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=f"Status updated via quick controls to {new_status}.",
            created_by=request.user
        )

        return JsonResponse({
            'success': True,
            'message': f"Order #{order.order_number} updated to {order.get_status_display()}.",
            'status': order.status,
            'status_display': order.get_status_display()
        })
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Product CRUD APIs for Admin Panel
@require_http_methods(["POST"])
def add_product(request):
    if not request.user.is_authenticated or not (request.user.is_staff or getattr(request.user, 'user_type', None) == 'admin'):
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)

    try:
        data = json.loads(request.body)
        product = ProductService.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            price=Decimal(str(data.get('price', '0.00'))),
            category=data.get('category', 'groceries'),
            stock_quantity=int(data.get('stock_quantity', 10)),
            is_available=True
        )
        return JsonResponse({'success': True, 'message': 'Product added successfully', 'product_id': product.id})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@require_http_methods(["POST"])
def update_product(request, product_id):
    if not request.user.is_authenticated or not (request.user.is_staff or getattr(request.user, 'user_type', None) == 'admin'):
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)

    try:
        product = get_object_or_404(ProductService, id=product_id)
        data = json.loads(request.body)
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = Decimal(str(data.get('price', product.price)))
        product.category = data.get('category', product.category)
        product.stock_quantity = int(data.get('stock_quantity', product.stock_quantity))
        product.is_available = bool(data.get('is_available', product.is_available))
        product.save()
        return JsonResponse({'success': True, 'message': 'Product updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@require_http_methods(["DELETE", "POST"])
def delete_product(request, product_id):
    if not request.user.is_authenticated or not (request.user.is_staff or getattr(request.user, 'user_type', None) == 'admin'):
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)

    try:
        product = get_object_or_404(ProductService, id=product_id)
        product.delete()
        return JsonResponse({'success': True, 'message': 'Product deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Order items sub-views
class OrderItemListView(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = 'orders/order_item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return OrderItem.objects.filter(order__pk=self.kwargs['order_pk'])


class OrderItemAddView(AdminRequiredMixin, CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_add.html'

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs['order_pk'])
        form.instance.order = order
        response = super().form_valid(form)
        messages.success(self.request, 'Item added to order.')
        return response


class OrderItemEditView(AdminRequiredMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_edit.html'

    def get_queryset(self):
        return OrderItem.objects.filter(order__pk=self.kwargs['order_pk'])


class OrderItemDeleteView(AdminRequiredMixin, DeleteView):
    model = OrderItem
    template_name = 'orders/order_item_delete.html'

    def get_queryset(self):
        return OrderItem.objects.filter(order__pk=self.kwargs['order_pk'])

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.kwargs['order_pk']})
