import base64

from django.contrib.auth.hashers import check_password
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse, JsonResponse

from .models import User
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer
import json


def healthz(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="healthz",
            event="health check requested",
            message="service health check."
        )
        if request.method == 'GET':
            if request.body:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="healthz",
                    event="bad_request_body",
                    message="Bad request, body received for healthz endpoint."
                )
                return HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="healthz",
                    event="bad_query_parameter",
                    message="Bad query parameter received for healthz endpoint."
                )
                return HttpResponseBadRequest(status=400)
            else:
                logger.info(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="healthz",
                    event="service_health_check",
                    message="Service is healthy."
                )
                return HttpResponse(status=200)
        else:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="healthz",
                event="method_not_allowed",
                message="Method not allowed for healthz endpoint."
            )
            return HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="healthz",
            event="error_processing_healthz",
            message="An error occurred while processing healthz request.",
            exception=str(e)
        )
        return HttpResponseBadRequest(status=400)


def ping(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="ping",
            event="ping_accessed",
            message="Ping endpoint accessed."
        )
        if request.method == 'GET':
            if request.body:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="ping",
                    event="bad_request_body",
                    message="Bad request body received for ping endpoint."
                )
                return HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="ping",
                    event="bad_query_parameter",
                    message="Bad query parameter received for ping endpoint."
                )
                return HttpResponseBadRequest(status=400)
            else:
                logger.info(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="ping",
                    event="Ping successful",
                    message="service is healthy and ping successful."
                )
                return JsonResponse({'message': 'pong'}, status=200)
        else:
            logger.error(
                event="method_not_allowed",
                message=f"Method '{request.method}' not allowed for endpoint '{request.path}'.",
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="ping",
            event="error_processing_ping",
            message="An error occurred while processing ping request.",
            exception=str(e)
        )
        return HttpResponseBadRequest(status=400)


def create_user(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="create_user",
            event="create_user_attempt",
            message="Create user endpoint accessed."
        )
        if request.method == 'POST':
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="json_decode_error",
                    message="Error decoding JSON in create_user.",
                    exception=str(e)
                )
                return HttpResponseBadRequest(status=400)

            # Check if the user already exists
            if User.objects.filter(username=request_data.get('username')).exists():
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="user_already_exists",
                    message="User with this username already exists.",
                    username=request_data.get('username')
                )
                return JsonResponse({'error': 'User with this username already exists.'}, status=400)

            serializer = CreateUserSerializer(data=request_data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="user_created",
                    message="User created successfully.",
                    username=user.username,
                )
                return JsonResponse(serializer.data, status=201)
            else:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="serializer_errors",
                    message="Serializer errors in create_user.",
                    errors=serializer.errors,
                    request_data=request_data
                )
                return HttpResponseBadRequest(status=400)
        else:
            logger.error(
                event="method_not_allowed",
                message=f"Method '{request.method}' not allowed for endpoint '{request.path}'.",
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponseNotAllowed(['POST'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="create_user",
            event="create_user_error",
            message="An error occurred while processing create user request.",
            exception=str(e)
        )
        try:
            if "Table 'webApp.myapp_user' doesn't exist" in str(e):
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="database_error",
                    message="Database error occurred while processing create user request.",
                    exception=str(e)
                )
                return JsonResponse({'error': 'An internal server error occurred. Please try again later.'},
                                    status=500)
        except Exception as err:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="create_user",
                event="error_processing_database_error",
                message="Error processing database error in create_user.",
                exception=str(err)
            )
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="create_user",
            event="unknown_error",
            message="An error occurred while processing create user request.",
            exception=str(e)
        )
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
            logger.warn(
                method=request.method,
                request_id=request.request_id,
                endpoint="user_info",
                event="Fetching user detail failed",
                message=f"Authorisation failure for user: {username}"
            )
            return None
    except User.DoesNotExist:
        logger.warn(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="Fetching user detail failed",
            message=f"User: {username} not found."
        )
        return None


def user_info(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="get_user_info_accessed",
            message="Get user info endpoint accessed."
        )
        if request.method == 'GET' or request.method == 'PUT':
            user = get_user_from_credentials(request)
            if not user:
                return HttpResponse(status=401)

            if request.method == 'GET':
                if request.body:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="bad_request_body",
                        message="Bad request body received for get user info endpoint."
                    )
                    return HttpResponseBadRequest(status=400)
                elif request.GET:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="bad_query_parameter",
                        message="Bad query parameter received for get user info endpoint."
                    )
                    return HttpResponseBadRequest(status=400)
                else:
                    serializer = UserSerializer(user)
                    logger.info(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        user_name=user.username,
                        event="success event ",
                        message="user data fetched successfully."
                    )
                    return JsonResponse(serializer.data, status=200)
            elif request.method == 'PUT':
                if request.GET:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="bad_query_parameter",
                        message="Bad query parameter received for update user info endpoint."
                    )
                    return HttpResponseBadRequest(status=400)
                request_data = json.loads(request.body)

                # Check if any unexpected keys are present in request_data
                unexpected_keys = set(request_data.keys()) - {'first_name', 'last_name', 'password'}
                if unexpected_keys:
                    logger.warn(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="unexpected_keys",
                        message=f"Failed to update to user info for user: {user.username}",
                    )
                    return HttpResponseBadRequest(status=400)
                serializer = UpdateUserSerializer(user, data=request_data)
                if serializer.is_valid():
                    serializer.save()
                    logger.info(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        user_name=user.username,
                        event="success event ",
                        message="user data updated successfully."
                    )
                    return HttpResponse(status=204)
                else:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="serializer_errors",
                        message=f"Failed to update to user info for user: {user.username}",
                        errors=serializer.errors
                    )
                    return HttpResponseBadRequest(status=400)

        else:
            logger.error(
                event="method_not_allowed",
                message=f"Method '{request.method}' not allowed for '{request.path}'.",
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponseNotAllowed(['GET', 'PUT'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="error_processing_user_info",
            message="An error occurred while processing user info request.",
            exception=str(e)
        )
        try:
            if "Table 'webApp.myapp_user' doesn't exist" in str(e):
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="user_info",
                    event="database_error",
                    message="Database error occurred while processing user info request.",
                    exception=str(e)
                )
                return JsonResponse({'error': 'An internal server error occurred. Please try again later.'},
                                    status=500)
        except Exception as err:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="user_info",
                event="error_processing_database_error",
                message="Error processing database error in user_info.",
                exception=str(err)
            )
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="unknown_error",
            message="An error occurred while processing user info request.",
            exception=str(e)
        )
        return HttpResponseBadRequest(status=400)
