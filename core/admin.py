from django.contrib import admin
from .models import Counselor, AssessmentQuestion, TemplateWellnessTask, AppointmentSlot
admin.site.register(AppointmentSlot)
admin.site.register(Counselor)
@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
	list_display = ('text', 'category')
	fields = ('text', 'category')
# admin.site.register(Appointment)  # Removed to prevent manual add/edit
# admin.site.register(PeerSupport)  # Removed to prevent admin from managing peer support
admin.site.register(TemplateWellnessTask)
