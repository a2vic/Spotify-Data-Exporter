"""
Utilitaires pour les appels à l'API Spotify.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, TypeVar

import spotipy
from spotipy.exceptions import SpotifyException

# Configurer le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type générique pour la fonction décorée
F = TypeVar('F', bound=Callable[..., Any])


def retry_on_api_error(
    func: Callable[[], Any],
    max_retries: int = 3,
    delay: int = 2,
    backoff_factor: float = 2.0,
    retry_on_status: Optional[list] = None
) -> Any:
    """
    Réessaie une fonction en cas d'erreur d'API.
    
    Args:
        func: Fonction à exécuter
        max_retries: Nombre maximum de tentatives
        delay: Délai initial entre les tentatives (en secondes)
        backoff_factor: Facteur multiplicatif pour augmenter le délai entre les tentatives
        retry_on_status: Liste des codes d'erreur HTTP à réessayer (par défaut: 429, 500, 502, 503, 504)
        
    Returns:
        Le résultat de la fonction
        
    Raises:
        SpotifyException: Si toutes les tentatives échouent
    """
    if retry_on_status is None:
        retry_on_status = [429, 500, 502, 503, 504]
        
    attempt = 0
    current_delay = delay
    
    while attempt < max_retries:
        try:
            return func()
        except SpotifyException as e:
            # Si c'est une erreur de rate limit ou une erreur serveur, réessayer
            if e.http_status in retry_on_status:
                attempt += 1
                
                # Si c'est la dernière tentative, lever l'exception
                if attempt >= max_retries:
                    logger.error(f"Échec après {max_retries} tentatives: {e}")
                    raise
                
                # Récupérer le délai Retry-After si disponible (pour les erreurs 429)
                retry_after = e.headers.get('Retry-After', current_delay) if hasattr(e, 'headers') else current_delay
                try:
                    retry_after = int(retry_after)
                except (ValueError, TypeError):
                    retry_after = current_delay
                
                logger.warning(
                    f"Erreur API (statut {e.http_status}), tentative {attempt}/{max_retries}. "
                    f"Nouvelle tentative dans {retry_after} secondes."
                )
                
                # Attendre avant de réessayer
                time.sleep(retry_after)
                
                # Augmenter le délai pour la prochaine tentative
                current_delay = current_delay * backoff_factor
            else:
                # Pour les autres erreurs, ne pas réessayer
                logger.error(f"Erreur API non récupérable (statut {e.http_status}): {e}")
                raise
        except Exception as e:
            # Pour les autres exceptions, ne pas réessayer
            logger.error(f"Exception non récupérable: {e}")
            raise


def rate_limit_decorator(max_retries: int = 3, delay: int = 2) -> Callable[[F], F]:
    """
    Décorateur pour gérer les limites de débit de l'API Spotify.
    
    Args:
        max_retries: Nombre maximum de tentatives
        delay: Délai initial entre les tentatives (en secondes)
        
    Returns:
        Fonction décorée
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_on_api_error(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay
            )
        return wrapper  # type: ignore
    return decorator
