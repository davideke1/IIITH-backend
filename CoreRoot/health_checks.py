# CoreRoot/health_checks.py

from django.http import JsonResponse
from django.db import connection
import redis

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            one = cursor.fetchone()[0]
            if one != 1:
                raise Exception("Database health check failed")

        # Check Redis connection
        redis_client = redis.Redis(host='redis', port=6379, db=0)
        if not redis_client.ping():
            raise Exception("Redis health check failed")

        return JsonResponse({"status": "ok"}, status=200)
    except redis.RedisError as re:
        return JsonResponse({"status": "error", "message": f"Redis error: {str(re)}"}, status=500)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"General error: {str(e)}"}, status=500)
