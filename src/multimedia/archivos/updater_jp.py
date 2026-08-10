from manim import *
import numpy as np

class Orbit(Scene):
    def construct(self):
        jp = Dot() #estrella principal del sistema
        
        text = Tex(r"Cuando los planetas se alinean,\\",
                   r"la excentricidad orbital modifica la\\",
                   r"sincronizacion de sus encuentros." , font_size = 32)
        text.move_to(UP*3.5)
        
        radius1 = 1
        radius2 = 2
        speed1 = 2
        speed2 = 1  

        planet1 = Dot(radius=0.3, color=BLUE)
        planet1.move_to([radius1, 0, 0])

        planet2 = Dot(radius=0.6, color=BLUE)
        planet2.move_to([radius2, 0, 0])

        orbit1 = Circle(color=WHITE, radius=1)
        orbit2 = Circle(color=WHITE, radius=2)
        
        time = ValueTracker(0)
        
        resonance_active = [False]  

        def planet_movement(mob):
            angle = speed1 * time.get_value()
            x = radius1 * np.cos(angle)
            y = radius1 * np.sin(angle)
            mob.move_to([x, y, 0])
            
            check_resonance()

        def planet_movement2(mob):
            angle = speed2 * time.get_value()
            x = radius2 * np.cos(angle)
            y = radius2 * np.sin(angle)
            mob.move_to([x, y, 0])

            check_resonance()

        def check_resonance(): #verifica si los planetas estan en resonancia
            angle1 = (speed1 * time.get_value()) % (2 * PI)
            angle2 = (speed2 * time.get_value()) % (2 * PI)

            tolerance = 0.1

            in_resonance = (abs(angle1 - angle2) < tolerance or 
                            abs(angle1 - angle2 - 2*PI) < tolerance or
                            abs(angle1 - angle2 + 2*PI) < tolerance)

            if in_resonance:
                if not resonance_active[0]:  
                    resonance_active[0] = True
                    planet1.set_color(GREEN)
                    planet2.set_color(GREEN)
            else:
                if resonance_active[0]: 
                    resonance_active[0] = False
                    planet1.set_color(BLUE)
                    planet2.set_color(BLUE)

        planet1.add_updater(planet_movement)
        planet2.add_updater(planet_movement2)

        self.play(Write(text))
        self.play(Create(jp), Create(orbit1), Create(orbit2))
        self.play(Create(planet1), Create(planet2))
        
        self.wait(1)
        self.play(time.animate.set_value(4 * PI), run_time=8, rate_func=linear)
        self.wait(1)