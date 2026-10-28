from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse

from .models import Review, ReviewHelpful, ReviewResponse, ReviewReport
from orders.models import Order, ProductService


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return bool(user.is_authenticated and (
            user.is_staff or
            user.is_superuser or
            getattr(user, 'user_type', None) == 'admin'
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Administrative access required.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class ReviewListView(ListView):
    """
    Public customer reviews directory.
    """
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 12

    def get_queryset(self):
        queryset = Review.objects.filter(is_public=True).select_related(
            'customer', 'product', 'order'
        ).order_by('-created_at')

        rating = self.request.GET.get('rating')
        if rating and rating.isdigit():
            queryset = queryset.filter(rating=int(rating))

        product_id = self.request.GET.get('product')
        if product_id and product_id.isdigit():
            queryset = queryset.filter(product_id=int(product_id))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rating_filter'] = self.request.GET.get('rating', '')
        context['products'] = ProductService.objects.filter(is_available=True)
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Submit a review for a delivered order.
    """
    model = Review
    fields = ['rating', 'title', 'comment']
    template_name = 'reviews/review_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs['order_pk'])
        self.product = get_object_or_404(ProductService, pk=kwargs['product_pk'])

        # Verify customer placed the order and it was delivered
        if self.order.customer != request.user:
            messages.error(request, 'You may only review products from your own orders.')
            return redirect('orders:order_list')

        if self.order.status != 'delivered':
            messages.error(request, 'Reviews can only be submitted after your order is successfully delivered.')
            return redirect('orders:order_detail', pk=self.order.pk)

        # Check if already reviewed
        if Review.objects.filter(customer=request.user, order=self.order, product=self.product).exists():
            messages.info(request, 'You have already submitted a review for this product.')
            return redirect('orders:order_detail', pk=self.order.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.order = self.order
        form.instance.product = self.product
        form.instance.is_verified = True
        form.instance.is_public = True
        response = super().form_valid(form)
        messages.success(self.request, 'Thank you! Your verified review has been published.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['product'] = self.product
        return context

    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.order.pk})


class AdminReviewModerationView(AdminRequiredMixin, ListView):
    """
    Admin moderation dashboard for all reviews.
    """
    model = Review
    template_name = 'reviews/admin_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 25

    def get_queryset(self):
        return Review.objects.all().select_related('customer', 'product', 'order').order_by('-created_at')

    def post(self, request, *args, **kwargs):
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')
        review = get_object_or_404(Review, id=review_id)

        if action == 'toggle_visibility':
            review.is_public = not review.is_public
            review.save()
            status_text = 'visible' if review.is_public else 'hidden'
            messages.success(request, f"Review #{review.id} is now {status_text}.")
        elif action == 'delete':
            review.delete()
            messages.success(request, f"Review #{review_id} has been permanently deleted.")

        return redirect('reviews:admin_review_list')
