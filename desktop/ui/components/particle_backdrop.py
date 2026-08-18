"""Real-time ambient particle backdrop widget using QPainter."""

import math
import random
from typing import List

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget


class Particle:
    """Represents a single glowing celestial particle."""

    def __init__(self, width: float, height: float):
        self.x = random.uniform(0, max(width, 100))
        self.y = random.uniform(0, max(height, 100))
        self.radius = random.uniform(1.5, 3.2)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3, 0.8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.base_alpha = random.uniform(0.3, 0.75)
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.02, 0.05)

    def update(self, width: float, height: float) -> None:
        self.x += self.vx
        self.y += self.vy
        self.pulse_phase += self.pulse_speed

        # Bounce or wrap smoothly
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0

        if self.y < 0:
            self.y = height
        elif self.y > height:
            self.y = 0

    @property
    def current_alpha(self) -> float:
        return max(0.15, min(0.9, self.base_alpha + 0.2 * math.sin(self.pulse_phase)))


class ParticleBackdropWidget(QWidget):
    """Smooth ambient backdrop canvas with interconnected cyber constellation particles."""

    def __init__(self, num_particles: int = 36, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self._num_particles = num_particles
        self._particles: List[Particle] = []
        self._initialized = False

        # 30 FPS smooth loop with low CPU overhead
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(33)

    def _init_particles(self) -> None:
        w = float(self.width()) or 1200.0
        h = float(self.height()) or 800.0
        self._particles = [Particle(w, h) for _ in range(self._num_particles)]
        self._initialized = True

    def _on_tick(self) -> None:
        if not self._initialized and self.width() > 10:
            self._init_particles()

        w = float(self.width())
        h = float(self.height())
        for p in self._particles:
            p.update(w, h)

        self.update()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._initialized:
            self._init_particles()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()

        # 1. Subtle deep gradient background
        # Deep space dark base: #060911 to #090e1a
        painter.fillRect(0, 0, w, h, QColor(7, 10, 18, 255))

        # 2. Draw connections between close particles
        connection_max_dist = 140.0
        p_count = len(self._particles)

        for i in range(p_count):
            p1 = self._particles[i]
            for j in range(i + 1, p_count):
                p2 = self._particles[j]
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist = math.hypot(dx, dy)
                if dist < connection_max_dist:
                    factor = 1.0 - (dist / connection_max_dist)
                    alpha = int(factor * 60)
                    pen = QPen(QColor(56, 189, 248, alpha), 1.0)
                    painter.setPen(pen)
                    painter.drawLine(QPointF(p1.x, p1.y), QPointF(p2.x, p2.y))

        # 3. Draw particles with glow
        for p in self._particles:
            alpha = int(p.current_alpha * 255)
            
            # Outer subtle halo
            halo_pen = QPen(Qt.PenStyle.NoPen)
            painter.setPen(halo_pen)
            painter.setBrush(QBrush(QColor(56, 189, 248, int(alpha * 0.25))))
            painter.drawEllipse(QPointF(p.x, p.y), p.radius * 2.2, p.radius * 2.2)

            # Core particle
            painter.setBrush(QBrush(QColor(147, 197, 253, alpha)))
            painter.drawEllipse(QPointF(p.x, p.y), p.radius, p.radius)

        painter.end()
