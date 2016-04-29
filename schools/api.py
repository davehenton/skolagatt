from rest_framework import viewsets
from common.models import School
from .serializers import SchoolSerializer

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
