from django.urls import path

from equipment import views

urlpatterns = [
    path("", views.equipment_list, name="equipment_list"),
    path("<int:equipment_id>/", views.equipment_detail,
         name="equipment_detail"),
]
