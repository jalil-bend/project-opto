from django.db import models
from users.models import Patient, Professional

# Modèle pour les dossiers médicaux
class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        'users.Patient',
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    professional = models.ForeignKey(
        'users.Professional',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    details = models.TextField()
    file = models.FileField(upload_to='medical_records/%Y/%m/%d/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Dossier de {self.patient.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

# Modèle pour les images médicales
class MedicalImage(models.Model):
    CATEGORY_CHOICES = [
        ('topographie', 'Topographie'),
        ('oct', 'OCT'),
        ('lampe_a_fente', 'Lampe à fente'),
    ]

    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='images')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='medical_records/images/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'uploaded_at']

    def __str__(self):
        return f"{self.get_category_display()} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

# Modèle pour les ordonnances
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()

    def __str__(self):
        return f'Ordonnance pour {self.patient}'