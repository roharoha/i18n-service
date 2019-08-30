from django.db.models import F
from django.test import TestCase
from django.urls import reverse

from keys_and_translations.factories import KeyFactory, available_locale_and_message
from keys_and_translations.models import Key


class LanguageDetectRequestTestCase(TestCase):
    def test_language_detect_with_post_put(self):
        resp = self.client.post(reverse('language_detect'),
                                {'message': 'meaningless message'})
        self.assertEqual(resp.json().get('error'),
                         'language detect could be only GET request method.')

        resp = self.client.put(reverse('language_detect'),
                               {'message': 'meaningless message'})
        self.assertEqual(resp.json().get('error'),
                         'language detect could be only GET request method.')

    def test_language_detect(self):
        for locale, message in available_locale_and_message.items():
            resp = self.client.get(reverse('language_detect'),
                                   {'message': message})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json().get('locale'), locale)


class KeyRequestTestCase(TestCase):
    def setUp(self):
        KeyFactory.create_batch(size=5)
        self.keys_created = Key.objects.all()

    def test_key_get(self):
        resp = self.client.get(reverse('keys'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('keys'),
                         list(self.keys_created.values('id', 'name')))

    def test_key_post_with_invalid_name(self):
        resp = self.client.post(reverse('keys'),
                                {'name': 'THISISINVALIDKEYNAME'})
        self.assertEqual(resp.json().get('error'),
                         'key name should be only lower case alphabet and dot(.)')

    def test_key_post(self):
        resp = self.client.post(reverse('keys'),
                                {'name': 'this.is.valid.key.name'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('key').get('name'),
                         'this.is.valid.key.name')

    def test_key_update_with_get_post(self):
        resp = self.client.get(reverse('key_update',
                                       kwargs={'keyId': self.keys_created.first().id}))
        self.assertEqual(resp.json().get('error'),
                         'key update could be only PUT request method.')

        resp = self.client.post(reverse('key_update',
                                        kwargs={'keyId': self.keys_created.first().id}))
        self.assertEqual(resp.json().get('error'),
                         'key update could be only PUT request method.')

    def test_key_update_to_not_existing_key(self):
        resp = self.client.put(reverse('key_update',
                                       kwargs={'keyId': (self.keys_created.last().id + 1)}),
                               {'name': 'this.is.valid.key.name'})
        self.assertEqual(resp.json().get('error'),
                         "key doesn't exist")

    def test_key_update_with_invalid_name(self):
        resp = self.client.put(reverse('key_update',
                                       kwargs={'keyId': self.keys_created.last().id}),
                               {"name": "THISISINVALIDKEYNAME"})
        self.assertEqual(resp.json().get('error'),
                         'key name should be only lower case alphabet and dot(.)')

    def test_key_update(self):
        resp = self.client.put(reverse('key_update',
                                       kwargs={'keyId': self.keys_created.last().id}),
                               {'name': 'this.is.valid.key.name'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('key').get('name'),
                         'this.is.valid.key.name')


class TranslationRequestTestCase(TestCase):
    def setUp(self):
        self.key = KeyFactory()
        self.translations_created = self.key.translation_set.all()

    def test_translations_with_post_put(self):
        resp = self.client.post(reverse('translations',
                                        kwargs={'keyId': self.key.id}))
        self.assertEqual(resp.json().get('error'),
                         'translation list could be only GET request method.')

        resp = self.client.put(reverse('translations',
                                       kwargs={'keyId': self.key.id}))
        self.assertEqual(resp.json().get('error'),
                         'translation list could be only GET request method.')

    def test_translations(self):
        resp = self.client.get(reverse('translations',
                                       kwargs={'keyId': self.key.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('translations'),
                         list(self.translations_created.annotate(
                             keyId=F('key__id')
                         ).values('id', 'keyId', 'locale', 'value')))

    def test_translations_in_locale_get(self):
        for locale in ['ko', 'en', 'ja']:
            resp = self.client.get(reverse('translations_in_locale',
                                           kwargs={
                                               'keyId': self.key.id,
                                               'locale': locale,
                                           }))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json().get('translation'),
                             self.translations_created.filter(
                                 locale=locale
                             ).annotate(
                                 keyId=F('key__id')
                             ).values('id', 'keyId', 'locale', 'value').first())

    def test_translations_in_locale_post_without_value(self):
        resp = self.client.post(reverse('translations_in_locale',
                                        kwargs={
                                            'keyId': self.key.id,
                                            'locale': 'ko',
                                        }))
        self.assertEqual(resp.json().get('error'),
                         "translation value doesn't exist")

    def test_translations_in_locale_post_with_different_locale(self):
        resp = self.client.post(reverse('translations_in_locale',
                                        kwargs={
                                            'keyId': self.key.id,
                                            'locale': 'ko',
                                        }),
                                {'value': 'this is not ko locale'})
        self.assertEqual(resp.json().get('error'),
                         "translation locale is different")

    def test_translations_in_locale_post(self):
        for locale in ['ko', 'en', 'ja']:
            another_value_translation = self.translations_created.get(locale=locale)
            new_value = f'(new) {another_value_translation.value}'
            another_value_translation.delete()

            resp = self.client.post(reverse('translations_in_locale',
                                            kwargs={
                                                'keyId': self.key.id,
                                                'locale': locale,
                                            }),
                                    {'value': new_value})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json().get('translation').get('value'),
                             new_value)

    def test_translations_in_locale_put_without_value(self):
        resp = self.client.put(reverse('translations_in_locale',
                                       kwargs={
                                           'keyId': self.key.id,
                                           'locale': 'ko',
                                       }), {})
        self.assertEqual(resp.json().get('error'),
                         "translation value doesn't exist")

    def test_translations_in_locale_put_with_different_locale(self):
        resp = self.client.put(reverse('translations_in_locale',
                                       kwargs={
                                           'keyId': self.key.id,
                                           'locale': 'ko',
                                       }),
                               {'value': 'this is not ko locale'})
        self.assertEqual(resp.json().get('error'),
                         "translation locale is different")

    def test_translations_in_locale_put(self):
        for locale in ['ko', 'en', 'ja']:
            translation_to_update = self.translations_created.get(locale=locale)
            new_value = f'(new) {translation_to_update.value}'

            resp = self.client.put(reverse('translations_in_locale',
                                           kwargs={
                                               'keyId': self.key.id,
                                               'locale': locale,
                                           }),
                                   {'value': new_value})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json().get('translation').get('value'),
                             new_value)
