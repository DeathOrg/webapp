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
        # Check database connection before processing the request
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
        except DatabaseError:
            # If there's a database error, return a 503 response
            # return HttpResponseServerError("Database unavailable", status=503)
            return HttpResponse(status=503)

        # Proceed with processing the request
        response = self.get_response(request)

        return response
