#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PySide import QtGui, QtCore

from datafiles import PhysicalKeyboard


class KeyboardWidget(QtGui.QWidget):
    bgcolor = QtGui.QColor('white')
    kbcolor = QtGui.QColor('#cccccc')
    keycolor = QtGui.QColor('#eeeeee')
    keyframecolor = QtGui.QColor('#888888')
    font_family = 'Helvetia, Arial'
    margins = (10, 10, 10, 10)

    def __init__(self, parent=None):
        super(KeyboardWidget, self).__init__(parent)

    def set_keyboard(self, pk):
        self.pk = pk

    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)

        # fill background
        window_rect = p.window()
        p.fillRect(window_rect, self.bgcolor)

        # set coordinate transform
        kb_rect = self.pk.get_rect()

        scale_x = (window_rect.width() - self.margins[1] - self.margins[3])\
                  / kb_rect.width()
        scale_y = (window_rect.height() - self.margins[0] - self.margins[2])\
                  / kb_rect.height()
        p.translate(self.margins[1], self.margins[0])
        p.scale(scale_x, scale_y)

        # draw keyboard
        p.fillRect(kb_rect, self.kbcolor)

        # draw each key
        for key in self.pk.keys:
            # draw key
            p.save()
            p.setBrush(QtGui.QBrush(self.keycolor))
            pen = QtGui.QPen(0)
            pen.setColor(self.keyframecolor)
            p.setPen(pen)
            self._draw_shape(p, key.shape)
            p.restore()

            # draw text
            # lines on key defined by bounding box
            key_bbox = self._get_bounding_rect(key.shape)

            line1 = QtCore.QRectF(key_bbox.left() + key_bbox.width() * 0.15,
                                  key_bbox.top() + key_bbox.height() * 0.12,
                                  key_bbox.width() * 0.70,
                                  key_bbox.height() * 0.30)
            line2 = QtCore.QRectF(line1)
            line2.translate(0, key_bbox.height() * 0.38)
            if key.labels:
                self._draw_text_into_box(p, line1, key.labels[0])
            if len(key.labels) > 1:
                self._draw_text_into_box(p, line2, key.labels[1])

        # all done
        p.end()

    def _draw_shape(self, p, shape):
        if QtCore.QRectF == type(shape):
            p.drawRoundedRect(shape, 0.2, 0.2)
        else:
            raise TypeError("Don't know how to draw %r" % type(shape))

    def _draw_text_into_box(self, p, box, text):
        """tries to draw text into QRectF box. the text's baseline will be
        put onto the lower edge of the box. if the text does not fit into the
        box when using the box' height as the ascent, it will be proportionally
        scaled down."""
        p.save()

        abs_box = p.worldTransform().mapRect(box)
        p.setWorldMatrixEnabled(False)

        font = QtGui.QFont(self.font_family, 1)
        font.setPixelSize(abs_box.height())
        p.setFont(font)

        bounding_rect = p.fontMetrics().boundingRect(text)
        scale = abs_box.width() / bounding_rect.width()
        if scale < 1:
            font.setPixelSize(abs_box.height() * scale)
            p.setFont(font)

        #p.fillRect(abs_box, QtGui.QColor('cyan'))
        p.drawText(abs_box.bottomLeft(), text)
        p.restore()

    def _get_bounding_rect(self, shape):
        if QtCore.QRectF == type(shape):
            return shape
        raise TypeError("Don't know how to calculate bounding rect of %r" %
                        type(shape))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    kw = KeyboardWidget()
    kw.set_keyboard(PhysicalKeyboard.from_xml(sys.stdin))
    kw.show()
    sys.exit(app.exec_())
