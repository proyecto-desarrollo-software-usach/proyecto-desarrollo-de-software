###ARCHIVO DE ANIMACIONES PARA MÉTODOS DE DESCUBRIMIENTO DE EXOPLANETAS.

from manim import *

class Methods(Scene):
    def construct(self):
        text_m = Tex(r"Métodos de deteccion de exoplanetas",font_size=60).set_color_by_gradient(BLUE, YELLOW)

        text_m2 = Tex(r"los exoplanetas, al ser planetas de sistemas muy distantes\\",
                      r"al nuestro, necesitan de métodos especiales para ser descubiertos.\\",
                      r"Los métodos de detección de exoplanetas varían\\",
                      r"según el tipo de sistema planetario estudiado.",font_size=45)

        self.play(FadeIn(text_m))
        self.play(text_m.animate.shift(UP*3.25))
        self.wait(1)
        self.play(FadeIn(text_m2))
        self.wait(4)
        self.play(FadeOut(text_m2))

        text_m3 = Tex(r"Algunos métodos de detección de exoplanetas:")
        text_m3.move_to(UP*2.25)

        linea1 = Tex(r"-Método de tránsito")         
        linea2 = Tex(r"-Método de velocidad radial")
        linea3 = Tex(r"-Captura de imagen directa")
        linea4 = Tex(r"-Microlensing")

        linea1.move_to(UP*1.2)
        linea2.next_to(linea1, DOWN, buff=0.5)
        linea3.next_to(linea2, DOWN, buff=0.5)
        linea4.next_to(linea3, DOWN, buff=0.5)

        text_m4 = VGroup(linea1,linea2,linea3,linea4)

        self.play(FadeIn(text_m3))
        self.play(Write(text_m4))
        self.wait(2)