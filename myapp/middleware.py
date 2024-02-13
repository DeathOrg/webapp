# myapp/middleware.py
from django.db import connection, DatabaseError
from django.http import HttpResponseServerError, HttpResponse


class CustomHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class DatabaseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Check database connection before processing the request
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
        except DatabaseError as db_error:
            logger.error(f"Database error: {db_error}")
            return HttpResponse(status=503)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return HttpResponse(status=503)

        # Proceed with processing the request
        response = self.get_response(request)

        return response
