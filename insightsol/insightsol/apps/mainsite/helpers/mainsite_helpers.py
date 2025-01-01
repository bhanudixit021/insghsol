from django.db.models import F, Func

class JSONBuildObject(Func):
    function = 'jsonb_build_object'
    template = "%(function)s('mime_type', %(expressions)s[0]::text, 'url', %(expressions)s[1]::text)"
