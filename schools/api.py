from rest_framework import viewsets, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from celery.result import AsyncResult
from common.models  import School
from .serializers   import SchoolSerializer


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