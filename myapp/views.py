from django.db import connection
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse, JsonResponse


def healthz(request):
    try:
        logger.info('Healthz endpoint accessed.')
        if request.method == 'GET':
            if request.body:
                logger.error('Bad request body received for healthz endpoint.')
                response = HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error('Bad query parameter received for healthz endpoint.')
                response = HttpResponseBadRequest(status=400)
            else:
                try:
                    # Check database connectivity
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    logger.info('Database connection successful.')
                    response = HttpResponse(status=200)
                except Exception as e:
                    logger.error(f"Error connecting to database: {e}")
                    # Return HTTP 503 Service Unavailable
                    response = HttpResponse(status=503)
        else:
            logger.error('Method not allowed for healthz endpoint.')
            response = HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(f"An error occurred while processing request body: {e}")
        response = HttpResponseBadRequest(status=400)

    return response


def ping(request):
    try:
        logger.info('Ping endpoint accessed.')
        if request.method == 'GET':
            if request.body:
                logger.error('Bad request body received for ping endpoint.')
                return HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error('Bad query parameter received for ping endpoint.')
                return HttpResponseBadRequest(status=400)
            else:
                return JsonResponse({'message': 'pong'}, status=200)
        else:
            response = HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(f"An error occurred while processing request body: {e}")
        response = HttpResponseBadRequest(status=400)

    return response
