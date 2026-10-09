"""Identité visuelle et textuelle d'une instance (nom, couleurs, logo, accueil).

Les valeurs par défaut sont celles du Garage (client n°1) ; une autre instance les
surcharge via son `.env` (variables `BRAND_*`) et, pour les images, via le dossier
`branding/` (voir `settings.py`).
"""
import colorsys
import os

DEFAUTS = {
    'NAME': 'Le Garage',
    'COLOR_DARK': '#201e1f',
    'COLOR_ACCENT': '#80b048',
    'COLOR_ACCENT_DARK': '#6a9339',
    'LOGO': '',
    'ICON_DIR': '',
    'HERO_IMAGE': '',
    'CALENDAR_IMAGE': '',
    'HOME_TITLE': 'RESTEZ EN FORME',
    'HOME_TEXT': 'Venez pratiquer une activité sportive près de chez vous pour améliorer votre forme physique.',
}


def _hex_vers_rgb(couleur):
    couleur = couleur.lstrip('#')
    if len(couleur) == 3:
        couleur = ''.join(c * 2 for c in couleur)
    return tuple(int(couleur[i:i + 2], 16) for i in (0, 2, 4))


def assombrir(couleur, facteur=0.84):
    r, g, b = (v / 255 for v in _hex_vers_rgb(couleur))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l * facteur, s)
    return '#{:02x}{:02x}{:02x}'.format(round(r * 255), round(g * 255), round(b * 255))


ARTICLES = ('le', 'la', 'les', 'un', 'une', "l'", "l’", 'the')


def initiale(nom):
    """Première lettre significative du nom (sans article) : « Le Garage » -> « G »."""
    mots = nom.strip().split()
    while len(mots) > 1 and mots[0].lower() in ARTICLES:
        mots = mots[1:]
    nom_utile = mots[0] if mots else nom
    for article in ("l'", "l’"):
        if nom_utile.lower().startswith(article) and len(nom_utile) > len(article):
            nom_utile = nom_utile[len(article):]
    return nom_utile[:1].upper() or '?'


def charger_marque(environ=os.environ):
    marque = {cle: environ.get(f'BRAND_{cle}') or defaut for cle, defaut in DEFAUTS.items()}
    if not environ.get('BRAND_COLOR_ACCENT_DARK') and environ.get('BRAND_COLOR_ACCENT'):
        marque['COLOR_ACCENT_DARK'] = assombrir(marque['COLOR_ACCENT'])
    marque['COLOR_DARK_RGB'] = ', '.join(str(v) for v in _hex_vers_rgb(marque['COLOR_DARK']))
    marque['COLOR_ACCENT_RGB'] = ', '.join(str(v) for v in _hex_vers_rgb(marque['COLOR_ACCENT']))
    marque['INITIALE'] = initiale(marque['NAME'])
    marque['TEAM'] = f"L'équipe {marque['NAME']}"
    return marque
