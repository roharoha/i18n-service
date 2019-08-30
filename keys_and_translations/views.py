import ast
import detectlanguage
import json
import re

from django.conf import settings
from django.http import HttpResponse
from django.db.models import F

from keys_and_translations.models import Key, Translation

detectlanguage.configuration.api_key = settings.DETECT_LANGUATE_KEY


def _json_resp(data):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type="application/json; encoding=utf-8")


# endpoints for keys
def _key_name_validator(name):
    """
    check whether name contains only lowercase alphabets and dot(.)s
    using regular expression.
    if match, return matched name,
    and not, return error HttpResponse
    :param name: 
    :return: 
    """
    pattern = re.compile('[a-z.]{1,255}')
    matcher = pattern.match(name)
    if matcher:
        return matcher.group()

    return None


def _key_get(request):
    """
    return all key list (id, name)
    :param request: 
    :return: 
    """
    keys = list(Key.objects.values('id', 'name'))
    return _json_resp({"keys": keys})


def _key_post(request):
    """
    if name value in body validate, add new key & return key (id, name)
    :param request: 
    :return: 
    """
    name = _key_name_validator(request.POST.get('name'))
    if name:
        new_key = Key(name=name)
        new_key.save()
        return _json_resp({"key": Key.objects.filter(id=new_key.id).values('id', 'name').first()})

    return _json_resp({"error": 'key name should be only lower case alphabet and dot(.)'})


def keys(request):
    """
    return appropriate values for each request method
    :param request: 
    :return: 
    """
    if request.method == 'GET':
        return _key_get(request)

    elif request.method == 'POST':
        return _key_post(request)


def key_update(request, keyId):
    """
    1. check request method is 'PUT'
    2. check key object to update exists
    3. check name value in body validate
    if all check are passed, update key name value
     
    :param request: 
    :param keyId: 
    :return: 
    """
    if request.method != 'PUT':
        return _json_resp({"error": 'key update could be only PUT request method.'})

    key_to_update = Key.objects.filter(id=keyId)
    if not key_to_update.exists():
        return _json_resp({"error": "key doesn't exist"})

    body = ast.literal_eval(request.body.decode(encoding='UTF-8'))
    name = _key_name_validator(body.get('name'))
    if name:
        key_to_update.update(name=name)
        return _json_resp({"key": Key.objects.filter(id=keyId).values('id', 'name').first()})

    return _json_resp({"error": 'key name should be only lower case alphabet and dot(.)'})


# endpoints for translations
def translations(request, keyId):
    """
    check request method is GET
    if GET, return translation list (id, key_id, locale, value)
    
    :param request: 
    :param keyId: 
    :return: 
    """
    if request.method != 'GET':
        return _json_resp({"error": 'translation list could be only GET request method.'})

    translations = list(Translation.objects.filter(
        key_id=keyId
    ).annotate(
        keyId=F('key__id')
    ).values('id', 'keyId', 'locale', 'value'))

    return _json_resp({"translations": translations})


def _translations_in_locale_get(request, keyId, locale):
    """
    return translation object which has same keyid and locale
    :param request: 
    :param keyId: 
    :param locale: 
    :return: 
    """
    return _json_resp({
        "translation": Translation.objects.filter(
            key_id=keyId, locale=locale
        ).annotate(
            keyId=F('key__id')
        ).values(
            'id', 'keyId', 'locale', 'value').first()})


def _translations_in_locale_post(request, keyId, locale):
    """
    1. check value in body exists
    2. check detected language locale is same with locale
    all check are passed, add new translate and return that.
    
    :param request: 
    :param keyId: 
    :param locale: 
    :return: 
    """
    value = request.POST.get('value')
    if not value:
        return _json_resp({"error": "translation value doesn't exist"})

    _locale = _language_detect(value)
    if _locale != locale:
        return _json_resp({"error": "translation locale is different"})

    new_translation = Translation(
        key=Key.objects.get(id=keyId),
        locale=locale,
        value=value
    )
    new_translation.save()
    return _json_resp({
        "translation": Translation.objects.filter(
            id=new_translation.id
        ).annotate(
            keyId=F('key__id')
        ).values('id', 'keyId', 'locale', 'value').first()})


def _translations_in_locale_put(request, keyId, locale):
    """
    1. check translation object to update exists
    2. check value in body exists
    all check are passed, update translation and return that.

    :param request: 
    :param keyId: 
    :param locale: 
    :return: 
    """
    translation_to_update = Translation.objects.filter(key__id=keyId, locale=locale)
    if not translation_to_update.exists():
        return _json_resp({"error": "translation doesn't exist"})

    body = ast.literal_eval(request.body.decode(encoding='UTF-8'))
    value = body.get('value')
    if not value:
        return _json_resp({"error": "translation value doesn't exist"})

    _locale = _language_detect(value)
    if _locale != locale:
        return _json_resp({"error": "translation locale is different"})

    translation_to_update.update(value=value)
    return _json_resp({
        "translation": translation_to_update.annotate(
            keyId=F('key__id')
        ).values('id', 'keyId', 'locale', 'value').first()})


def translations_in_locale(request, keyId, locale):
    """
    return appropriate values for each request method
    :param request: 
    :return: 
    """
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
        return _json_resp({"error": 'language detect could be only GET request method.'})

    message = request.GET.get('message')
    if not message:
        return _json_resp({"error": "nothing to detect"})

    return _json_resp({"locale": _language_detect(message)})
