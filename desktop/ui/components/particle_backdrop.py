"""Gothic ambient particle backdrop with animated cathedral Rose Window and rising embers."""

import math
import random
from typing import List

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget


class GothicEmber:
    """Represents a rising crimson ember or ethereal mist particle."""

    def __init__(self, width: float, height: float):
        self.x = random.uniform(0, max(width, 100))
        self.y = random.uniform(0, max(height, 100))
        self.radius = random.uniform(1.2, 3.4)
        self.vx = random.uniform(-0.35, 0.35)
        self.vy = random.uniform(-0.4, -0.9)
        self.particle_type = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
        self.base_alpha = random.uniform(0.3, 0.8)
        self.flicker_phase = random.uniform(0, 2 * math.pi)
        self.flicker_speed = random.uniform(0.03, 0.08)

    def update(self, width: float, height: float) -> None:
        self.x += self.vx + 0.15 * math.sin(self.flicker_phase)
        self.y += self.vy
        self.flicker_phase += self.flicker_speed

        if self.y < 0:
            self.y = height + random.uniform(5, 20)
            self.x = random.uniform(0, width)
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0

    @property
    def current_alpha(self) -> float:
        return max(0.15, min(0.95, self.base_alpha + 0.25 * math.sin(self.flicker_phase * 1.5)))


class ParticleBackdropWidget(QWidget):
    """Gothic ambient canvas with animated sacred Rose Window geometry and rising embers."""

    def __init__(self, num_particles: int = 42, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self._num_particles = num_particles
        self._embers: List[GothicEmber] = []
        self._initialized = False
        self._rose_angle = 0.0

        # 30 FPS smooth rendering loop
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(33)

    def _init_embers(self) -> None:
        w = float(self.width()) or 1440.0
        h = float(self.height()) or 900.0
        self._embers = [GothicEmber(w, h) for _ in range(self._num_particles)]
        self._initialized = True

    def _on_tick(self) -> None:
        if not self._initialized and self.width() > 10:
            self._init_embers()

        # Slow ambient rotation of sacred geometry
        self._rose_angle += 0.0018
        if self._rose_angle > 2 * math.pi:
            self._rose_angle -= 2 * math.pi

        w = float(self.width())
        h = float(self.height())
        for e in self._embers:
            e.update(w, h)

        self.update()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._initialized:
            self._init_embers()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()

        # 1. Deep Obsidian Gothic Base (#030408)
        painter.fillRect(0, 0, w, h, QColor(4, 3, 7, 255))

        # 2. Draw Gothic Rose Windows (Sacred Geometry Watermarks)
        self._draw_gothic_rose_window(painter, w * 0.72, h * 0.45, radius=260.0, angle=self._rose_angle, alpha=28)
        self._draw_gothic_rose_window(painter, w * 0.18, h * 0.85, radius=160.0, angle=-self._rose_angle * 1.3, alpha=20)
        self._draw_alchemy_circle(painter, w * 0.90, h * 0.12, radius=120.0, angle=self._rose_angle * 0.8, alpha=24)

        # 3. Connections between nearby embers
        connection_dist = 110.0
        count = len(self._embers)

        for i in range(count):
            e1 = self._embers[i]
            for j in range(i + 1, count):
                e2 = self._embers[j]
                dx = e1.x - e2.x
                dy = e1.y - e2.y
                dist = math.hypot(dx, dy)
                if dist < connection_dist:
                    factor = 1.0 - (dist / connection_dist)
                    alpha = int(factor * 35)
                    pen = QPen(QColor(190, 18, 60, alpha), 1.0)
                    painter.setPen(pen)
                    painter.drawLine(QPointF(e1.x, e1.y), QPointF(e2.x, e2.y))

        # 4. Glowing Embers
        for e in self._embers:
            alpha = int(e.current_alpha * 255)

            if e.particle_type == 0:  # Crimson Ember
                core_color = QColor(251, 113, 133, alpha)
                halo_color = QColor(225, 29, 72, int(alpha * 0.28))
            elif e.particle_type == 1:  # Violet Mist
                core_color = QColor(216, 180, 254, alpha)
                halo_color = QColor(147, 51, 234, int(alpha * 0.22))
            else:  # Burnished Gold
                core_color = QColor(253, 230, 138, alpha)
                halo_color = QColor(217, 119, 6, int(alpha * 0.30))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_color))
            painter.drawEllipse(QPointF(e.x, e.y), e.radius * 2.4, e.radius * 2.4)

            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QPointF(e.x, e.y), e.radius, e.radius)

        painter.end()

    def _draw_gothic_rose_window(
        self, painter: QPainter, cx: float, cy: float, radius: float, angle: float, alpha: int
    ) -> None:
        """Renders an intricate Gothic Cathedral Rose Window (Rosetón Gótico) with 12 petals."""
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(angle))

        pen_crimson = QPen(QColor(225, 29, 72, alpha), 1.2)
        pen_gold = QPen(QColor(245, 158, 11, int(alpha * 0.8)), 1.0)
        pen_thin = QPen(QColor(136, 19, 55, int(alpha * 0.6)), 0.8)

        # Concentric Outer Rings
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen_crimson)
        painter.drawEllipse(QPointF(0, 0), radius, radius)
        painter.drawEllipse(QPointF(0, 0), radius * 0.94, radius * 0.94)
        painter.drawEllipse(QPointF(0, 0), radius * 0.70, radius * 0.70)
        painter.drawEllipse(QPointF(0, 0), radius * 0.38, radius * 0.38)
        painter.drawEllipse(QPointF(0, 0), radius * 0.16, radius * 0.16)

        # 12 Cathedral Lancets / Petals
        num_petals = 12
        petal_r = radius * 0.28
        for i in range(num_petals):
            a = (2 * math.pi / num_petals) * i
            px = math.cos(a) * (radius * 0.68)
            py = math.sin(a) * (radius * 0.68)

            painter.setPen(pen_gold)
            painter.drawEllipse(QPointF(px, py), petal_r, petal_r)

            # Radial spokes
            sx1 = math.cos(a) * (radius * 0.16)
            sy1 = math.sin(a) * (radius * 0.16)
            sx2 = math.cos(a) * radius
            sy2 = math.sin(a) * radius
            painter.setPen(pen_thin)
            painter.drawLine(QPointF(sx1, sy1), QPointF(sx2, sy2))

        # Inner Quadrafoil
        num_inner = 6
        inner_r = radius * 0.12
        for j in range(num_inner):
            ia = (2 * math.pi / num_inner) * j + (math.pi / 6)
            ix = math.cos(ia) * (radius * 0.24)
            iy = math.sin(ia) * (radius * 0.24)
            painter.setPen(pen_crimson)
            painter.drawEllipse(QPointF(ix, iy), inner_r, inner_r)

        painter.restore()

    def _draw_alchemy_circle(
        self, painter: QPainter, cx: float, cy: float, radius: float, angle: float, alpha: int
    ) -> None:
        """Renders an intricate celestial alchemy circle with gothic octagram."""
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(angle))

        pen_gold = QPen(QColor(217, 119, 6, alpha), 1.0)
        pen_crimson = QPen(QColor(190, 18, 60, int(alpha * 0.7)), 0.8)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen_gold)
        painter.drawEllipse(QPointF(0, 0), radius, radius)
        painter.drawEllipse(QPointF(0, 0), radius * 0.85, radius * 0.85)

        # Inscribed Octagram (2 crossed squares)
        r_square = radius * 0.85
        pts1 = []
        pts2 = []
        for k in range(4):
            a1 = (math.pi / 2) * k
            a2 = a1 + (math.pi / 4)
            pts1.append(QPointF(math.cos(a1) * r_square, math.sin(a1) * r_square))
            pts2.append(QPointF(math.cos(a2) * r_square, math.sin(a2) * r_square))

        painter.setPen(pen_crimson)
        for k in range(4):
            painter.drawLine(pts1[k], pts1[(k + 1) % 4])
            painter.drawLine(pts2[k], pts2[(k + 1) % 4])

        painter.drawEllipse(QPointF(0, 0), radius * 0.35, radius * 0.35)
        painter.restore()
