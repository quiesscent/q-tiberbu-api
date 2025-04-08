from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Appointment)
admin.site.register(Doctor)
admin.site.register(MedicalRecord)
admin.site.register(Patient)