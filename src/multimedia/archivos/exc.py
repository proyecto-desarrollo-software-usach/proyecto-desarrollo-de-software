from manim import *

class Exc(Scene):
    def construct(self):

        text1 = Text("Excentricidad de una Órbita:",color=WHITE,weight=BOLD)
        
        #explicar el factor e
        text_e2 = Tex(r"$\mathit{e}$ = grado de desviacion \\",
                    r"de una funcion cónica respecto \\",
                    r"a una circunferencia.").next_to(text1,DOWN)

        self.play(Write(text1),Write(text_e2))
        self.wait(1)
        self.play(Unwrite(text_e2))
        self.play(text1.animate.to_edge(UP))

        #deifnir figuras cónicas
        circulo = Circle(color=WHITE,).shift(LEFT*4)
        
        elps = Ellipse(color=WHITE)
        
        prbl = FunctionGraph(lambda x: x**2 ,x_range=[-2,2] ,color=WHITE).shift(RIGHT*4,DOWN*2)

        text_c1 = Tex(r"$\mathit{e=0}$").scale(1)
        text_c1.next_to(circulo, DOWN)

        text_c2 = Tex(r"$\mathit{0<e<1}$").scale(1)
        text_c2.next_to(elps, DOWN)

        text_c3 = Tex(r"$\mathit{e=1}$").scale(1)
        text_c3.next_to(prbl, DOWN)

        #animar cónicas
        self.play(Create(circulo),Create(elps),Create(prbl))
        self.play(Write(text_c1),Write(text_c2),Write(text_c3))
        self.wait(1)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        





