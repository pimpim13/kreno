from django.test import SimpleTestCase, TestCase, override_settings

from config.branding import assombrir, charger_marque


class MarqueTests(SimpleTestCase):
    def test_defauts_reproduisent_le_garage(self):
        marque = charger_marque({})
        self.assertEqual(marque['NAME'], 'Le Garage')
        self.assertEqual(marque['COLOR_DARK'], '#201e1f')
        self.assertEqual(marque['COLOR_ACCENT'], '#80b048')
        self.assertEqual(marque['COLOR_DARK_RGB'], '32, 30, 31')
        self.assertEqual(marque['TEAM'], "L'équipe Le Garage")
        self.assertEqual(marque['COLOR_ACCENT_DARK'], '#6a9339')

    def test_surcharge_par_environnement(self):
        marque = charger_marque({'BRAND_NAME': 'Studio Zen', 'BRAND_COLOR_ACCENT': '#ff0000'})
        self.assertEqual(marque['NAME'], 'Studio Zen')
        self.assertEqual(marque['TEAM'], "L'équipe Studio Zen")
        self.assertEqual(marque['COLOR_ACCENT_DARK'], assombrir('#ff0000'))

    def test_valeur_vide_retombe_sur_le_defaut(self):
        self.assertEqual(charger_marque({'BRAND_NAME': ''})['NAME'], 'Le Garage')


class MarqueRenduTests(TestCase):
    def test_accueil_utilise_la_marque(self):
        marque = charger_marque({'BRAND_NAME': 'Studio Zen', 'BRAND_HOME_TITLE': 'RESPIREZ'})
        with override_settings(BRAND=marque):
            reponse = self.client.get('/')
        self.assertContains(reponse, '<title>Studio Zen</title>', html=True)
        self.assertContains(reponse, 'RESPIREZ')
        self.assertNotContains(reponse, 'Le Garage')

    def test_manifest_suit_la_marque(self):
        marque = charger_marque({'BRAND_NAME': 'Studio Zen', 'BRAND_COLOR_DARK': '#112233'})
        with override_settings(BRAND=marque):
            donnees = self.client.get('/manifest.webmanifest').json()
        self.assertEqual(donnees['name'], 'Studio Zen')
        self.assertEqual(donnees['theme_color'], '#112233')
        self.assertEqual(len(donnees['icons']), 2)


class FondsTests(TestCase):
    def test_sans_photo_le_fond_est_un_degrade_du_theme(self):
        with override_settings(BRAND=charger_marque({})):
            reponse = self.client.get('/')
        self.assertContains(reponse, '--fond-accueil: radial-gradient')
        self.assertNotContains(reponse, '.jpg\'')

    def test_photo_configuree(self):
        with override_settings(BRAND=charger_marque({'BRAND_HERO_IMAGE': 'img/logo-le-garage.jpg'})):
            reponse = self.client.get('/')
        self.assertContains(reponse, "--fond-accueil: url('/static/img/logo-le-garage.jpg')")


class LogoTests(TestCase):
    def test_initiale_ignore_les_articles(self):
        from config.branding import initiale
        self.assertEqual(initiale('Le Garage'), 'G')
        self.assertEqual(initiale("L'Atelier"), 'A')
        self.assertEqual(initiale('Studio Zen'), 'S')

    def test_sans_logo_monogramme_en_html(self):
        with override_settings(BRAND=charger_marque({})):
            reponse = self.client.get('/')
        self.assertContains(reponse, 'logo-lettre">G<')
        self.assertContains(reponse, 'href="/marque/icone-32.png"')

    def test_logo_configure(self):
        with override_settings(BRAND=charger_marque({'BRAND_LOGO': 'img/mon-logo.png'})):
            reponse = self.client.get('/')
        self.assertContains(reponse, '/static/img/mon-logo.png')
        self.assertNotContains(reponse, 'logo-lettre')

    def test_icone_generee(self):
        reponse = self.client.get('/marque/icone-192.png')
        self.assertEqual(reponse['Content-Type'], 'image/png')
        self.assertTrue(reponse.content.startswith(b'\x89PNG'))
        self.assertEqual(self.client.get('/marque/icone-99.png').status_code, 404)
        self.assertEqual(self.client.get('/favicon.ico').status_code, 302)
