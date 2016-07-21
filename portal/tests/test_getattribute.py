from collections import namedtuple
from django.test import TestCase
from django.template import Context, Template


class GetAttributeTestCase(TestCase):

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_get_attribute(self):
        # Handle dict
        rendered = self.render_template(
            '{% load getattribute %}'
            '{{ obj|getattribute:key }}',
            {'obj': {'foo': 'bar'}, 'key': 'foo'}
        )
        self.assertEqual(rendered, 'bar')

        # Handle object
        Obj = namedtuple('Obj', ['foo'])
        obj = Obj('bar')

        rendered = self.render_template(
            '{% load getattribute %}'
            '{{ obj|getattribute:key }}',
            {'obj': obj, 'key': 'foo'}
        )
        self.assertEqual(rendered, 'bar')
