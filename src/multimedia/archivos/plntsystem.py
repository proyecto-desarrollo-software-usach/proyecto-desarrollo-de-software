from manim import *

class Sistema(Scene):
    def construct(self):

        self.camera.frame_height = 8
        self.camera.frame_width = 14
        
        estrella = Circle(radius=0.9, color=YELLOW, fill_opacity=1)
        estrella_glow = Circle(radius=1.0, color=YELLOW, fill_opacity=0.2)
        estrella_glow2 = Circle(radius=1.2, color=ORANGE, fill_opacity=0.1)

        titulo = Text("Sistema estelar:", font_size=36, color=WHITE, weight=BOLD)
        subtitulo = Text("se conforma de su estrella y sus planetas.", font_size=28, color=WHITE).next_to(titulo, DOWN, buff=0.2)

        orbita1 = Circle(radius=1.8, color=BLUE_E, stroke_width=1.5, stroke_opacity=0.4)
        orbita2 = Circle(radius=2.8, color=BLUE_E, stroke_width=1.5, stroke_opacity=0.3)
        orbita3 = Circle(radius=3.8, color=BLUE_E, stroke_width=1.5, stroke_opacity=0.2)

        planeta1 = Dot(point=[1.8, 0, 0], color=BLUE, radius=0.2)
        planeta2 = Dot(point=[2.8, 0, 0], color=GREEN, radius=0.25)
        planeta3 = Dot(point=[-3.8, 0, 0], color=RED, radius=0.3)

        p1_label = Text("P1", font_size=18, color=BLUE).next_to(planeta1, UP, buff=0.1)
        p2_label = Text("P2", font_size=18, color=GREEN).next_to(planeta2, UP, buff=0.1)
        p3_label = Text("P3", font_size=18, color=RED).next_to(planeta3, DOWN, buff=0.1)


        self.play(Write(titulo), Write(subtitulo))
        self.wait(2)
        self.play(titulo.animate.shift(UP*3.5).scale(0.6),FadeOut(subtitulo))

        self.play(FadeIn(estrella_glow2), FadeIn(estrella_glow), FadeIn(estrella))

        self.play(
            Create(orbita1), 
            Create(orbita2), 
            Create(orbita3),
            FadeIn(planeta1),
            FadeIn(planeta2),
            FadeIn(planeta3),
            Write(p1_label),
            Write(p2_label),
            Write(p3_label),
            run_time=1
        )
        
        recuadro = Rectangle(
            width=9, 
            height=9, 
            color=WHITE, 
            stroke_width=2,
            stroke_opacity=0.3
        )
        self.play(Create(recuadro), run_time=0.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects])