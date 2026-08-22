from manim import *

class Periodo(Scene):
    def construct(self):

        self.camera.frame_height = 8
        self.camera.frame_width = 14

        titulo = Text("PERÍODO ORBITAL", font_size=36, color=WHITE, weight=BOLD).to_edge(UP)
        subtitulo = Text("Tiempo en dar una vuelta", font_size=28, color=WHITE).next_to(titulo, DOWN, buff=0.2)

        estrella = Circle(radius=0.7, color=YELLOW, fill_opacity=1)
        estrella_glow = Circle(radius=0.9, color=YELLOW, fill_opacity=0.2)
        orbita = Circle(radius=2.5, color=BLUE_E, stroke_width=2)

        planeta = Dot(point=[2.5, 0, 0], color=BLUE, radius=0.2)
        planeta_label = Text("Planeta", font_size=20, color=BLUE).next_to(planeta, UP, buff=0.1)

        marcas = VGroup(
            Dot(point=[2.5, 0, 0], color=WHITE, radius=0.05, fill_opacity=0.5),
            Dot(point=[0, 2.5, 0], color=WHITE, radius=0.05, fill_opacity=0.5),
            Dot(point=[-2.5, 0, 0], color=WHITE, radius=0.05, fill_opacity=0.5),
            Dot(point=[0, -2.5, 0], color=WHITE, radius=0.05, fill_opacity=0.5)
        )

        cronometro = Circle(radius=0.5, color=WHITE, stroke_width=2).shift(RIGHT * 4.5 + UP * 2.5)
        cronometro_label = Text("T", font_size=24, color=WHITE).next_to(cronometro, DOWN, buff=0.1)

        centro_reloj = cronometro.get_center()

        angulo = ValueTracker(0)

        aguja = always_redraw(
            lambda: Line(
                start=centro_reloj,
                end=centro_reloj + 0.4 * np.array([
                    np.cos(PI / 2 - angulo.get_value()),np.sin(PI / 2 - angulo.get_value()),0]),color=WHITE,stroke_width=3))

        self.play(Write(titulo), Write(subtitulo))
        self.wait(0.3)

        self.play(FadeIn(estrella_glow), FadeIn(estrella))
        self.play(Create(orbita), FadeIn(marcas))
        self.play(FadeIn(planeta), Write(planeta_label))
        self.play(Create(cronometro), Write(cronometro_label), FadeIn(aguja))

        trayectoria = Circle(radius=2.5, stroke_opacity=0).move_to(ORIGIN)

        self.play(MoveAlongPath(planeta, trayectoria, rate_func=linear),angulo.animate.set_value(TAU),run_time=6,rate_func=linear)

        circulo_completo = Circle(radius=2.5, color=YELLOW, stroke_width=4, stroke_opacity=0.5)

        self.play(Create(circulo_completo), run_time=0.5)

        self.wait(0.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects])