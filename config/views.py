import io

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.templatetags.static import static
from PIL import Image, ImageDraw, ImageFont

from config.branding import _hex_vers_rgb

TAILLES_ICONE = (16, 32, 180, 192, 512)


def _url_icone(taille, nom_fichier):
    """Icône fournie par l'instance (BRAND_ICON_DIR) ou monogramme généré."""
    dossier = settings.BRAND['ICON_DIR']
    if dossier:
        return static(f'{dossier}/{nom_fichier}')
    return f'/marque/icone-{taille}.png'


def icone(request, taille):
    """Monogramme (initiale du nom, couleur d'accent sur fond sombre) généré à la volée."""
    if taille not in TAILLES_ICONE:
        raise Http404
    marque = settings.BRAND
    image = Image.new('RGB', (taille, taille), _hex_vers_rgb(marque['COLOR_DARK']))
    police = ImageFont.load_default(size=int(taille * 0.7))
    ImageDraw.Draw(image).text(
        (taille / 2, taille / 2), marque['INITIALE'], font=police,
        fill=_hex_vers_rgb(marque['COLOR_ACCENT']), anchor='mm',
    )
    tampon = io.BytesIO()
    image.save(tampon, format='PNG')
    reponse = HttpResponse(tampon.getvalue(), content_type='image/png')
    reponse['Cache-Control'] = 'public, max-age=3600'
    return reponse


def manifest(request):
    """Manifeste PWA généré à partir de l'identité de l'instance."""
    marque = settings.BRAND
    icones = [
        {'src': _url_icone(t, f'icon-{t}.png'), 'sizes': f'{t}x{t}', 'type': 'image/png'}
        for t in (192, 512)
    ]
    return JsonResponse(
        {
            'name': marque['NAME'],
            'short_name': marque['NAME'],
            'start_url': '/',
            'display': 'standalone',
            'background_color': marque['COLOR_DARK'],
            'theme_color': marque['COLOR_DARK'],
            'icons': icones,
        },
        content_type='application/manifest+json',
        json_dumps_params={'ensure_ascii': False},
    )
