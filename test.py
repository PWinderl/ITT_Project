from PyQt5 import QtWidgets, QtGui
import pygame
import sys


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, surface, parent=None):
        super(ImageWidget, self).__init__(parent)
        w = surface.get_width()
        h = surface.get_height()
        self.data = surface.get_buffer().raw
        self.image = QtGui.QImage(self.data, w, h, QtGui.QImage.Format_RGB32)
        self.setGeometry(0, 0, w, h)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, self.image)
        qp.end()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, surface, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setCentralWidget(ImageWidget(surface, self))
        self.setGeometry(0, 0, 500, 500)


class Game():

    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (width, height), pygame.FULLSCREEN | pygame.NOFRAME)
        self.surface = pygame.Surface(self.screen.get_size())
        self.surface.fill((64, 128, 192, 224))
        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()

    def get_surface(self):
        return self.screen

    def run(self):
        clock = pygame.time.Clock()
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            # pygame.display.flip()
            clock.tick(30)
    pygame.quit()


app = QtWidgets.QApplication(sys.argv)
g = Game(500, 500)
w = MainWindow(g.get_surface())
w.show()
g.run()
app.exec_()
