from manim import *

class Exc(Scene):
    def construct(self):

        text1 = MathTex(r"\text{¿Qué es la excentricidad de una orbita?}").set_color(BLUE)
        
        #explicar el factor e
        text_e2 = Tex(r"$\mathit{e}$ = grado de desviacion \\",
                    r"de una funcion cónica respecto \\",
                    r"a una circunferencia.")

        self.play(Write(text1))
        self.play(text1.animate.shift(UP*3.5).scale(0.6))
        self.play(Write(text_e2))
        self.wait(1)
        self.play(Unwrite(text_e2))
        
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
        self.play(Create(circulo))
        self.play(Write(text_c1))


        self.play(Create(elps))
        self.play(Write(text_c2))


        self.play(Create(prbl))
        self.play(Write(text_c3))

        self.wait(2)

        group1= VGroup(circulo, elps, prbl, text_c1, text_c2, text_c3, text1)

        self.play(FadeOut(group1))

        





