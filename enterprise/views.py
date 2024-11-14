from contextlib import suppress
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListSerializer

from .models import News, Department
from .forms import DepartmentsForm
from .departments import СurrentDepartment


class DepartmentListSerializer(ListSerializer):

    def update(self, instance, validated_data):
        ret = []
        for item in validated_data:   
            department, _ = Department.objects.update_or_create(
                identifier_1C=item.pop('identifier_1C', ''),
                defaults = item
            )
            ret.append(department)
        return ret


class DepartmentSerializer(ModelSerializer):
    
    class Meta:
        model = Department
        fields = '__all__'
        list_serializer_class = DepartmentListSerializer


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_departments(request):
    serializer = DepartmentSerializer(instance='', data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def departments(request):
    if request.method == 'POST':
        department = СurrentDepartment(request)
        form = DepartmentsForm(request.POST)
        if form.is_valid():
            with suppress(Department.DoesNotExist): 
                department.update(
                    Department.objects.get(
                        id=form.cleaned_data.get('departments')
                ))
        return redirect("/catalog/products")
    else:
        form = DepartmentsForm()
    return render(request, 'forms/departments.html', {'form': form})
