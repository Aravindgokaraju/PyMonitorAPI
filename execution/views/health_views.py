from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..mongo_service import MongoService

@api_view(['GET'])
def test_mongo(request):
    try:
        mongo_service = MongoService()
        count = mongo_service.collection.count_documents({})
        return Response({"status": "success", "count": count})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy", "service": "backend"})