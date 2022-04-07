from django.urls import path

from . import views
from . import views_generate_report

urlpatterns = [
    path('json_data/', views.json_data.as_view()),
    path('customer_data/', views.customer_data.as_view()),
    path('generate_report/', views_generate_report.generate_report.as_view()),
    path('generate_specific_report/', views_generate_report.generate_specific_report.as_view()),

]
