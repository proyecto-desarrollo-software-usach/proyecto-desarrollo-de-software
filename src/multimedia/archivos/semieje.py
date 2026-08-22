from manim import *

class Semieje(Scene):
    def construct(self):
        self.camera.frame_height = 8
        self.camera.frame_width = 14

        titulo = Text("Semieje Mayor:", font_size=36, color=WHITE, weight=BOLD).to_edge(UP)
        subtitulo = Text('"Tamaño" de la órbita (a).', font_size=28, color=WHITE).next_to(titulo, DOWN, buff=0.2)

        estrella = Dot(point=[-2, 0, 0], color=YELLOW, radius=0.2)
        estrella_glow = Circle(radius=0.3, color=YELLOW, fill_opacity=0.3).move_to(estrella)
        estrella_label = Text("★", font_size=30, color=YELLOW).next_to(estrella, DOWN, buff=0.1)

        elipse = Ellipse(width=6, height=4, color=BLUE_E, stroke_width=2)
        elipse.shift(RIGHT * 0.5)

        planeta_ap = Dot(point=[3.5, 0, 0], color=GREEN, radius=0.18)
        planeta_per = Dot(point=[-2.5, 0, 0], color=RED, radius=0.18)

        ap_label = Text("Máx", font_size=20, color=GREEN).next_to(planeta_ap, DOWN, buff=0.1)
        per_label = Text("Mín", font_size=20, color=RED).next_to(planeta_per, DOWN, buff=0.1)

        linea_max = Line(start=estrella.get_center(), end=planeta_ap.get_center(), color=GREEN, stroke_width=2)
        linea_min = Line(start=estrella.get_center(), end=planeta_per.get_center(), color=RED, stroke_width=2)

        semieje = Arrow(
            start=[0.5, 0, 0],
            end=[3.5, 0, 0],
            color=WHITE,
            stroke_width=3,
            buff=0
        )

        semieje_label = Text("a", font_size=28, color=WHITE, weight=BOLD).next_to(semieje, UP, buff=0.1)

        promedio = MathTex(
            r"a = \frac{d_{\max} + d_{\min}}{2}",font_size=30,color=WHITE).to_edge(DOWN)

        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.3)
        self.play(FadeIn(estrella_glow), FadeIn(estrella), Write(estrella_label))
        self.play(Create(elipse), run_time=1.5)
        self.play(FadeIn(planeta_ap), FadeIn(planeta_per), Write(ap_label), Write(per_label))
        self.play(Create(linea_max), Create(linea_min))
        self.wait(1.5)
        self.play(Create(semieje), Write(semieje_label))
        self.play(Write(promedio))
        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects])