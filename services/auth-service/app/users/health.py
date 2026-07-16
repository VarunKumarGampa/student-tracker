from django.http import JsonResponse


def health_check(request):
    """
    Simple health check endpoint.
    Returns 200 if the service is running.
    Kubernetes calls this to decide if the pod
    should receive traffic.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'auth-service',
    })