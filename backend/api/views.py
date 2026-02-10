
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse
from .models import UploadRecord
from .serializers import UploadRecordSerializer
from .utils import process_csv_file, generate_pdf_report
from django.contrib.auth import authenticate
import base64

class UploadAPIView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        try:
            stats = process_csv_file(file_obj)
            
            # Save to DB
            record = UploadRecord.objects.create(
                filename=file_obj.name,
                summary_json=stats
            )
            
            # Maintain only last 5 records
            ids_to_keep = UploadRecord.objects.all().values_list('id', flat=True)[:5]
            UploadRecord.objects.exclude(id__in=ids_to_keep).delete()
            
            serializer = UploadRecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HistoryAPIView(APIView):
    def get(self, request):
        records = UploadRecord.objects.all()[:5]
        serializer = UploadRecordSerializer(records, many=True)
        return Response(serializer.data)

class PDFExportView(APIView):
    # Allow URL param auth for simple download links if needed, or stick to header
    permission_classes = [permissions.AllowAny] # We handle auth manually for browsers to click links

    def get(self, request, pk):
        # Manual Basic Auth check if passed via query params (browser link case)
        user_param = request.query_params.get('username')
        pass_param = request.query_params.get('password')
        
        user = None
        if user_param and pass_param:
            user = authenticate(username=user_param, password=pass_param)
        elif 'HTTP_AUTHORIZATION' in request.META:
            # Fallback to standard header
            pass
        else:
            # If not authenticated, reject
            if not request.user.is_authenticated:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            user = request.user

        if not user:
             return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            record = UploadRecord.objects.get(pk=pk)
            pdf_buffer = generate_pdf_report(record)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{record.id}.pdf"'
            return response
        except UploadRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
