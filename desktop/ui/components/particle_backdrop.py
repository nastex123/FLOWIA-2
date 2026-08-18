"""Gothic ambient ember and mist particle backdrop widget using QPainter."""

import math
import random
from typing import List

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget


class GothicEmber:
    """Represents a rising crimson ember or ethereal mist particle."""

    def __init__(self, width: float, height: float):
        self.x = random.uniform(0, max(width, 100))
        self.y = random.uniform(0, max(height, 100))
        self.radius = random.uniform(1.2, 3.4)
        
        # Embers rise gently upwards with slight lateral sway
        self.vx = random.uniform(-0.35, 0.35)
        self.vy = random.uniform(-0.4, -0.9)  # Upward drift
        
        # Ember color type: 0 = crimson ember, 1 = violet mist, 2 = burnished gold
        self.particle_type = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
        self.base_alpha = random.uniform(0.3, 0.8)
        self.flicker_phase = random.uniform(0, 2 * math.pi)
        self.flicker_speed = random.uniform(0.03, 0.08)

    def update(self, width: float, height: float) -> None:
        self.x += self.vx + 0.15 * math.sin(self.flicker_phase)
        self.y += self.vy
        self.flicker_phase += self.flicker_speed

        # When ember reaches top or bounds, respawn at bottom
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
    """Gothic ambient canvas with rising embers and ethereal connections."""

    def __init__(self, num_particles: int = 42, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self._num_particles = num_particles
        self._embers: List[GothicEmber] = []
        self._initialized = False

        # 30 FPS smooth rendering loop with low resource consumption
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

        # 2. Subtle connections between proximity embers
        connection_dist = 120.0
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
                    alpha = int(factor * 45)
                    # Crimson / Violet filigree line
                    pen = QPen(QColor(190, 18, 60, alpha), 1.0)
                    painter.setPen(pen)
                    painter.drawLine(QPointF(e1.x, e1.y), QPointF(e2.x, e2.y))

        # 3. Draw glowing embers
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

            # Outer subtle halo
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_color))
            painter.drawEllipse(QPointF(e.x, e.y), e.radius * 2.4, e.radius * 2.4)

            # Core particle
            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QPointF(e.x, e.y), e.radius, e.radius)

        painter.end()
