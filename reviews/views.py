from django.shortcuts import render
from django.views.generic import TemplateView


class ReviewListView(TemplateView):
    """
    Review list view
    """
    template_name = 'reviews/review_list.html'