import detectlanguage
import re

from django.conf import settings
from django.http import JsonResponse

from keys_and_translations.models import Key, Translation

detectlanguage.configuration.api_key = settings.DETECT_LANGUATE_KEY


# endpoints for keys
def _key_name_validator(name):
    pattern = re.compile('[a-z.]{1,255}')
    matcher = pattern.match(name)
    if matcher:
        return matcher.group()
    return JsonResponse(data={"error": 'key name should be only lower case alphabet and dot(.)'})


def _key_get(request):
    keys = list(Key.objects.values('id', 'name'))
    return JsonResponse(data={"keys": keys})


def _key_post(request):
    name = _key_name_validator(request.POST.get('name'))

    if name:
        new_key = Key(name=name)
        new_key.save()
        return JsonResponse(data={
            "key": Key.objects.filter(id=new_key.id).values('id', 'name').first()})


def keys(request):
    if request.method == 'GET':
        return _key_get(request)

    elif request.method == 'POST':
        return _key_post(request)


def key_update(request, keyId):
    if request.method != 'PUT':
        return JsonResponse(data={"error": 'key update could be only PUT request method.'})

    key_to_update = Key.objects.filter(id=keyId)
    if not key_to_update.exists():
        return JsonResponse(data={"error": "key doesn't exist"})

    name = _key_name_validator(request.PUT.get('name'))
    if name:
        key_to_update.update(name=name)
        return JsonResponse(data={
            "key": Key.objects.filter(id=keyId).values('id', 'name').first()})


# endpoints for translations
def translations(request, keyId):
    if request.method != 'GET':
        return JsonResponse(data={"error": 'translation list could be only GET request method.'})

    translations = list(Translation.objects.filter(key_id=keyId)
                        .values('id', 'key_id', 'locale', 'value'))
    return JsonResponse(data={"translations": translations})


def _translations_in_locale_get(request, keyId, locale):
    return JsonResponse(data={
        "translation": Translation.objects.filter(
            key_id=keyId, locale=locale).values('id', 'key_id', 'locale', 'value').first()})


def _translations_in_locale_post(request, keyId, locale):
    value = request.POST.get('value')
    if not value:
        return JsonResponse(data={"error": "translation value doesn't exist"})

    locale = _language_detect(value)
    new_translation = Translation(
        key=Key.objects.get(id=keyId),
        locale=locale,
        value=value
    )
    new_translation.save()
    return JsonResponse(data={
        "translation": Translation.objects.filter(
            id=new_translation.id).values('id', 'key_id', 'locale', 'value').first()})


def _translations_in_locale_put(request, keyId, locale):
    translation_to_update = Translation.objects.filter(key__id=keyId, locale=locale)
    if not translation_to_update.exists():
        return JsonResponse(data={"error": "translation doesn't exist"})

    value = request.PUT.get('value')
    if not value:
        return JsonResponse(data={"error": "translation value doesn't exist"})

    translation_to_update.update(value=value)
    return JsonResponse(data={
        "translation": Translation.objects.filter(
            id=translation_to_update.id).values('id', 'key_id', 'locale', 'value').first()})


def translations_in_locale(request, keyId, locale):
    if request.method == 'GET':
        return _translations_in_locale_get(request, keyId, locale)

    if request.method == 'POST':
        return _translations_in_locale_post(request, keyId, locale)

    if request.method == 'PUT':
        return _translations_in_locale_put(request, keyId, locale)


def _language_detect(message):
    return detectlanguage.simple_detect(message)


def language_detect(request):
    if request.method != 'GET':
        return JsonResponse(data={"error": 'language detect could be only PUT request method.'})

    message = request.GET.get('message')
    if not message:
        return JsonResponse(data={"error": "nothing to detect"})

    return JsonResponse(data={"locale": _language_detect(message)})
