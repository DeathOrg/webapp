import base64

from django.db import connection
from django.db import IntegrityError
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse, JsonResponse

from .models import User
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer
import json


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


def get_user_from_credentials(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        return None, None

    encoded_credentials = auth_header[len('Basic '):]
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded_credentials.split(':', 1)

    try:
        user = User.objects.get(username=username)
        return user, password
    except User.DoesNotExist:
        return None, None


def user_info(request):
    try:
        if request.method == 'GET' or request.method == 'PUT':
            user, password = get_user_from_credentials(request)
            if not user or password != user.password:
                return HttpResponse(status=401)

            if request.method == 'GET':
                if request.body:
                    logger.error('Bad request body received for get user info endpoint.')
                    return HttpResponseBadRequest(status=400)
                elif request.GET:
                    logger.error('Bad query parameter received for get user info endpoint.')
                    return HttpResponseBadRequest(status=400)
                else:
                    serializer = UserSerializer(user)
                    return JsonResponse(serializer.data, status=200)
            elif request.method == 'PUT':
                if request.GET:
                    logger.error('Bad query parameter received for update user info endpoint.')
                    return HttpResponseBadRequest(status=400)
                request_data = json.loads(request.body)
                if not request_data.get('username') or request_data.get('username') != user.username:
                    return HttpResponseBadRequest(status=400)
                request_data.pop('username', None)
                # Check if any unexpected keys are present in request_data
                unexpected_keys = set(request_data.keys()) - {'first_name', 'last_name', 'password'}
                if unexpected_keys:
                    logger.error(f'Got unexpected keys: {unexpected_keys}')
                    return HttpResponseBadRequest(status=400)
                serializer = UpdateUserSerializer(user, data=request_data)
                if serializer.is_valid():
                    serializer.save()
                    return HttpResponse(status=204)
                else:
                    return HttpResponseBadRequest(status=400)

        else:
            return HttpResponseNotAllowed(['GET', 'PUT'])

    except Exception as e:
        logger.error(f"An error occurred while processing user info request: {e}")
        return HttpResponseBadRequest(status=400)
