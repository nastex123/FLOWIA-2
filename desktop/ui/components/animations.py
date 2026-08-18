"""Animation helper utilities for PySide6 desktop suite."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QObject
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget, QWidget


class SidebarAnimator(QObject):
    """Animates width changes on a sidebar widget smoothly."""

    def __init__(self, target_widget: QWidget, duration_ms: int = 240, parent=None):
        super().__init__(parent or target_widget)
        self.target_widget = target_widget
        self.duration_ms = duration_ms
        self._anim = QPropertyAnimation(self.target_widget, b"maximumWidth", self)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.setDuration(self.duration_ms)

        self._min_anim = QPropertyAnimation(self.target_widget, b"minimumWidth", self)
        self._min_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._min_anim.setDuration(self.duration_ms)

    def animate_to(self, target_width: int) -> None:
        self._anim.stop()
        self._min_anim.stop()

        curr_w = self.target_widget.width()
        self._anim.setStartValue(curr_w)
        self._anim.setEndValue(target_width)

        self._min_anim.setStartValue(curr_w)
        self._min_anim.setEndValue(target_width)

        self._anim.start()
        self._min_anim.start()


class PageTransitioner(QObject):
    """Performs smooth opacity fade-in transitions when switching stacked widget pages."""

    def __init__(self, stacked_widget: QStackedWidget, duration_ms: int = 180, parent=None):
        super().__init__(parent or stacked_widget)
        self.stacked_widget = stacked_widget
        self.duration_ms = duration_ms
        self._opacity_effect = QGraphicsOpacityEffect(self.stacked_widget)
        self.stacked_widget.setGraphicsEffect(self._opacity_effect)
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(self.duration_ms)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def transition_to_index(self, index: int) -> None:
        self._fade_anim.stop()
        self._opacity_effect.setOpacity(0.0)
        self.stacked_widget.setCurrentIndex(index)

        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()

    def transition_to_widget(self, widget: QWidget) -> None:
        self._fade_anim.stop()
        self._opacity_effect.setOpacity(0.0)
        self.stacked_widget.setCurrentWidget(widget)

        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()
