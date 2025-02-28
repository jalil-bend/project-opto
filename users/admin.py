from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Professional, Patient, PatientProfessional, Researcher, ResearcherAccess

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_professional', 'is_patient', 'is_researcher', 'is_staff')
    list_filter = ('is_professional', 'is_patient', 'is_researcher', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_professional', 'is_patient', 'is_researcher', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_professional', 'is_patient', 'is_researcher'),
        }),
    )

class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number')
    search_fields = ('user__username', 'user__email', 'license_number')

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle création
            obj.user.is_professional = True
            obj.user.save()
        super().save_model(request, obj, form, change)

class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'access_code', 'get_accessed_professionals')
    search_fields = ('user__username', 'user__email', 'license_number', 'access_code')

    def get_accessed_professionals(self, obj):
        return ", ".join([p.user.get_full_name() for p in obj.accessed_codes.all()])
    get_accessed_professionals.short_description = 'Professionnels consultés'

class ResearcherAccessAdmin(admin.ModelAdmin):
    list_display = ('researcher', 'professional', 'access_date')
    list_filter = ('access_date',)
    search_fields = ('researcher__user__username', 'professional__user__username')



admin.site.register(User, CustomUserAdmin)
admin.site.register(Professional, ProfessionalAdmin)
admin.site.register(Researcher, ResearcherAdmin)
admin.site.register(ResearcherAccess, ResearcherAccessAdmin)
