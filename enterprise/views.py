from django.shortcuts import render
from django.conf import settings
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger


from .models import News


class NewsView(ListView):
    model = News
    template_name = 'news.html'
    context_object_name = 'news'
    allow_empty = True
    paginate_by = 5
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)

        paginator = Paginator(context['news'], self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            news_page = paginator.page(page)
        except PageNotAnInteger:
            news_page = paginator.page(1)
        except EmptyPage:
            news_page = paginator.page(paginator.num_pages)

        context['products']  = news_page
        context['MEDIA_URL'] = settings.MEDIA_URL

        return context

