from rest_framework import viewsets, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from celery.result import AsyncResult
from common.models  import School, Student
from .serializers   import SchoolSerializer
from django.db.models import Q


class SchoolViewSet(viewsets.ModelViewSet):
    queryset           = School.objects.all()
    serializer_class   = SchoolSerializer
    permission_classes = (permissions.IsAdminUser,)


class TaskMonitor(APIView):
	renderer_classes = (JSONRenderer, )

	def get(self, request, format=None):
		if 'job' in self.request.GET:
			job_id = self.request.GET.get('job')
		else:
			return Response({})

		job = AsyncResult(job_id)
		
		if job.state == 'PROGRESS':
			return Response(job.result)
		else:
			return Response(job.state)


class StudentSearch(APIView):
	renderer_classes = (JSONRenderer, )

	def get(self, request, format=None):
		if 'q' in self.request.GET:
			q = self.request.GET.get('q')
		else:
			return Response([])

		qs = Student.objects.filter(
			Q(ssn__icontains = q) | Q(name__icontains = q)
		).values('id', 'ssn', 'name', 'school__id').distinct().all()[:200]
		results = [ x for x in qs ]
		return Response(results)

