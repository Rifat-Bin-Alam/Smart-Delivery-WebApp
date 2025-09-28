from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid
import json

from .models import ProductService, Order, OrderItem, OrderStatusHistory
from .forms import OrderForm, OrderItemForm, OrderCancellationForm
from payments.models import Payment

class ProductListView(ListView):
    """
    Product list view
    """
    model = ProductService
    template_name = 'orders/products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        return ProductService.objects.filter(is_available=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductService.objects.values_list('category', flat=True).distinct()
        return context


class ProductDetailView(DetailView):
    """
    Product detail view
    """
    model = ProductService
    template_name = 'orders/product_detail.html'
    context_object_name = 'product'


class ProductCategoryView(ListView):
    """
    Product category view
    """
    model = ProductService
    template_name = 'orders/product_category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        return ProductService.objects.filter(
            category=self.kwargs['category'],
            is_available=True
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs['category']
        return context


class OrderListView(LoginRequiredMixin, ListView):
    """
    Order list view
    """
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Order.objects.all().order_by('-created_at')
        else:
            return Order.objects.filter(customer=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_staff or self.request.user.is_superuser
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Order detail view
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user)


class OrderCreateView(TemplateView):
    """
    Order create view
    """
    template_name = 'orders/simple_order_create.html'


class CartView(LoginRequiredMixin, TemplateView):
    """
    Shopping cart view
    """
    template_name = 'orders/cart.html'


class CheckoutView(LoginRequiredMixin, TemplateView):
    """
    Checkout view
    """
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get cart data from session or localStorage (handled by JavaScript)
        context['cart_items'] = []  # Will be populated by JavaScript
        return context


class OrderSuccessView(TemplateView):
    """
    Order success view
    """
    template_name = 'orders/success.html'


class InvoiceView(LoginRequiredMixin, DetailView):
    """
    Invoice view
    """
    model = Order
    template_name = 'orders/invoice.html'
    context_object_name = 'order'
    
    def get_object(self):
        order_id = self.kwargs.get('order_id')
        try:
            order = Order.objects.get(order_number=order_id)
            # Check if user has permission to view this order
            if self.request.user.is_staff or self.request.user.is_superuser or order.customer == self.request.user:
                return order
            else:
                return None
        except Order.DoesNotExist:
            return None


class OrderTrackView(LoginRequiredMixin, DetailView):
    """
    Order tracking view
    """
    model = Order
    template_name = 'orders/order_track.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user)


class OrderEditView(LoginRequiredMixin, UpdateView):
    """
    Order edit view
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_edit.html'
    success_url = reverse_lazy('orders:order_list')
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user)


class OrderCancelView(LoginRequiredMixin, TemplateView):
    """
    Order cancel view with comprehensive cancellation form
    """
    template_name = 'orders/order_cancel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, pk=kwargs['pk'])
        
        # Check if user can cancel this order
        if order.customer != self.request.user and not self.request.user.is_staff:
            context['error'] = 'আপনার এই অর্ডার বাতিল করার অনুমতি নেই।'
            return context
        
        # Check if order can be cancelled
        if not order.can_be_cancelled():
            context['error'] = 'এই অর্ডার আর বাতিল করা যাবে না।'
            context['order'] = order
            return context
        
        context['order'] = order
        context['form'] = OrderCancellationForm()
        context['cancellation_deadline'] = order.get_cancellation_deadline()
        context['can_cancel'] = order.can_be_cancelled()
        
        return context
    
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        
        # Check permissions
        if order.customer != request.user and not request.user.is_staff:
            messages.error(request, 'আপনার এই অর্ডার বাতিল করার অনুমতি নেই।')
            return redirect('orders:order_detail', pk=order.pk)
        
        # Check if order can be cancelled
        if not order.can_be_cancelled():
            messages.error(request, 'এই অর্ডার আর বাতিল করা যাবে না।')
            return redirect('orders:order_detail', pk=order.pk)
        
        form = OrderCancellationForm(request.POST)
        
        if form.is_valid():
            # Update order with cancellation details
            order.status = 'cancelled'
            order.cancellation_reason = form.cleaned_data['reason']
            order.cancellation_notes = form.cleaned_data['additional_notes']
            order.cancelled_at = timezone.now()
            order.cancelled_by = request.user
            order.refund_preference = form.cleaned_data['refund_preference']
            order.save()
            
            # Create status history entry
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                notes=f'Order cancelled by {request.user.get_full_name()}. Reason: {form.cleaned_data["reason"]}',
                created_by=request.user
            )
            
            # Create refund if needed
            if form.cleaned_data['refund_preference'] and form.cleaned_data['refund_preference'] != 'no_refund_needed':
                self._create_refund(order, form.cleaned_data['refund_preference'])
            
            messages.success(request, 'অর্ডার সফলভাবে বাতিল হয়েছে। রিফান্ড প্রক্রিয়াকরণ শুরু হয়েছে।')
            return redirect('orders:order_detail', pk=order.pk)
        else:
            messages.error(request, 'ফর্মে কিছু ত্রুটি আছে। দয়া করে আবার চেষ্টা করুন।')
            return self.get(request, *args, **kwargs)
    
    def _create_refund(self, order, refund_preference):
        """
        Create refund record for cancelled order
        """
        try:
            from payments.models import Refund, Payment
            
            # Find the payment for this order
            payment = Payment.objects.filter(order=order).first()
            
            if payment:
                Refund.objects.create(
                    payment=payment,
                    amount=order.total_amount,
                    reason=f'Order cancellation: {order.cancellation_reason}',
                    status='pending',
                    processed_by=order.cancelled_by
                )
        except Exception as e:
            # Log error but don't fail the cancellation
            print(f"Error creating refund: {e}")


class OrderHistoryView(LoginRequiredMixin, ListView):
    """
    Order history view
    """
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')


class OrderHistoryDetailView(LoginRequiredMixin, DetailView):
    """
    Order history detail view
    """
    model = Order
    template_name = 'orders/order_history_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


# Admin views
class AdminOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin order list view
    """
    model = Order
    template_name = 'orders/admin_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')


class AdminOrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Admin order detail view
    """
    model = Order
    template_name = 'orders/admin_order_detail.html'
    context_object_name = 'order'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AssignDeliveryAgentView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Assign delivery agent view
    """
    template_name = 'orders/assign_delivery_agent.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AdminOrderStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Admin order status update view
    """
    template_name = 'orders/admin_order_status_update.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# Order item views
class OrderItemListView(LoginRequiredMixin, ListView):
    """
    Order item list view
    """
    model = OrderItem
    template_name = 'orders/order_item_list.html'
    context_object_name = 'order_items'
    
    def get_queryset(self):
        order = get_object_or_404(Order, pk=self.kwargs['order_pk'])
        if order.customer == self.request.user or self.request.user.is_staff:
            return OrderItem.objects.filter(order=order)
        return OrderItem.objects.none()


class OrderItemAddView(LoginRequiredMixin, CreateView):
    """
    Order item add view
    """
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_add.html'
    
    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs['order_pk'])
        form.instance.order = order
        response = super().form_valid(form)
        messages.success(self.request, 'পণ্য সফলভাবে যোগ করা হয়েছে।')
        return response


class OrderItemEditView(LoginRequiredMixin, UpdateView):
    """
    Order item edit view
    """
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_edit.html'
    
    def get_queryset(self):
        return OrderItem.objects.filter(order__pk=self.kwargs['order_pk'])


class OrderItemDeleteView(LoginRequiredMixin, DeleteView):
    """
    Order item delete view
    """
    model = OrderItem
    template_name = 'orders/order_item_delete.html'
    
    def get_queryset(self):
        return OrderItem.objects.filter(order__pk=self.kwargs['order_pk'])
    
    def get_success_url(self):
        return reverse_lazy('orders:order_item_list', kwargs={'order_pk': self.kwargs['order_pk']})


# Order status views
class OrderStatusView(LoginRequiredMixin, DetailView):
    """
    Order status view
    """
    model = Order
    template_name = 'orders/order_status.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=self.request.user)


class OrderStatusUpdateView(LoginRequiredMixin, TemplateView):
    """
    Order status update view
    """
    template_name = 'orders/order_status_update.html'
    
    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'আপনার এই কাজ করার অনুমতি নেই।')
            return redirect('orders:order_list')
        
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        try:
            order = Order.objects.get(id=order_id)
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=f'Status changed from {old_status} to {new_status}',
                created_by=request.user
            )
            
            messages.success(request, f'অর্ডার #{order.order_number} এর স্ট্যাটাস সফলভাবে আপডেট করা হয়েছে।')
        except Order.DoesNotExist:
            messages.error(request, 'অর্ডার খুঁজে পাওয়া যায়নি।')
        except Exception as e:
            messages.error(request, f'একটি সমস্যা হয়েছে: {str(e)}')
        
        return redirect('orders:order_list')


# API View for Admin Order Status Update
@csrf_exempt
@require_http_methods(["POST"])
def admin_update_order_status(request):
    """
    API endpoint for admin to update order status (AJAX)
    """
    if not request.user.is_authenticated or not request.user.is_admin:
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        if not order_id or not new_status:
            return JsonResponse({'success': False, 'message': 'Order ID and status required'})
        
        order = Order.objects.get(id=order_id)
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=f'Status changed from {old_status} to {new_status} by admin',
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Order #{order.order_number} status updated to {order.get_status_display()}',
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'customer_name': order.customer.get_full_name() or order.customer.username,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.strftime('%d %b %Y, %I:%M %p')
            }
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# API View for Dashboard Data
@require_http_methods(["GET"])
def dashboard_data_api(request):
    """
    API endpoint to get dashboard data for real-time updates
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
    
    try:
        if request.user.is_admin:
            # Admin dashboard data
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Recent orders for admin
            recent_orders = Order.objects.all().order_by('-created_at')[:10]
            
            data = {
                'user_type': 'admin',
                'total_orders': Order.objects.count(),
                'pending_orders': Order.objects.filter(status='pending').count(),
                'confirmed_orders': Order.objects.filter(status='confirmed').count(),
                'completed_orders': Order.objects.filter(status='delivered').count(),
                'recent_orders': [
                    {
                        'id': order.id,
                        'order_number': order.order_number,
                        'customer_name': order.customer.get_full_name() or order.customer.username,
                        'status': order.status,
                        'status_display': order.get_status_display(),
                        'total_amount': str(order.total_amount),
                        'created_at': order.created_at.strftime('%d %b %Y, %I:%M %p')
                    } for order in recent_orders
                ]
            }
        else:
            # User dashboard data
            user_orders = Order.objects.filter(customer=request.user)
            recent_orders = user_orders.order_by('-created_at')[:5]
            
            data = {
                'user_type': 'user',
                'total_orders': user_orders.count(),
                'pending_orders': user_orders.filter(status='pending').count(),
                'completed_orders': user_orders.filter(status='delivered').count(),
                'cancelled_orders': user_orders.filter(status='cancelled').count(),
                'total_spent': str(Payment.objects.filter(
                    order__customer=request.user,
                    status='completed'
                ).aggregate(total=Sum('amount'))['total'] or 0),
                'recent_orders': [
                    {
                        'id': order.id,
                        'order_number': order.order_number,
                        'status': order.status,
                        'status_display': order.get_status_display(),
                        'total_amount': str(order.total_amount),
                        'created_at': order.created_at.strftime('%d %b %Y, %I:%M %p')
                    } for order in recent_orders
                ]
            }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# Real-time Order Creation API
@csrf_exempt
@require_http_methods(["POST"])
def create_order_from_cart(request):
    """
    Create order from cart data (AJAX endpoint)
    """
    print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
    print(f"DEBUG: User: {request.user}")
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Login required'}, status=401)
    
    try:
        data = json.loads(request.body)
        cart_items = data.get('cart_items', [])
        
        print(f"DEBUG: Cart items: {cart_items}")
        print(f"DEBUG: Data: {data}")
        
        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Cart is empty'})
        
        # Create order
        order = Order.objects.create(
            order_number=f'ORD{uuid.uuid4().hex[:8].upper()}',
            customer=request.user,
            delivery_address=data.get('delivery_address', ''),
            delivery_city=data.get('delivery_city', 'ঢাকা'),
            total_amount=Decimal('0.00'),
            status='pending',
            special_instructions=data.get('special_instructions', '')
        )
        
        total_amount = Decimal('0.00')
        out_of_stock_items = []
        
        # First pass: Check stock availability
        for item in cart_items:
            try:
                product = ProductService.objects.get(id=item['id'])
                quantity = int(item['quantity'])
                
                if not product.is_in_stock(quantity):
                    out_of_stock_items.append({
                        'name': product.name,
                        'requested': quantity,
                        'available': product.stock_quantity,
                        'status': product.get_stock_status()
                    })
            except ProductService.DoesNotExist:
                print(f"DEBUG: Product not found with ID: {item.get('id')}")
                return JsonResponse({'success': False, 'message': f'Product {item.get("id")} not found'})
        
        # If any items are out of stock, return error
        if out_of_stock_items:
            error_message = "নিম্নলিখিত পণ্যগুলি স্টকে নেই:\n"
            for item in out_of_stock_items:
                error_message += f"• {item['name']}: {item['status']}\n"
            return JsonResponse({
                'success': False, 
                'message': error_message,
                'out_of_stock_items': out_of_stock_items
            })
        
        # Second pass: Create order items and reduce stock
        for item in cart_items:
            try:
                product = ProductService.objects.get(id=item['id'])
                quantity = int(item['quantity'])
                unit_price = product.price
                item_total = unit_price * quantity
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=item_total
                )
                
                # Reduce stock
                product.reduce_stock(quantity)
                
                total_amount += item_total
                
            except ProductService.DoesNotExist:
                print(f"DEBUG: Product not found with ID: {item.get('id')}")
                continue
            except Exception as e:
                print(f"DEBUG: Error creating order item: {e}")
                continue
        
        # Update order total
        order.total_amount = total_amount
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order created from cart',
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Order created successfully',
            'order_id': order.id,
            'order_number': order.order_number,
            'total_amount': str(total_amount)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_product(request):
    """
    Add new product (Admin only)
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        product = ProductService.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            price=Decimal(data.get('price', '0.00')),
            category=data.get('category'),
            stock_quantity=int(data.get('stock_quantity', 0)),
            is_available=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Product added successfully',
            'product_id': product.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_product(request, product_id):
    """
    Update product (Admin only)
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)
    
    try:
        product = ProductService.objects.get(id=product_id)
        data = json.loads(request.body)
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = Decimal(data.get('price', str(product.price)))
        product.category = data.get('category', product.category)
        product.stock_quantity = int(data.get('stock_quantity', product.stock_quantity))
        product.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Product updated successfully'
        })
        
    except ProductService.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_product(request, product_id):
    """
    Delete product (Admin only)
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)
    
    try:
        product = ProductService.objects.get(id=product_id)
        product.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Product deleted successfully'
        })
        
    except ProductService.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)