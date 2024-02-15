import base64

from django.contrib.auth.hashers import check_password
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
                return HttpResponse(status=200)
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
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
                return HttpResponseBadRequest(status=400)

            logger.info(f'Request data: {request_data}')

            # Check if the user already exists
            if User.objects.filter(username=request_data.get('username')).exists():
                logger.error('User with this username already exists.')
                return JsonResponse({'error': 'User with this username already exists.'}, status=400)

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
    except Exception as e:
        logger.error(f"Some error occurred: {e}")
        try:
            if "Table 'webApp.myapp_user' doesn't exist" in str(e):
                logger.error(f"Database error occurred while processing create user request: {e}")
                return JsonResponse({'error': 'An internal server error occurred. Please try again later.'},
                                    status=500)
        except Exception as eee:
            logger.error(f"something bad happened while processing the error: {eee}")
        logger.error(f"An error occurred while processing create user request: {e}")
        return HttpResponseBadRequest(status=400)


def get_user_from_credentials(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        return None

    encoded_credentials = auth_header[len('Basic '):]
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded_credentials.split(':', 1)

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            return user
        else:
            return None
    except User.DoesNotExist:
        return None


def user_info(request):
    try:
        if request.method == 'GET' or request.method == 'PUT':
            user = get_user_from_credentials(request)
            if not user:
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
                    logger.error(f'serializer.errors {serializer.errors}')
                    return HttpResponseBadRequest(status=400)

        else:
            return HttpResponseNotAllowed(['GET', 'PUT'])
    except Exception as e:
        logger.error(f"Some error occurred: {e}")
        try:
            if "Table 'webApp.myapp_user' doesn't exist" in str(e):
                logger.error(f"Database error occurred while processing user info request: {e}")
                return JsonResponse({'error': 'An internal server error occurred. Please try again later.'},
                                    status=500)
        except Exception as eee:
            logger.error(f"something bad happened while processing the error: {eee}")
        logger.error(f"An error occurred while processing user info request: {e}")
        return HttpResponseBadRequest(status=400)
