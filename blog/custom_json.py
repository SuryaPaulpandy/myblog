from django.core.signing import JSONSerializer
from datetime import datetime
from django.utils.timezone import is_aware


class CustomJSONSerializer(JSONSerializer):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
