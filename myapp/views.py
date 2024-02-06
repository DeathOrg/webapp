from django.db import connection
from django.db import IntegrityError
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer, CreateUserSerializer
import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


def healthz(request):
    try:
        logger.info('Healthz endpoint accessed.')
        if request.method == 'GET':
            if request.body:
                logger.error('Bad request body received for healthz endpoint.')
                return HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error('Bad query parameter received for healthz endpoint.')
                return HttpResponseBadRequest(status=400)
            else:
                try:
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    logger.info('Database connection successful.')
                    return HttpResponse(status=200)
                except Exception as e:
                    logger.error(f"Error connecting to database: {e}")
                    return HttpResponse(status=503)
        else:
            logger.error('Method not allowed for healthz endpoint.')
            return HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(f"An error occurred while processing request body: {e}")
        return HttpResponseBadRequest(status=400)


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
            return HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(f"An error occurred while processing request body: {e}")
        return HttpResponseBadRequest(status=400)


def create_user(request):
    try:
        if request.method == 'POST':
            logger.info('Create user endpoint accessed.')
            request_data = json.loads(request.body)
            logger.info(f'Request data: {request_data}')

            serializer = CreateUserSerializer(data=request_data)
            if serializer.is_valid():
                logger.info('Serializer is valid.')
                user = serializer.save()
                logger.info('User object created successfully.')
                logger.info(serializer.data)
                return JsonResponse(serializer.data, status=201)
            else:
                logger.error(f'Serializer errors: {serializer.errors}')
                return HttpResponseBadRequest(status=400)
        else:
            return HttpResponseNotAllowed(['POST'])
    except IntegrityError:
        logger.error('User with this email already exists.')
        return HttpResponseBadRequest(status=400)
    except Exception as e:
        logger.error(f"An error occurred while processing user info request: {e}")
        return HttpResponseBadRequest(status=400)

@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_info(request):
    try:
        logger.info('User info endpoint accessed.')
        logger.info(f'Requests: {request}')
        if request.method == 'GET':
            logger.info(f'Request user: {request.user}')
            user = request.user
            serializer = UserSerializer(user)
            return JsonResponse(serializer.data, status=200)
        elif request.method == 'PUT':
            user = request.user
            data = request.data  # Retrieve data from request.data
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info('User information updated successfully.')
                return JsonResponse(serializer.data, status=200)  # Return JsonResponse with status 200
            else:
                logger.error('Invalid data received for updating user information.')
                return HttpResponseBadRequest(status=400)
        else:
            logger.error('Method not allowed for user info endpoint.')
            return HttpResponseNotAllowed(['GET', 'PUT'])
    except Exception as e:
        logger.error(f"An error occurred while processing user info request: {e}")
        return HttpResponseBadRequest(status=400)
