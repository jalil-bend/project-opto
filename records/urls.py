from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_record, name='upload_record'),
    path('upload/<int:patient_id>/', views.upload_record, name='upload_record_for_patient'),
    path('view/<int:patient_id>/', views.view_records, name='view_records'),
    path('my-records/', views.patient_records, name='patient_records'),  # Nouvelle URL pour les patients
    path('create-prescription/<int:patient_id>/', views.create_prescription, name='create_prescription'),  # Nouvelle URL pour créer une ordonnance
]