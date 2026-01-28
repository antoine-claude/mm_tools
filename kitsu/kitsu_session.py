import bpy
from typing import Optional, Dict
from . import prefs

class KitsuSession:
    """Classe pour gérer la session Kitsu et la persistance."""

    def __init__(self):
        self._session = None

    def login(self, email: str, password: str, host: str) -> bool:
        """Connexion à Kitsu."""
        try:
            # Logique de connexion (à adapter selon votre API)
            self._session = {"email": email, "password": password, "host": host}
            return True
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False

    def logout(self) -> None:
        """Déconnexion de Kitsu."""
        self._session = None

    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est connecté."""
        return self._session is not None

    def get_session_data(self) -> Optional[Dict]:
        """Retourne les données de la session."""
        return self._session

# Instance globale de la session
kitsu_session = KitsuSession()

def auto_login():
    """Tente de se reconnecter automatiquement au démarrage."""
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.is_logged_in and prefs.email and prefs.password:
        kitsu_session.login(prefs.email, prefs.password, prefs.host)
