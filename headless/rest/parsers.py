from djangorestframework_camel_case.parser import CamelCaseJSONParser
from rest_framework.parsers import MultiPartParser


class DefaultJSONParser(CamelCaseJSONParser):
    pass


class DefaultMultiPartParser(MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        return super().parse(stream, media_type, parser_context)
