from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_patient
from .views import change_password_professional, change_password_patient
from .views import admin_dashboard  # Import the admin_dashboard view
from .views import CustomLoginView  # Import the CustomLoginView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('grant-access/', views.grant_access, name='grant_access'),
    path('mes-dossiers/', views_patient.patient_records, name='patient_records'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('patient/<int:patient_id>/profile/', views.patient_profile, name='patient_profile'),
    path('terms-and-conditions/', views.TermsAndConditions, name='terms-and-conditions'),
    path('chat/<int:discussion_id>/', views.chat_view, name='chat'),
    path('chat/upload/', views.upload_file, name='chat_upload'),
    path('discussions/', views.discussions_list, name='discussions_list'),
    path('discussions/create/<int:user_id>/', views.create_discussion, name='create_discussion'),
    path('change-password-professional/', change_password_professional, name='change_password_professional'),
    path('change-password-patient/', change_password_patient, name='change_password_patient'),
    path('submit_contact/', views.contact_view, name='contact'),  # Ajout du chemin pour le formulaire de contact
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),  # Add the route for the admin dashboard
    path('add-user/', views.add_user, name='add_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('view-user/<int:user_id>/', views.view_user, name='view_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('professional-dashboard/', views.professional_dashboard, name='professional_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('researcher/access/', views.researcher_access, name='researcher_access'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('researcher/dashboard/', views.researcher_dashboard, name='researcher_dashboard'),
    path('access-records/', views.access_patient_records, name='access_patient_records'),
    path('access-projects/', views.view_patient_records, name='view_patient_records'),
    path('consult_data/', views.consult_data, name='consult_data'),
    path('researcher/dashboard/', views.researcher_dashboard, name='researcher_dashboard'),
    path('view-patient-records/', views.view_patient_records, name='view_patient_records'),
]
