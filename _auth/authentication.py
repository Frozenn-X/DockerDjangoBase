from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import AuthToken


class TokenAuthentication(BaseAuthentication):
    """
    Authentification personnalisée basée sur les tokens.
    Format de l'en-tête: Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    """
    keyword = 'Token'
    model = AuthToken

    def get_authorization_header(self, request):
        """
        Extraire l'en-tête d'autorisation et le renvoyer sous forme de chaîne
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode('iso-8859-1')
        return auth

    def authenticate(self, request):
        """
        Authentifier l'utilisateur en fonction de son token
        """
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Header d\'autorisation invalide. Aucune information d\'identification fournie.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Header d\'autorisation invalide. Format des informations d\'identification invalide.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Header d\'autorisation invalide. Le token ne peut pas être décodé.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        """
        Valider le token et renvoyer l'utilisateur
        """
        user = AuthToken.get_user_from_token(key)
        
        if user is None:
            raise exceptions.AuthenticationFailed(_('Token invalide ou expiré.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('Utilisateur inactif ou supprimé.'))

        return (user, key)

    def authenticate_header(self, request):
        """
        Renvoyer une chaîne à utiliser comme valeur de l'en-tête WWW-Authenticate
        """
        return self.keyword 