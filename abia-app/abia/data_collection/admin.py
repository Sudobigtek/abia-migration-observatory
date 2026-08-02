from django.contrib import admin
from django.http import HttpResponse
from .models import FormSubmission
import csv


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name}.csv'
    writer = csv.writer(response)
    fields = [f for f in opts.get_fields() if not f.many_to_many and not f.one_to_many]
    writer.writerow([f.verbose_name for f in fields])
    for obj in queryset:
        row = []
        for f in fields:
            v = getattr(obj, f.name)
            if callable(v):
                v = v()
            row.append(v)
        writer.writerow(row)
    return response

export_to_csv.short_description = 'Export selected to CSV'


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'form_type', 'title', 'created_at', 'synced_to_ncfrmi', 'synced_to_iom']
    list_filter = ['form_type', 'synced_to_ncfrmi', 'synced_to_iom', 'created_at']
    search_fields = ['title', 'form_type']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    actions = [export_to_csv]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            lga = request.user.userprofile.assigned_lga
            if lga:
                return qs.filter(data__lga__iexact=lga)
        except Exception:
            pass
        return qs.none()
