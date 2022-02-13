"""
roids.py - Asteroids style game demo using polygons.
"""

import math
import random
import utime
import micropython
import st7789
import tft_config
import tft_buttons as Buttons


tft = tft_config.config(1, buffer_size=64*64*2)
buttons = Buttons.Buttons()


def main():
    '''
    Game on!
    '''

    class Poly():
        '''
        Poly class to keep track of a polygon based sprite
        '''

        def __init__(
                self,
                # list (x,y) tuples of convex polygon, must be closed
                polygon,
                x=None,             # x location of polygon
                y=None,             # y location of polygon
                v_x=None,           # velocity in x axis
                v_y=None,           # velocity in y axis
                angle=None,         # angle in radians polygon is facing
                spin=None,          # spin in radians per frame_time
                scale=None,         # scale factor for polygon
                radius=None,        # radius of polygon for collision detection
                max_velocity=10,    # max velocity of polygon
                counter=0):

            # scale the polygon if scale was given
            self.polygon = (
                polygon if scale is None else [(int(scale*x[0]), int(scale*x[1])) for x in polygon])

            # if no location given assign a random location
            self.x = random.randint(0, width) if x is None else x
            self.y = random.randint(0, width) if y is None else y

            # set angle if given
            self.angle = float(0) if angle is None else angle

            # set random spin unless one was given
            self.spin = random.randint(-3, 3) / 16 if spin is None else spin

            # set random velocity unless one was given
            self.velocity_x = random.uniform(
                0.50, 0.99)*6-3 + 0.75 if v_x is None else v_x
            self.velocity_y = random.uniform(
                0.50, 0.99)*6-3 + 0.75 if v_y is None else v_y

            # set radius, max_velocity and radius counter
            self.radius = radius
            self.max_velocity = max_velocity
            self.counter = counter

        def rotate(self, rad):
            '''
            Rotate polygon in radians
            '''
            self.angle += rad
            if self.angle > rad_max:
                self.angle = 0
            elif self.angle < 0:
                self.angle = rad_max

        def move(self):
            '''
            Rotate and move polygon velocity distance.
            '''
            if self.spin != 0:
                self.rotate(self.spin)

            self.x += int(self.velocity_x)
            self.y += int(self.velocity_y)
            self.x %= width
            self.y %= height

        def draw(self, color):
            '''
            Draw the polygon
            '''
            tft.polygon(self.polygon, self.x, self.y, color, self.angle, 0, 0)

        def collision(self, poly):
            '''
            Detect collisions using overlapping radiuses.
            Returns True on collision.
            '''
            return abs(
                ((self.x - poly.x) * (self.x - poly.x) +
                 (self.y - poly.y) * (self.y - poly.y))
                < (self.radius + poly.radius) * (self.radius + poly.radius))

    def create_roid(size, x=None, y=None, v_x=None, v_y=None):
        '''
        Create a new roid with the given parameters.
        '''
        return Poly(
            roid_poly,
            x=x,
            y=y,
            v_x=v_x,
            v_y=v_y,
            scale=roid_scale[size],
            radius=roid_radius[size],
            counter=size)

    def update_missiles():
        '''
        Update active missiles and handle asteroid hits.
        '''
        for missile in list(missiles):                          # for each missile
            missile.draw(st7789.BLACK)                          # erase old missile
            if missile.counter > 0:                             # if counter > 0 missile is active
                missile.move()                                  # update missile position

                for roid in list(roids):                        # for each roid
                    if missile.collision(roid):                 # check if missile collides with roid
                        roid.draw(st7789.BLACK)                 # erase the roid
                        if roid.counter > 0:                    # if roid is not the smallest size
                            roids.append(                       # add first smaller roid
                                create_roid(
                                    roid.counter-1,
                                    x=roid.x,
                                    y=roid.y,
                                    v_x=roid.velocity_x,
                                    v_y=roid.velocity_y))
                            roids.append(                       # add second smaller roid
                                create_roid(
                                    roid.counter-1,
                                    x=roid.x,
                                    y=roid.y,
                                    v_x=-roid.velocity_x,
                                    v_y=-roid.velocity_y))

                        roids.remove(roid)                      # remove the roid that was hit
                        missile.counter = 0

                if missile.counter > 0:                         # if the missile has life left
                    missile.draw(st7789.WHITE)                  # draw missile
                    missile.counter -= 1                        # reduce missile life
                else:

                    missiles.remove(missile)                    # remove exploded missile
            else:
                missiles.remove(missile)                        # remove expired missile

    def update_ship():
        '''
        Update ship velocity and limit to max_velocity
        '''
        # apply drag to velocity of ship so it will eventually slow to a stop
        ship.velocity_x -= ship.velocity_x * ship_drag_frame
        ship.velocity_y -= ship.velocity_y * ship_drag_frame

        if ship.velocity_x > ship.max_velocity:        # Limit ship velocity to +/- max_velocity
            ship.velocity_x = ship.max_velocity
        elif ship.velocity_x < -ship.max_velocity:
            ship.velocity_x = -ship.max_velocity

        if ship.velocity_y > ship.max_velocity:
            ship.velocity_y = ship.max_velocity
        elif ship.velocity_y < -ship.max_velocity:
            ship.velocity_y = -ship.max_velocity

        if abs(ship.velocity_x) < 0.1:                  # if ship is moving very slowly, stop it
            ship.velocity_x = 0.0

        if abs(ship.velocity_y) < 0.1:
            ship.velocity_y = 0.0

        ship.move()                                     # move the ship and draw it
        ship.draw(st7789.WHITE)

    def update_roids():
        '''
        Update roid positions handle ship collisions
        Returns True if not hit, False if hit
        '''
        not_hit = True

        for roid in roids:                  # for each roid, erase, move then draw
            roid.draw(st7789.BLACK)
            roid.move()
            roid.draw(st7789.WHITE)

            if roid.collision(ship):        # check for roid/ship collision
                ship.draw(st7789.BLACK)     # erase ship
                ship.velocity_x = 0.0       # stop movement
                ship.velocity_y = 0.0

                not_hit = False

        return not_hit

    def explode_ship():
        '''
        Increment explosion step and alternate between drawing
        explosion poly and explosion poly rotated 45 degrees

        Returns True when explosion is finished
        '''
        ship.counter += 1
        if ship.counter % 2 == 0:
            tft.polygon(explosion_poly, ship.x, ship.y, st7789.BLACK, 0.785398)
            tft.polygon(explosion_poly, ship.x, ship.y, st7789.WHITE)
        else:
            tft.polygon(explosion_poly, ship.x, ship.y, st7789.WHITE, 0.785398)
            tft.polygon(explosion_poly, ship.x, ship.y, st7789.BLACK)

        if ship.counter > 25:
            # erase explosion, move ship to center and stop explosion
            tft.polygon(explosion_poly, ship.x, ship.y, st7789.BLACK)
            # move ship to center
            ship.x = width >> 1
            ship.y = height >> 1
            ship.counter = 0
            return True

        return False

    # enable display and clear screen
    tft.init()
    tft.fill(st7789.BLACK)
    width = tft.width()
    height = tft.height()

    rad_max = 2 * math.pi               # 360' in radians

    # ship variables
    ship_alive = True
    ship_radius = 7
    ship_rad_frame = rad_max / 16       # turning rate per frame
    ship_accel_frame = 0.6              # acceleration per frame
    ship_drag_frame = 0.015             # drag factor per frame

    ship_poly = [(-7, -7), (7, 0), (-7, 7), (-3, 0), (-7, -7)]

    ship = Poly(
        ship_poly,
        x=width >> 1,
        y=height >> 1,
        v_x=0,
        v_y=0,
        radius=ship_radius,
        spin=0.0)

    explosion_poly = [(-4, -4), (-4, 4), (4, 4), (4, -4), (-4, -4)]

    # asteroid variables
    roid_radius = [5, 10, 16]
    roid_scale = [0.33, 0.66, 1.0]

    roid_poly = [
        (-5, -15), (-2, -13), (11, -14), (15, -7), (14, 0),
        (16, 5), (11, 16), (7, 16), (-7, 14), (-14, 7),
        (-13, 1), (-14, -8), (-11, -15), (-5, -15)]
    roids = []

    # missile variables
    missile_velocity = 8
    missile_max = 8
    missile_life = 20
    missile_rate = 200
    missile_last = utime.ticks_ms()
    missile_poly = [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    missiles = []

    frame_time = 60                         # target frame rate delay

    # game loop
    while True:
        last_frame = utime.ticks_ms()

        # add roids if there are none
        if len(roids) == 0:
            roids = [create_roid(2), create_roid(2)]

        update_missiles()

        # Erase the ship
        ship.draw(st7789.BLACK)

        if ship_alive:
            # if left button pressed
            if buttons.left.value() == 0:
                # rotate ship counter clockwise
                ship.rotate(-ship_rad_frame)

            # if right button pressed
            if buttons.right.value() == 0:
                 # rotate ship clockwise
                ship.rotate(ship_rad_frame)

            # if hyperspace button pressed move ship to random location
            if buttons.hyper and buttons.hyper.value() == 0:
                diameter = ship.radius * 2
                ship.x = random.randint(diameter, width - diameter)
                ship.y = random.randint(diameter, height - diameter)

                # stop movement
                ship.velocity_x = 0.0
                ship.velocity_y = 0.0

            # if thrust button pressed
            if buttons.thrust.value() == 0:
                # accelerate ship in the direction the ship is facing
                d_y = math.sin(ship.angle) * ship_accel_frame
                d_x = math.cos(ship.angle) * ship_accel_frame
                ship.velocity_x += d_x
                ship.velocity_y += d_y

            # if the fire button is pressed and less than missile_max active missles
            if buttons.fire.value() == 0 and len(missiles) < missile_max:

                # limit missiles firing to once every missile_rate ms
                if last_frame - missile_last > missile_rate:

                    # fire missile in direction ship in facing
                    v_y = math.sin(ship.angle) * missile_velocity
                    v_x = math.cos(ship.angle) * missile_velocity

                    # create new missile
                    missile = Poly(
                        missile_poly,
                        x=ship.x,
                        y=ship.y,
                        v_x=v_x,
                        v_y=v_y,
                        angle=ship.angle,
                        radius=1,
                        spin=0.0,
                        counter=missile_life)

                    # add to to missile list and save last fire time
                    missiles.append(missile)
                    missile_last = last_frame

            update_ship()

        else:
            # explosion animation until returns True
            ship_alive = explode_ship()

        # update roids and return if ship was not hit
        not_hit = update_roids()
        if ship_alive:
            ship_alive = not_hit

        # wait until frame time expires
        while utime.ticks_ms() - last_frame < frame_time:
            pass


main()
