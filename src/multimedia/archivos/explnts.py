from manim import *

class Exoplanet(Scene):
    def construct(self):
        # Configurar tiempo
        self.camera.frame_height = 8
        self.camera.frame_width = 14

        sol = Circle(radius=0.8, color=YELLOW, fill_opacity=1)
        sol_glow = Circle(radius=0.9, color=YELLOW, fill_opacity=0.3)
        
        orbita = Circle(radius=2, color=BLUE_E, stroke_width=1, stroke_opacity=0.5)
        planeta_orb = Dot(point=[2, 0, 0], color=BLUE, radius=0.25)
        planeta_orb_label = Text("Exoplaneta", font_size=24, color=BLUE).next_to(planeta_orb, UP, buff=0.2)
        
        errante = Dot(point=[-3, -2, 0], color=RED, radius=0.25)
        errante_label = Text("Errante", font_size=20, color=RED).next_to(errante, DOWN, buff=0.2)
        
        flecha_errante = Arrow(start=[-3, -2, 0], end=[-1, -3.5, 0], color=RED, buff=0)
        
        titulo = Text("Diferencia entre exoplaneta y planeta errante:", font_size=36, color=WHITE, weight=BOLD).to_edge(UP)
        
        self.play(Write(titulo))
        self.wait(0.5)
        
        self.play(FadeIn(sol_glow), FadeIn(sol), Create(orbita))
        self.play(FadeIn(planeta_orb), Write(planeta_orb_label))
        
        # Mostrar planeta errante
        self.play(FadeIn(errante), Write(errante_label))
        self.play(Create(flecha_errante))
        
        self.play(
            planeta_orb.animate.move_to([-2, 0, 0]),
            run_time=1.5,
            rate_func=linear
        )
        
        self.play(
            errante.animate.move_to([-1, -3.5, 0]),
            flecha_errante.animate.put_start_and_end_on([-1, -3.5, 0], [1, -4.5, 0]),
            run_time=1.5,
            rate_func=linear
        )
        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects])