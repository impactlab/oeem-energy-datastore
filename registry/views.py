from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AnonymousUser

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import exceptions
from rest_framework import viewsets

from registry import models
from registry import serializers


class ConnectionViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = serializers.ConnectionSerializer
    queryset = models.Connection.objects.all().order_by('pk')


class RegistryConnectionTokenAuthentication(authentication.BaseAuthentication):

    keyword = 'Token'

    def authenticate(self, request):

        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header.'
                    ' Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header.'
                    ' Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            connection = models.Connection.objects.get(token=token)
        except:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return (AnonymousUser(), connection)


class RegistrySummary(APIView):

    authentication_classes = (RegistryConnectionTokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        connection = request.auth
        return Response(connection.summary_data())
