from random import choice

import factory.fuzzy
from factory import DjangoModelFactory
from faker import Faker

faker = Faker()
available_locale_and_message = {
    'ko': '테스트용 메시지입니다.',
    'en': 'this is message for test',
    'ja': 'これはテスト用のメッセージです',
}


class BaseKeyFactory(DjangoModelFactory):
    class Meta:
        model = 'keys_and_translations.Key'

    name = factory.sequence(lambda n: f'test.key.name.{n}')


class BaseTranslationFactory(DjangoModelFactory):
    class Meta:
        model = 'keys_and_translations.Translation'

    key = factory.SubFactory(BaseKeyFactory)
    locale = choice(list(available_locale_and_message.keys()))
    value = available_locale_and_message.get(locale)


class KeyFactory(BaseKeyFactory):
    @factory.post_generation
    def translation(self, create, extracted=None, **kwargs):
        if not create or extracted:
            return
        else:
            for locale, message in available_locale_and_message.items():
                BaseTranslationFactory(key=self,
                                       locale=locale,
                                       value=f'{self.id} {message}')
