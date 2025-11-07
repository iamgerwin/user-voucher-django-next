"""Health check views for monitoring and Docker health checks."""
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import time


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    """
    return Response({
        'status': 'healthy',
        'service': 'backend',
        'timestamp': time.time()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """
    Detailed health check endpoint.
    Checks database and cache connectivity.
    """
    health_status = {
        'status': 'healthy',
        'service': 'backend',
        'timestamp': time.time(),
        'checks': {}
    }

    overall_healthy = True

    # Check database connectivity
    try:
        connection.ensure_connection()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        overall_healthy = False
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }

    # Check cache connectivity
    try:
        cache_key = 'health_check'
        cache.set(cache_key, 'ok', 10)
        cache_value = cache.get(cache_key)

        if cache_value == 'ok':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache connection successful'
            }
        else:
            overall_healthy = False
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'message': 'Cache read/write failed'
            }
    except Exception as e:
        overall_healthy = False
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'message': f'Cache connection failed: {str(e)}'
        }

    # Update overall status
    if not overall_healthy:
        health_status['status'] = 'unhealthy'

    status_code = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(health_status, status=status_code)
