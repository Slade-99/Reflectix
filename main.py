from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random
from drawing import Drawing, Width, Height
from drawing import scaling


### Main class to initialize the game ####
class Game:
    def __init__(self):

        ## All global variables
        self.setup = Drawing()  ### Class used for drawing all objects
        self.available_states = ['Home', 'level-1', 'level-2', 'level-3', 'Rules', 'level-transition',
                                 'game-over']  # All the available states of the game
        self.state = 'Home'  # The current state
        self.current_level = 2  ## Current level in the game
        self.Width, self.Height = Width, Height  ## Screen
        self.return_button_coordinates = [0, 0, 0, 0]
        self.pause_button_coordinates = [0, 0, 0, 0]
        self.boundary_top = 0.93 * self.Height
        self.boundary_bottom = 0.01 * self.Height
        self.boundary_left = 0.01 * self.Width
        self.boundary_right = 0.99 * self.Width
        self.current_score = 0
        self.mirrors = 20
        self.pause_state = False
        self.mirror_length = 0
        self.rotation_angle = 0

        ### Update these coordinates to change the position of objects ###
        self.striker1_coordinates = [0.3 * self.Width, 0.3 * self.Height]  ## x,y
        self.striker2_coordinates = [0.45 * self.Width, 0.28 * self.Height]
        self.target_coordinates = [round(0.75 * self.Width), round(0.65 * self.Height), round(0.8 * self.Width), round(
            0.75 * self.Height)]  ### x1,y1,x2,y2  (x1,y1) -> bottom left   (x2,y2) -> top right
        self.mirror_coordinates = []
        self.barrier1_coordinates = [round(0.3 * self.Width), round(0.58 * self.Height), round(0.45 * self.Width),
                                     round(0.65 * self.Height)]
        self.barrier2_coordinates = [round(0.75 * self.Width), round(0.15 * self.Height), round(0.8 * self.Width),
                                     round(0.35 * self.Height)]
        self.point_of_failure1_coordinates = [round(0.6 * self.Width), round(0.58 * self.Height),
                                              round(0.65 * self.Width), round(0.65 * self.Height)]
        self.point_of_failure2_coordinates = [round(0.6 * self.Width), round(0.28 * self.Height),
                                              round(0.65 * self.Width), round(0.35 * self.Height)]

        self.screen_center = (self.Width / 2, self.Height / 2)
        self.boundary_dimensions = (self.boundary_left, self.boundary_right, self.boundary_top, self.boundary_bottom)

        self.mirror_spawn_time = None
        self.mirror_lifetime = 5  # Mirror lifetime in seconds
        self.barrier_velocity = [5,5]
        self.strikers = []
        self.striker_velocity = []
        self.striker_radius = 10 if scaling == 1 else 5

        self.start_time = time.time()

        self.initialize_strikers(1)    #initializing to level 1

        self.level3_hits = [False,False] #Flags to check whether both strikers hit the target or not
        self.striker_hit_target = [False] * len(self.strikers)

        #Level 3 target shrinking

        # Calculate the initial width and height of the target
        initial_target_width = self.target_coordinates[2] - self.target_coordinates[0]
        initial_target_height = self.target_coordinates[3] - self.target_coordinates[1]

        ## Set target_shrink_rate as 1% of the smaller dimension of the target
        self.target_shrink_rate = max(1,round(min(initial_target_width, initial_target_height) * 0.01,2))


        #
        self.target_min_size = min(5, round(min(self.Width, self.Height) * 0.05, 2)) # Minimum size of the target
        self.target_current_size = [self.target_coordinates[2] - self.target_coordinates[0],
                                    self.target_coordinates[3] - self.target_coordinates[1]]

        self.last_update_time = time.time()
        self.update_interval = 0.05 * (self.Width/1500) * (self.Height/1000)  # Update interval for shrinking the target


        ##Highscores
        self.display_high_scores()


    def initialize_strikers(self, level):
        self.strikers = []
        self.striker_velocity = []
        self.mirror_coordinates = []  # Clearing leftover mirrors
        self.level3_hits = [False] * 2 if level == 3 else []
        self.striker_hit_target = [False] * 2 if level == 3 else [False] * 1

        # Base velocities for 1500 x 1000
        base_v_lvl1 = [5, 4]
        base_v_lvl2 = [7, 6]
        base_v_lvl3 = [[6, 5], [-4, 5]]

        if level == 1:
            self.strikers.append([self.striker1_coordinates[0], self.striker1_coordinates[1]])
            self.striker_velocity.append([
                base_v_lvl1[0] * (self.Width / 1500),
                base_v_lvl1[1] * (self.Height / 1000)
            ])
            self.mirrors = 20
            self.striker_hit_target = [False] * len(self.strikers)

        elif level == 2:
            self.strikers.append([self.striker1_coordinates[0], self.striker1_coordinates[1]])
            self.striker_velocity.append([
                base_v_lvl2[0] * (self.Width / 1500),
                base_v_lvl2[1] * (self.Height / 1000)
            ])
            self.mirrors = 15
            self.striker_hit_target = [False] * len(self.strikers)

        elif level == 3:

            self.strikers.append([self.striker1_coordinates[0], self.striker1_coordinates[1]])
            self.striker_velocity.append([
                base_v_lvl3[0][0] * (self.Width / 1500),
                base_v_lvl3[0][1] * (self.Height / 1000)
            ])
            self.strikers.append([self.striker2_coordinates[0], self.striker2_coordinates[1]])
            self.striker_velocity.append([
                base_v_lvl3[1][0] * (self.Width / 1500),
                base_v_lvl3[1][1] * (self.Height / 1000)
            ])
            self.mirrors = 15
            self.striker_hit_target = [False] * len(self.strikers)

    def move_ball(self):
        if self.pause_state:  ## If the game is paused
            return

        ## Updating positions
        for i in range(len(self.strikers)):
            self.strikers[i][0] += self.striker_velocity[i][0]
            self.strikers[i][1] += self.striker_velocity[i][1]

            # Collision with walls/boundaries
            boundary_left, boundary_right, boundary_top, boundary_bottom = self.boundary_dimensions
            if self.strikers[i][0] - self.striker_radius <= boundary_left or self.strikers[i][
                0] + self.striker_radius >= boundary_right:
                self.striker_velocity[i][0] = -self.striker_velocity[i][0]  ## Reflect horizontally

            if self.strikers[i][1] - self.striker_radius <= boundary_bottom or self.strikers[i][
                1] + self.striker_radius >= boundary_top:
                self.striker_velocity[i][1] = - self.striker_velocity[i][1]  ## Reflect vertically

            # Collision with mirrors
            if self.check_mirror_collision(i):
                self.reflect_from_mirror(i)

            # Collision with target
            if self.check_target_collision(i) and not self.striker_hit_target[i]:
                self.hit_target(i)
                self.striker_hit_target[i] = True

            # Collision with failure points
            if self.check_failure_collision(i):
                self.game_over()

            #Collision with barriers
            if self.current_level in [2, 3]:
                collision_type1 = self.check_barrier_collision(i, self.barrier1_coordinates)
                if collision_type1:
                    self.reflect_from_barrier(i, self.barrier1_coordinates, collision_type1)

                collision_type2 = self.check_barrier_collision(i, self.barrier2_coordinates)
                if collision_type2:
                    self.reflect_from_barrier(i, self.barrier2_coordinates, collision_type2)








    def check_mirror_collision(self, striker_index):
        if len(self.mirror_coordinates) == 0:
            return False

        mx1, my1, mx2, my2 = self.mirror_coordinates
        striker_x, striker_y = self.strikers[striker_index]




        ## Mirror Vector
        mirror_vector = [mx2 - mx1, my2 - my1]
        mirror_length = math.sqrt(mirror_vector[0] ** 2 + mirror_vector[1] ** 2)

        #Vector from the mirror start point to the striker
        to_striker_vector = [striker_x - mx1, striker_y - my1]

        #Projection of the striker vector onto the mirror vector
        projection_length = (to_striker_vector[0] * mirror_vector[0] +
                             to_striker_vector[1] * mirror_vector[1]) / mirror_length


        ### Check if the projection is within the mirror bounds
        if 0 <= projection_length <= mirror_length:

            ### Compute the perpendicular distance from the striker to the mirror
            perpendicular_vector = [
                to_striker_vector[0] - projection_length * (mirror_vector[0] / mirror_length),
                to_striker_vector[1] - projection_length * (mirror_vector[1] / mirror_length)
            ]
            perpendicular_distance = math.sqrt(perpendicular_vector[0] ** 2 + perpendicular_vector[1] ** 2)


            if perpendicular_distance <= self.striker_radius:  ### Check if the perpendicular distance is less than the striker radius
                return True

        return False


    # Reflection from mirror
    def reflect_from_mirror(self,striker_index):

        mx1, my1, mx2, my2 = self.mirror_coordinates

        ## Compute the mirror's normal vector
        mirror_vector = [mx2 - mx1, my2 - my1]
        mirror_length = math.sqrt(mirror_vector[0] ** 2 + mirror_vector[1] ** 2)
        mirror_normal = [-mirror_vector[1] / mirror_length, mirror_vector[0] / mirror_length]

        # Get the striker's current velocity
        vx, vy = self.striker_velocity[striker_index]

        # Calculate the dot product between the velocity and the normal
        dot_product = vx * mirror_normal[0] + vy * mirror_normal[1]

        # Reflect the velocity
        self.striker_velocity[striker_index][0] -= 2 * dot_product * mirror_normal[0]
        self.striker_velocity[striker_index][1] -= 2 * dot_product * mirror_normal[1]

        # Ensure the striker does not "stick" to the mirror
        self.strikers[striker_index][0] += self.striker_velocity[striker_index][0]
        self.strikers[striker_index][1] += self.striker_velocity[striker_index][1]


    # Target collision
    def check_target_collision(self, striker_index):
        tx1, ty1, tx2, ty2 = self.target_coordinates
        striker_x, striker_y = self.strikers[striker_index]
        return tx1 <= striker_x <= tx2 and ty1 <= striker_y <= ty2

    # Handle target hitting
    def hit_target(self,striker_index):
        self.current_score += self.mirrors  # Points based on remaining mirrors


        self.start_time = time.time()

        if self.current_level == 1:
            self.state = "level-transition"
            self.initialize_strikers(2)  # Move to next level 2

        elif self.current_level == 2:
            self.state = "level-transition"
            self.initialize_strikers(3)  # Move to next level 3

        elif self.current_level == 3:

            self.level3_hits[striker_index] = True
            self.strikers[striker_index] = [-200,-200] #Moving the striker off-screen

            if all(self.level3_hits):

                self.state = "game-over"
                self.start_time = time.time()


        glutPostRedisplay()






    # Failure collision
    def check_failure_collision(self, striker_index):
        if self.current_level == 1:
            pass                        # No failure points in level 1

        if self.current_level == 2:
            fx1, fy1, fx2, fy2 = self.point_of_failure1_coordinates
            ball_x, ball_y = self.strikers[striker_index]
            return fx1 <= ball_x <= fx2 and fy1 <= ball_y <= fy2

        if self.current_level == 3:
            fx1, fy1, fx2, fy2 = self.point_of_failure1_coordinates
            ball_x, ball_y = self.strikers[striker_index]
            if fx1 <= ball_x <= fx2 and fy1 <= ball_y <= fy2:
                return True

            fx1, fy1, fx2, fy2 = self.point_of_failure2_coordinates
            return fx1 <= ball_x <= fx2 and fy1 <= ball_y <= fy2
        return False

    def move_barriers(self):
        boundary_left, boundary_right, boundary_top, boundary_bottom = self.boundary_dimensions

        # Move barrier 1 (Horizontal distance)
        self.barrier1_coordinates[0] += self.barrier_velocity[0]
        self.barrier1_coordinates[2] += self.barrier_velocity[0]

        # Reflect barrier 1
        if self.barrier1_coordinates[0] <= boundary_left or self.barrier1_coordinates[2] >= boundary_right:
            self.barrier_velocity[0] = -self.barrier_velocity[0]

        # Move barrier 2 (Vertical distance)
        self.barrier2_coordinates[1] += self.barrier_velocity[1]
        self.barrier2_coordinates[3] += self.barrier_velocity[1]

        # Reflect barrier 2
        if self.barrier2_coordinates[1] <= boundary_bottom or self.barrier2_coordinates[3] >= boundary_top:
            self.barrier_velocity[1] = -self.barrier_velocity[1]

        # Check collision with target for vertical barrier
        tx1, ty1, tx2, ty2 = self.target_coordinates
        bx1, by1, bx2, by2 = self.barrier2_coordinates

        if (bx1 <= tx2 and bx2 >= tx1) and (by1 <= ty2 and by2 >= ty1):
            self.barrier_velocity[1] = -self.barrier_velocity[1]

    def check_barrier_collision(self, striker_index, barrier_coord):
        striker_x, striker_y = self.strikers[striker_index]
        striker_radius = self.striker_radius

        # Barrier bounding box
        bx1, by1, bx2, by2 = barrier_coord

        # Horizontal collision (top or bottom edge of barrier)
        if bx1 <= striker_x <= bx2 and (
                abs(striker_y - by1) <= striker_radius or abs(striker_y - by2) <= striker_radius):
            return "horizontal"

        # Vertical collision (left or right edge of barrier)
        if by1 <= striker_y <= by2 and (
                abs(striker_x - bx1) <= striker_radius or abs(striker_x - bx2) <= striker_radius):
            return "vertical"

        return None




    def reflect_from_barrier(self,striker_index,barrier_coords,barrier_type):
        striker_x, striker_y = self.strikers[striker_index]

        striker_radius = self.striker_radius

        bx1, by1, bx2, by2 = barrier_coords

        if barrier_type == "horizontal":
            # Reflect on the top or bottom edge of the horizontal barrier
            if abs(striker_y - by1) <= striker_radius:
                self.striker_velocity[striker_index][1] = -abs(self.striker_velocity[striker_index][1])  # Reflect down
            elif abs(striker_y - by2) <= striker_radius:
                self.striker_velocity[striker_index][1] = abs(self.striker_velocity[striker_index][1])  # Reflect up

        elif barrier_type == "vertical":
            # Reflect on the left or right edge of the vertical barrier
            if abs(striker_x - bx1) <= striker_radius:
                self.striker_velocity[striker_index][0] = -abs(self.striker_velocity[striker_index][0])  # Reflect left
            elif abs(striker_x - bx2) <= striker_radius:
                self.striker_velocity[striker_index][0] = abs(self.striker_velocity[striker_index][0])  # Reflect right

        # To prevent sticking
        self.strikers[striker_index][0] += self.striker_velocity[striker_index][0]
        self.strikers[striker_index][1] += self.striker_velocity[striker_index][1]

    def update_target_size(self):
        current_time = time.time()

        ## Check timing interval for shrinking or expanding
        if self.current_level == 3 and current_time - self.last_update_time >= self.update_interval:
            width = self.target_coordinates[2] - self.target_coordinates[0]
            height = self.target_coordinates[3] - self.target_coordinates[1]

            # Determine if we should shrink or expand
            if not hasattr(self, 'shrinking'):
                self.shrinking = True

            if self.shrinking:

                if width <= self.target_min_size or height <= self.target_min_size:

                    self.shrinking = False   # Stop shrinking if the size is below or equal to the minimum threshold
                else:
                    self.target_coordinates[0] += self.target_shrink_rate
                    self.target_coordinates[1] += self.target_shrink_rate
                    self.target_coordinates[2] -= self.target_shrink_rate
                    self.target_coordinates[3] -= self.target_shrink_rate
            else:
                # Stop expanding if the size is above or equal to the initial size
                initial_target_width = round(0.8 * self.Width) - round(0.75 * self.Width)
                initial_target_height = round(0.75 * self.Height) - round(0.65 * self.Height)
                if width >= initial_target_width or height >= initial_target_height:
                    self.shrinking = True
                else:
                    self.target_coordinates[0] -= self.target_shrink_rate
                    self.target_coordinates[1] -= self.target_shrink_rate
                    self.target_coordinates[2] += self.target_shrink_rate
                    self.target_coordinates[3] += self.target_shrink_rate


            self.last_update_time = current_time ###Last update time is updated





    def game_over(self):
        self.save_high_score(self.current_score)
        self.display_high_scores()
        self.state = "game-over"
        self.start_time = time.time()
        glutPostRedisplay()

    def save_high_score(self, score):
        scores = self.load_high_scores()
        scores.append(score)
        scores = sorted(scores, reverse =True) [:5]
        with open('high_scores.txt','w') as file:
            for score in scores:
                file.write(f"{score}\n")

    def load_high_scores(self):
        try:
            with open('high_scores.txt', 'r') as file:
                scores = file.readlines()
                scores = [int(score.strip()) for score in scores]
                return scores
        except FileNotFoundError:
            return []

    def display_high_scores(self):
        scores = self.load_high_scores()
        print("High Scores:")
        for score in scores:
            print(score)

    def main_display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.iterate()  ## Set the viewport and projection matrix

        glColor3f(0, 0, 0)

        if self.state == 'Home':
            self.setup.draw_Title()
            self.setup.draw_New_Game_Box()
            self.setup.draw_Level2_Box()
            self.setup.draw_Level3_Box()
            self.setup.draw_Rules_Box()
            self.setup.draw_Exit_Box()
            self.setup.draw_extras2()
            self.setup.draw_extras1()

        elif self.state == 'level-1':
            self.current_level = 1
            self.mirror_length = 70 if self.Width == 1500 else 35

            # Boundary and HUD Drawing
            self.setup.draw_boundary([self.boundary_left, self.boundary_bottom, self.boundary_right, self.boundary_top])
            self.return_button_coordinates = [round(0.95 * self.Width), 0.95 * self.Height, round(0.99 * self.Width),
                                              0.99 * self.Height]
            self.pause_button_coordinates = [0, round(0.95 * self.Height), round(0.05 * self.Width),
                                             round(0.99 * self.Height)]
            self.setup.draw_hud(self.return_button_coordinates, self.pause_button_coordinates, self.pause_state,
                                self.current_score, self.mirrors, self.state)

            # Spawn strikers dynamically
            for striker in self.strikers:
                self.setup.draw_circle(striker[0], striker[1], self.striker_radius, 3, 'g')

            # Spawn other elements
            self.setup.spawn_target(self.target_coordinates)
            if len(self.mirror_coordinates) > 0:
                self.setup.spawn_mirror(self.mirror_coordinates)

        elif self.state == 'level-2':
            self.current_level = 2
            self.mirror_length = 50 if self.Width == 1500 else 25

            # Boundary and HUD Drawing
            self.setup.draw_boundary([self.boundary_left, self.boundary_bottom, self.boundary_right, self.boundary_top])
            self.return_button_coordinates = [round(0.95 * self.Width), 0.95 * self.Height, round(0.99 * self.Width),
                                              0.99 * self.Height]
            self.pause_button_coordinates = [0, round(0.95 * self.Height), round(0.05 * self.Width),
                                             round(0.99 * self.Height)]
            self.setup.draw_hud(self.return_button_coordinates, self.pause_button_coordinates, self.pause_state,
                                self.current_score, self.mirrors, self.state)

            # Spawn strikers dynamically
            for striker in self.strikers:
                self.setup.draw_circle(striker[0], striker[1], self.striker_radius, 3, 'g')

            # Spawn other elements
            self.setup.spawn_target(self.target_coordinates)
            self.setup.spawn_point_of_failure1(self.point_of_failure1_coordinates)
            self.setup.spawn_barrier1(self.barrier1_coordinates)
            self.setup.spawn_barrier2(self.barrier2_coordinates)
            if len(self.mirror_coordinates) > 0:
                self.setup.spawn_mirror(self.mirror_coordinates)

        elif self.state == 'level-3':
            self.current_level = 3
            self.mirror_length = 30 if self.Width == 1500 else 15

            # Boundary and HUD Drawing
            self.setup.draw_boundary([self.boundary_left, self.boundary_bottom, self.boundary_right, self.boundary_top])
            self.return_button_coordinates = [round(0.95 * self.Width), 0.95 * self.Height, round(0.99 * self.Width),
                                              0.99 * self.Height]
            self.pause_button_coordinates = [0, round(0.95 * self.Height), round(0.05 * self.Width),
                                             round(0.99 * self.Height)]
            self.setup.draw_hud(self.return_button_coordinates, self.pause_button_coordinates, self.pause_state,
                                self.current_score, self.mirrors, self.state)

            # Spawn strikers dynamically
            for i, striker in enumerate(self.strikers):

                self.setup.draw_circle(striker[0], striker[1], self.striker_radius, 3, 'g')

            # Spawn other elements
            self.setup.spawn_target(self.target_coordinates)
            self.setup.spawn_point_of_failure1(self.point_of_failure1_coordinates)
            self.setup.spawn_point_of_failure2(self.point_of_failure2_coordinates)
            self.setup.spawn_barrier1(self.barrier1_coordinates)
            self.setup.spawn_barrier2(self.barrier2_coordinates)
            if len(self.mirror_coordinates) > 0:
                self.setup.spawn_mirror(self.mirror_coordinates)

        elif self.state == 'Rules':
            self.setup.draw_how_to_play()
            self.setup.draw_rule1()
            self.setup.draw_rule2()
            self.setup.draw_rule3()
            self.setup.draw_rule4()
            self.setup.draw_rule5()
            self.setup.draw_rule6()
            self.setup.draw_best_of_luck()
            self.return_button_coordinates = [round(0.93 * self.Width), round(0.93 * self.Height),
                                              round(0.97 * self.Width), round(0.97 * self.Height)]
            self.setup.draw_return_button(self.return_button_coordinates)

        elif self.state == 'level-transition':
            # Boundary
            self.setup.draw_boundary([self.boundary_left, self.boundary_bottom, self.boundary_right, self.boundary_top])
            self.setup.draw_comments(self.current_score, self.current_level)
            if time.time() - self.start_time >= 3:
                if self.current_level == 1:

                        self.state = "level-2"
                        self.current_level = 2
                        self.initialize_strikers(2)  # Initialize strikers for level 2
                        glutPostRedisplay()

                elif self.current_level == 2:


                        self.state = "level-3"
                        self.current_level = 3
                        self.initialize_strikers(3)  # Initialize strikers for level 3

                        glutPostRedisplay()

                elif self.current_level == 3 and all(self.level3_hits):
                    self.setup.draw_gameover_comments(self.current_score)


                    self.state = "Home"
                    glutPostRedisplay()

        elif self.state == 'game-over':
            self.setup.draw_boundary([self.boundary_left, self.boundary_bottom, self.boundary_right, self.boundary_top])
            self.return_button_coordinates = [0.95 * self.Width, 0.93 * self.Height, self.Width, self.Height]
            self.pause_button_coordinates = [0, 0.93 * self.Height, 0.05 * self.Width, self.Height]
            self.setup.draw_gameover_comments(self.current_score)

            if time.time() - self.start_time >= 3:
                self.current_score = 0 #Resetting the score when going to main menu
                self.state = "Home"
                glutPostRedisplay()

        glutSwapBuffers()

    def animate(self):
        if self.state in ['level-1', 'level-2', 'level-3']:
            self.move_ball()
            if self.mirror_spawn_time and time.time() - self.mirror_spawn_time > self.mirror_lifetime:
                self.mirror_coordinates = []  # Remove the mirror
                self.mirror_spawn_time = None  # Reset the spawn time

        if self.state == 'level-1':
            self.move_ball()
            if len(self.strikers) > 0 and self.check_target_collision(0):
                self.state = "level-transition"
                self.current_level = 2
                self.initialize_strikers(2)
                self.start_time = time.time()
                self.rotation_angle = 0
            elif self.check_failure_collision(0) and len(self.strikers) > 0:
                self.state = "game-over"
                self.start_time = time.time()
            glutPostRedisplay()

        elif self.state == 'level-2':
            self.move_ball()
            if self.check_target_collision(0) and len(self.strikers) > 0:
                self.state = "level-transition"
                self.current_level = 3
                self.initialize_strikers(3)
                self.start_time = time.time()
                self.rotation_angle = 0
            elif self.check_failure_collision(0) and len(self.strikers) > 0:
                self.state = "game-over"
                self.start_time = time.time()
            glutPostRedisplay()

        elif self.state == 'level-3':

            self.move_ball()

            self.move_barriers()

            self.update_target_size()  ##Target shrinks and expands here


            for i in range(len(self.strikers)):
                if self.check_target_collision(i) and not self.level3_hits[i]:
                    #self.level3_hits[i] = True
                    self.hit_target(i)

            if all(self.level3_hits):

                self.state = "game-over"
                #self.state = "level-transition"
                self.start_time = time.time()
            if len(self.strikers) > 1 and self.check_failure_collision(0) or self.check_failure_collision(1):
                self.state = "game-over"
                self.start_time = time.time()
            glutPostRedisplay()

        elif self.state == 'level-transition':
            self.setup.draw_boundary([self.boundary_left, self.boundary_bottom, self.boundary_right, self.boundary_top])
            if time.time() - self.start_time >= 3:
                if self.current_level == 1:
                    self.state = "level-2"
                    self.initialize_strikers(2)
                    self.mirror_coordinates = []

                elif self.current_level == 2:
                    self.state = "level-3"
                    self.initialize_strikers(3)
                    self.mirror_coordinates = []

                elif self.current_level == 3:
                    self.state = "Home"

            glutPostRedisplay()

        elif self.state == 'game-over':
            if time.time() - self.start_time >= 3:
                self.current_score = 0  # Resetting the score when going to main menu
                self.state = "Home"
            glutPostRedisplay()

    def mouseListener(self, button, state, x, y):  # /#/x, y is the x-y of the screen (2D)

        if button == GLUT_LEFT_BUTTON:

            if state == GLUT_DOWN:

                MOUSE_X = x
                MOUSE_Y = self.Height - y

                if (self.state == "Home"):

                    x1, y1, x2, y2 = self.setup.New_Game_Box_coordinates[0], self.setup.New_Game_Box_coordinates[1], \
                        self.setup.New_Game_Box_coordinates[2], self.setup.New_Game_Box_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.state = 'level-1'
                        self.current_level = 1
                        self.initialize_strikers(1)

                    x1, y1, x2, y2 = self.setup.Level2_Box_Box_coordinates[0], self.setup.Level2_Box_Box_coordinates[1], \
                        self.setup.Level2_Box_Box_coordinates[2], self.setup.Level2_Box_Box_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.state = 'level-2'
                        self.current_level = 2
                        self.initialize_strikers(2)

                    x1, y1, x2, y2 = self.setup.Level3_Box_Box_coordinates[0], self.setup.Level3_Box_Box_coordinates[1], \
                        self.setup.Level3_Box_Box_coordinates[2], self.setup.Level3_Box_Box_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.state = 'level-3'
                        self.current_level = 3
                        self.initialize_strikers(3)

                    x1, y1, x2, y2 = self.setup.Rules_Box_coordinates[0], self.setup.Rules_Box_coordinates[1], \
                        self.setup.Rules_Box_coordinates[2], self.setup.Rules_Box_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.state = 'Rules'

                    x1, y1, x2, y2 = self.setup.Exit_Box_coordinates[0], self.setup.Exit_Box_coordinates[1], \
                        self.setup.Exit_Box_coordinates[2], self.setup.Exit_Box_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        glutLeaveMainLoop()

                elif (self.state == "Rules"):

                    x1, y1, x2, y2 = self.return_button_coordinates[0], self.return_button_coordinates[1], \
                        self.return_button_coordinates[2], self.return_button_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.state = 'Home'

                ### If the player is playing at level 1
                elif (self.state == 'level-1'):

                    x1, y1, x2, y2 = self.return_button_coordinates[0], self.return_button_coordinates[1], \
                        self.return_button_coordinates[2], self.return_button_coordinates[3]

                    if (
                            MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):  ### Checking if mouse click inside return button
                        self.mirror_coordinates = []
                        self.state = 'Home'

                    x1, y1, x2, y2 = self.pause_button_coordinates[0], self.pause_button_coordinates[1], \
                        self.pause_button_coordinates[2], self.pause_button_coordinates[3]

                    if (
                            MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):  ### Checking if mouse click inside pause button

                        if (self.pause_state):
                            self.pause_state = False
                        else:
                            self.pause_state = True

                    x1, y1, x2, y2 = 0.01 * self.Width, 0.01 * self.Height, 0.99 * self.Width, 0.93 * self.Height  ###Boundary coordinates

                    if (
                            MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):  ## Checking if mouse click inside boundary

                        x1, y1, x2, y2 = self.target_coordinates[0], self.target_coordinates[1], \
                            self.target_coordinates[2], self.target_coordinates[3]

                        mirror_x1 = MOUSE_X - self.mirror_length
                        mirror_y1 = MOUSE_Y
                        mirror_x2 = MOUSE_X + self.mirror_length
                        mirror_y2 = MOUSE_Y

                        if not (
                                mirror_x2 >= x1 and mirror_x1 <= x2 and mirror_y2 >= y1 and mirror_y1 <= y2):  ### Checking if not inside the target box
                            if self.pause_state != True:  # Ensures mirror is not spawned during pause
                                if self.mirrors > 0:
                                    self.mirror_coordinates = [mirror_x1, mirror_y1, mirror_x2, mirror_y2]
                                    self.rotation_angle = 0
                                    self.mirrors -= 1
                                    self.mirror_spawn_time = time.time()
                                else:
                                    self.start_time = time.time()
                                    self.state = 'game-over'

                elif (self.state == 'level-2'):

                    x1, y1, x2, y2 = self.return_button_coordinates[0], self.return_button_coordinates[1], \
                        self.return_button_coordinates[2], self.return_button_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.mirror_coordinates = []
                        self.state = 'Home'

                    x1, y1, x2, y2 = self.pause_button_coordinates[0], self.pause_button_coordinates[1], \
                        self.pause_button_coordinates[2], self.pause_button_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):

                        if (self.pause_state):
                            self.pause_state = False
                        else:
                            self.pause_state = True

                    x1, y1, x2, y2 = 0.01 * self.Width, 0.01 * self.Height, 0.99 * self.Width, 0.93 * self.Height  ###Boundary coordinates

                    if (
                            MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):  ## Checking if mouse click inside boundary

                        x1, y1, x2, y2 = self.target_coordinates[0], self.target_coordinates[1], \
                            self.target_coordinates[2], self.target_coordinates[3]
                        x3, y3, x4, y4 = self.point_of_failure1_coordinates[0], self.point_of_failure1_coordinates[1], \
                            self.point_of_failure1_coordinates[2], self.point_of_failure1_coordinates[3]

                        mirror_x1 = MOUSE_X - self.mirror_length
                        mirror_y1 = MOUSE_Y
                        mirror_x2 = MOUSE_X + self.mirror_length
                        mirror_y2 = MOUSE_Y

                        if not (mirror_x2 >= x1 and mirror_x1 <= x2 and mirror_y2 >= y1 and mirror_y1 <= y2) and \
                                not (mirror_x2 >= x3 and mirror_x1 <= x4 and mirror_y2 >= y3 and mirror_y1 <= y4):
                            barrier_collision = False
                            for barrier in [self.barrier1_coordinates, self.barrier2_coordinates]:
                                bx1, by1, bx2, by2 = barrier
                                if mirror_x2 >= bx1 and mirror_x1 <= bx2 and mirror_y2 >= by1 and mirror_y1 <= by2:
                                    barrier_collision = True
                                    break

                            if not barrier_collision and self.pause_state != True:  # Ensures mirror is not spawned during pause
                                if self.mirrors > 0:
                                    self.mirror_coordinates = [mirror_x1, mirror_y1, mirror_x2, mirror_y2]
                                    self.rotation_angle = 0
                                    self.mirrors -= 1
                                    self.mirror_spawn_time = time.time()
                                else:
                                    self.start_time = time.time()
                                    self.state = 'game-over'

                elif (self.state == 'level-3'):

                    x1, y1, x2, y2 = self.return_button_coordinates[0], self.return_button_coordinates[1], \
                        self.return_button_coordinates[2], self.return_button_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):
                        self.mirror_coordinates = []
                        self.state = 'Home'

                    x1, y1, x2, y2 = self.pause_button_coordinates[0], self.pause_button_coordinates[1], \
                        self.pause_button_coordinates[2], self.pause_button_coordinates[3]

                    if (MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):

                        if (self.pause_state):
                            self.pause_state = False
                        else:
                            self.pause_state = True

                    x1, y1, x2, y2 = 0.01 * self.Width, 0.01 * self.Height, 0.99 * self.Width, 0.93 * self.Height  ###Boundary coordinates

                    if (
                            MOUSE_X >= x1 and MOUSE_X <= x2 and MOUSE_Y >= y1 and MOUSE_Y <= y2):  ## Checking if mouse click inside boundary

                        x1, y1, x2, y2 = self.target_coordinates[0], self.target_coordinates[1], \
                            self.target_coordinates[2], self.target_coordinates[3]
                        x3, y3, x4, y4 = self.point_of_failure1_coordinates[0], self.point_of_failure1_coordinates[1], \
                            self.point_of_failure1_coordinates[2], self.point_of_failure1_coordinates[3]
                        x5, y5, x6, y6 = self.point_of_failure2_coordinates[0], self.point_of_failure2_coordinates[1], \
                            self.point_of_failure2_coordinates[2], self.point_of_failure2_coordinates[3]
                        x7, y7, x8, y8 = self.barrier1_coordinates[0], self.barrier1_coordinates[1], \
                            self.barrier1_coordinates[2], self.barrier1_coordinates[3]
                        x9, y9, x10, y10 = self.barrier2_coordinates[0], self.barrier2_coordinates[1], \
                            self.barrier2_coordinates[2], self.barrier2_coordinates[3]

                        mirror_x1 = MOUSE_X - self.mirror_length
                        mirror_y1 = MOUSE_Y
                        mirror_x2 = MOUSE_X + self.mirror_length
                        mirror_y2 = MOUSE_Y

                        if not (mirror_x2 >= x1 and mirror_x1 <= x2 and mirror_y2 >= y1 and mirror_y1 <= y2) and \
                                not (mirror_x2 >= x3 and mirror_x1 <= x4 and mirror_y2 >= y3 and mirror_y1 <= y4) and \
                                not (mirror_x2 >= x5 and mirror_x1 <= x6 and mirror_y2 >= y5 and mirror_y1 <= y6):
                            barrier_collision = False
                            for barrier in [self.barrier1_coordinates, self.barrier2_coordinates]:
                                bx1, by1, bx2, by2 = barrier
                                if mirror_x2 >= bx1 and mirror_x1 <= bx2 and mirror_y2 >= by1 and mirror_y1 <= by2:
                                    barrier_collision = True
                                    break

                            if not barrier_collision and self.pause_state != True:  # Ensures mirror is not spawned during pause
                                if self.mirrors > 0:
                                    self.mirror_coordinates = [mirror_x1, mirror_y1, mirror_x2, mirror_y2]
                                    self.rotation_angle = 0
                                    self.mirrors -= 1
                                    self.mirror_spawn_time = time.time()
                                else:
                                    self.start_time = time.time()
                                    self.state = 'game-over'

                glutPostRedisplay()

    def keyboardListener(self, key, x, y):

        pass

        glutPostRedisplay()

    def specialKeyListener(self, key, x, y):

        if key == GLUT_KEY_UP:

            if (len(self.mirror_coordinates) > 0):
                self.rotation_angle += 10
                angle_radians = math.radians(self.rotation_angle)
                middle_x = (self.mirror_coordinates[0] + self.mirror_coordinates[2]) / 2
                middle_y = (self.mirror_coordinates[1] + self.mirror_coordinates[3]) / 2

                x1 = round(-1 * self.mirror_length * math.cos(angle_radians) + middle_x)
                y1 = round(-1 * self.mirror_length * math.sin(angle_radians) + middle_y)
                x2 = round(self.mirror_length * math.cos(angle_radians) + middle_x)
                y2 = round(self.mirror_length * math.sin(angle_radians) + middle_y)

                self.mirror_coordinates = [x1, y1, x2, y2]

        if key == GLUT_KEY_DOWN:
            if (len(self.mirror_coordinates) > 0):
                self.rotation_angle -= 10
                angle_radians = math.radians(self.rotation_angle)
                middle_x = (self.mirror_coordinates[0] + self.mirror_coordinates[2]) / 2
                middle_y = (self.mirror_coordinates[1] + self.mirror_coordinates[3]) / 2

                x1 = round(-1 * self.mirror_length * math.cos(angle_radians) + middle_x)
                y1 = round(-1 * self.mirror_length * math.sin(angle_radians) + middle_y)
                x2 = round(self.mirror_length * math.cos(angle_radians) + middle_x)
                y2 = round(self.mirror_length * math.sin(angle_radians) + middle_y)

                self.mirror_coordinates = [x1, y1, x2, y2]

        glutPostRedisplay()

    def iterate(self):
        glViewport(0, 0, self.Width, self.Height)  #### How much of the window I want to render
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.Width * 1, 0.0, self.Height * 1, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def init(self):

        glClearColor(0, 0, 0, 0)  ## Sets background colour to black

        glMatrixMode(GL_PROJECTION)  ## Defines 3d to 2d projections

        glLoadIdentity()  # Clear or reset matrix state
        # //give PERSPECTIVE parameters

        # gluPerspective(104,    1,  1,  1000.0)  ## Avoided since working with 2D only
        # field of view in y-axis, aspect ratio , near clip , far clip are the parameters

    def run(self):

        glutInit()
        glutInitWindowSize(self.Width, self.Height)
        glutInitWindowPosition(0, 0)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  # GLUT_DEPTH avoided as we are not working with 3D
        ## GLUT_DOUBLE used for two buffers front buffer holds current display and back buffer holds the next one to display
        ## it helps to prevent tearing and flickring while rendering GLUT_RBG rendering colour model is set to RGB
        wind = glutCreateWindow(b"Reflectix")
        self.init()  # Set projection and BG colour

        glutDisplayFunc(self.main_display)

        glutIdleFunc(self.animate)
        glutKeyboardFunc(self.keyboardListener)
        glutSpecialFunc(self.specialKeyListener)
        glutMouseFunc(self.mouseListener)
        glutMainLoop()


if __name__ == "__main__":
    app = Game()
    app.run()



