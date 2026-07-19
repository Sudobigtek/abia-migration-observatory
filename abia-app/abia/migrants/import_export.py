import csv
import io
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Migrant

def export_migrants_csv(queryset):
    """Export migrants to CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Full Name', 'Gender', 'Phone', 'Email', 'Nationality', 'State of Origin', 'LGA of Origin', 'Current LGA', 'Status', 'Created At'])
    for m in queryset:
        writer.writerow([
            str(m.id), m.full_name, m.gender, m.phone, m.email or '',
            m.nationality or '', m.state_of_origin or '', m.lga_of_origin or '',
            m.current_lga.name if m.current_lga else '', m.status,
            m.created_at.isoformat()
        ])
    return output.getvalue()

def export_migrants_excel(queryset):
    """Export migrants to Excel (placeholder - returns CSV for now)."""
    return export_migrants_csv(queryset)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def migrants_export(request):
    """Export migrants as CSV or Excel."""
    format_type = request.query_params.get('format', 'csv')
    status_filter = request.query_params.get('status')
    
    queryset = Migrant.objects.all()
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if format_type == 'csv':
        data = export_migrants_csv(queryset)
        response = HttpResponse(data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="migrants.csv"'
        return response
    else:
        return Response({'error': 'Format not supported yet'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def migrants_import(request):
    """Bulk import migrants from CSV."""
    if 'file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=400)
    
    file = request.FILES['file']
    decoded = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    created = 0
    errors = []
    for row in reader:
        try:
            Migrant.objects.create(
                full_name=row.get('Full Name', ''),
                gender=row.get('Gender', 'unknown'),
                phone=row.get('Phone', ''),
                email=row.get('Email', '') or None,
                nationality=row.get('Nationality', '') or None,
                status=row.get('Status', 'active')
            )
            created += 1
        except Exception as e:
            errors.append({'row': row, 'error': str(e)})
    
    return Response({
        'created': created,
        'errors': len(errors),
        'error_details': errors[:5]
    })
