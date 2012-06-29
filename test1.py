from collections import namedtuple

from gi.repository import Gtk


# drawing primites
Point = namedtuple('Point', ['x', 'y'])
Dimension = namedtuple('Dimension', ['w', 'y'])
Rectangle = namedtuple('Rectangle', ['x', 'y', 'w', 'h'])


class PhysicalKeyboardDescription(object):
    def __init__(self, name, width=44.0, height=13.5, default_gap=0.1,
                       default_keywidth=1.8, default_keyheight=1.8):
        self.name = name
        self.width = width
        self.height = height
        self.default_gap = default_gap
        self.default_keywidth = 1.8
        self.default_keyheight = 1.8
        self.keys = {}

    def add_key(self, label, x, y, width=None, height=None):
        self.keys[label] = {
            'x': x,
            'y': y,
            'width': width or self.default_keywidth,
            'height': height or self.default_keyheight
        }

    def add_row(self, x, y, keys):
        for i, k in enumerate(keys):
            self.add_key(
                label=k,
                x=x + i * (self.default_keywidth + self.default_gap),
                y=y,
            )


filco = PhysicalKeyboardDescription('Filco Majestouch')
filco.add_key('Esc', 0.5, 0.5)
filco.add_row(4.3, 0.5, ['F1', 'F2', 'F3', 'F4'])
filco.add_row(12.9, 0.5, ['F5', 'F6', 'F7', 'F8'])
filco.add_row(21.5, 0.5, ['F9', 'F10', 'F11', 'F12'])
filco.add_row(29.6, 0.5, ['PrintScreen\nSys Rq', 'ScrollLock', 'Pause'])

filco.add_row(0.5, 3.3, ['~\n`', '!\n1', '@\n2', '#\n3', '$\n4', '%\n5',
                          '^\n6', '&\n7', '*\n8', '(\n9', ')\n0', '_\n-',
                          '+\n='])
filco.add_key('Backspace', 25.2, 3.3, 3.5)


class KeyboardWidget(Gtk.Widget):
    FOREGROUND_COLOR = (0, 0, 0, 1)
    BACKGROUND_COLOR = (1, 1, 1, 1)
    STROKE_WIDTH = 0.03

    def __init__(self, pk, *args, **kwargs):
        super(KeyboardWidget, self).__init__(*args, **kwargs)
        self.set_has_window(False)
        self.pk = pk

        self.connect('draw', self.on_draw)

    def on_draw(self, _, cr):
        cr.set_source_rgba(*self.BACKGROUND_COLOR)
        cr.rectangle(0, 0,
                     self.get_allocated_width(), self.get_allocated_height())
        cr.fill()

        # set scaling such that keyboard fits widget
        # and we're drawing in virtual cm
        cr.scale(self.get_allocated_width() / self.pk.width,
                 self.get_allocated_height() / self.pk.height)

        cr.set_source_rgba(*self.FOREGROUND_COLOR)
        cr.set_line_width(self.STROKE_WIDTH)
        for label, key in self.pk.keys.iteritems():
            cr.save()
            cr.rectangle(key['x'], key['y'], key['width'], key['height'])
            cr.stroke()

            # keys text size is dependant on the key height
            cr.set_font_size(key['height'] / 2)

            # draw text
            #x_bearing, y_bearing, t_w, t_h = cr.text_extents(label)[:4]
            #cr.move_to(key['x'] + key['width'] * 0.25,
            #           key['y'] + key['height'] * 0.75)
            #if t_w > key['width'] / 2.0:
            #    factor = (key['width'] / 2.0) / t_w
            #    cr.scale(factor, factor)
            #cr.show_text(label)
            self._render_text_into_box(cr, 'foo', key['x'], key['y'],
            key['width'], key['height'])
            cr.restore()

    def _render_text_into_box(self, cr, text, x, y, w, h):
        """Tries to render a text with a context's current font size. If it is
        wider than the supplied box, scale the text down so that it fits
        exactly."""

        cr.save()
        x_bearing, y_bearing, t_w, t_h = cr.text_extents(text)[:4]

        cr.move_to(x, (y + h))

        if t_w > w:
            factor = w / t_w
            cr.scale(factor, factor)
            x_bearing, y_bearing, t_w, t_h = cr.text_extents(text)[:4]

        cr.show_text(text)
        cr.restore()


w = Gtk.Window()
w.connect("delete-event", Gtk.main_quit)
w.add(KeyboardWidget(filco))
w.show_all()

Gtk.main()
