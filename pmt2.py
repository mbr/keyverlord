import sys
from xml.etree import cElementTree as ET

from PySide import QtCore


def first_valid(*args):
    for a in args:
        if None != a:
            return a


def read_xml_shape(elem, context={}):

    if elem.tag == 'rect':
        x = float(first_valid(elem.attrib.get('x'), context.get('rect-x')))
        y = float(first_valid(elem.attrib.get('y'), context.get('rect-y')))
        w = float(first_valid(elem.attrib.get('w'), context.get('rect-w')))
        h = float(first_valid(elem.attrib.get('h'), context.get('rect-h')))

        return QtCore.QRectF(x, y, w, h)

    raise ValueError('Unknown shape %s' % elem.tag)


def read_xml_key(elem, context={}):
    return Key(
        keycode=int(elem.attrib['keycode']),
        labels=[l.text for l in elem.iterfind('label')],
        shape=read_xml_shape(elem.find('shape')[0], context)
    )


class PhysicalKeyboard(object):
    default_headers = {
        'name': u'Unnamed keyboard',
        'default-key-gap': 0.1,
        'default-key-width': 1.8,
        'default-key-height': 1.8
    }

    def __init__(self, headers, keys):
        self.headers = headers
        self.keys = keys

        self.update_keys()

    def update_keys(self):
        self._keycode_keys = {key.keycode: key for key in self.keys}

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.headers,
                               self.keys)

    @classmethod
    def from_xml(cls, source):
        headers = cls.default_headers.copy()

        keys = []

        et = ET.parse(source)
        root = et.getroot()

        # parse config
        for conf in root.find('head'):
            name = conf.attrib.get('name')
            value = type(cls.default_headers.get(name, u''))(conf.text)

            headers[name] = value

        context = {
            'rect-w': headers['default-key-width'],
            'rect-h': headers['default-key-height']
        }

        for rule in root.find('keys'):
            if rule.tag == 'key':
                keys.append(read_xml_key(rule, context))
            elif rule.tag == 'row':
                row_context = context.copy()
                row_context['rect-x'] = float(rule.attrib['x'])
                row_context['rect-y'] = float(rule.attrib['y'])

                for k in rule.iterfind('key'):
                    key = read_xml_key(k, row_context)
                    keys.append(key)
                    row_context['rect-x'] += headers['default-key-gap'] +\
                                             key.get_width()

        return cls(headers, keys)


class Key(object):
    def __init__(self, keycode, labels, shape):
        self.keycode = keycode
        self.labels = labels
        self.shape = shape

    def get_width(self):
        return self.shape.width()

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.keycode,
                                   self.labels,
                                   self.shape)


kb = PhysicalKeyboard.from_xml(sys.stdin)
print kb
