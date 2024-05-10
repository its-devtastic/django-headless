from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Folder
from .serializers import FolderPathSerializer


class FolderPathView(APIView):
    queryset = Folder.objects.none()

    def get(self, request, *args, **kwargs):
        folder_id = request.query_params.get("folder", None)

        if not folder_id:
            return Response(data=[])

        try:
            folder = Folder.objects.get(pk=folder_id)
            path = []
            while folder:
                path.insert(0, folder)
                folder = folder.parent
            return Response(data=FolderPathSerializer(path, many=True).data)
        except Folder.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
