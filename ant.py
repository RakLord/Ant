from config import *


class Ant(pg.sprite.Sprite):
    def __init__(self, draw_surf, home, pher_type=1):
        super().__init__()
        self.draw_surf = draw_surf
        self.home = home
        self.image = pg.Surface((12, 21)).convert()
        self.image.set_colorkey(0)
        color_brown = (80, 42, 42)
        self.pher_type = pher_type

        pg.draw.ellipse(self.image, color_brown, [4, 6, 4, 9])

        self.original_image = pg.transform.rotate(self.image.copy(), -90)
        self.rect = self.image.get_rect(center=self.home)
        self.angle = randint(0, 360)
        self.desire_direction = pg.Vector2(cos(radians(self.angle)), sin(radians(self.angle)))
        self.position = pg.Vector2(self.rect.center)
        self.velocity = pg.Vector2(0, 0)
        self.last_pheromone = home

    def update(self, delta_time, **kwargs):
        pheromones = kwargs["pheromones"]
        cur_w, cur_h = self.draw_surf.get_size()
        mid_sensor_result = left_sensor_result = right_sensor_result = (0, 0, 0)
        random_angle = randint(0, 360)
        acceleration = pg.Vector2(0, 0)
        wander_strength = 0.15
        max_speed = 12
        steer_strength = 3

        if self.position.distance_to(self.last_pheromone) > 24:
            pheromones.add(Trail(self.position, self.pher_type))
            self.last_pheromone = pg.Vector2(self.rect.center)

        mid_sensor_left = self.vint(self.position + pg.Vector2(21, -3).rotate(self.angle))
        mid_sensor_right = self.vint(self.position + pg.Vector2(21, 3).rotate(self.angle))
        left_sensor_1 = self.vint(self.position + pg.Vector2(18, -14).rotate(self.angle))
        left_sensor_2 = self.vint(self.position + pg.Vector2(16, -21).rotate(self.angle))
        right_sensor_1 = self.vint(self.position + pg.Vector2(18, 14).rotate(self.angle))
        right_sensor_2 = self.vint(self.position + pg.Vector2(16, 21).rotate(self.angle))

        # Checks if the sensor points are inside a rect and if they are grab the pixel values to the l/r of each sensor
        # and check the max value of either the left/right sensor for each R G B value
        if self.draw_surf.get_rect().collidepoint(mid_sensor_left) and self.draw_surf.get_rect().collidepoint(mid_sensor_right):
            mid_sensor_left_right = self.draw_surf.get_at(mid_sensor_left)[:3]
            mid_sensor_right_right = self.draw_surf.get_at(mid_sensor_right)[:3]
            mid_sensor_result = (max(mid_sensor_left_right[0], mid_sensor_right_right[0]),
                                 max(mid_sensor_left_right[1], mid_sensor_right_right[1]),
                                 max(mid_sensor_left_right[2], mid_sensor_right_right[2]))

        if self.draw_surf.get_rect().collidepoint(left_sensor_1) and self.draw_surf.get_rect().collidepoint(left_sensor_2):
            left_sensor_right_1 = self.draw_surf.get_at(left_sensor_1)[:3]
            left_sensor_right_2 = self.draw_surf.get_at(left_sensor_2)[:3]
            left_sensor_result = (max(left_sensor_right_1[0], left_sensor_right_2[0]),
                                  max(left_sensor_right_1[1], left_sensor_right_2[1]),
                                  max(left_sensor_right_1[2], left_sensor_right_2[2]))

        if self.draw_surf.get_rect().collidepoint(right_sensor_1) and self.draw_surf.get_rect().collidepoint(right_sensor_2):
            right_sensor_right_1 = self.draw_surf.get_at(right_sensor_1)[:3]
            right_sensor_right_2 = self.draw_surf.get_at(right_sensor_2)[:3]
            right_sensor_result = (max(right_sensor_right_1[0], right_sensor_right_2[0]),
                                   max(right_sensor_right_1[1], right_sensor_right_2[1]),
                                   max(right_sensor_right_1[2], right_sensor_right_2[2]))

        #  If the max sensor value (index 2 blue pixel) is gt the max value of either the left sensor,
        #  right. And the mid sensor green / blue is == 0 Then set the desired direction to forward. And set wander to 0
        if mid_sensor_result[2] > max(left_sensor_result[2], right_sensor_result[2]) and mid_sensor_result[:2] == (0, 0):
            self.desire_direction = pg.Vector2(1, 0).rotate(self.angle).normalize()  # Set dir to forwards
            wander_strength = 0

        elif left_sensor_result[2] > right_sensor_result[2] and left_sensor_result[:2] == (0, 0):
            self.desire_direction = pg.Vector2(1, -2).rotate(self.angle).normalize()  # Set dir to left (0,-1)
            wander_strength = 0

        elif right_sensor_result[2] > left_sensor_result[2] and right_sensor_result[:2] == (0, 0):
            self.desire_direction = pg.Vector2(1, 2).rotate(self.angle).normalize()  # Set dir to right (0, 1)
            wander_strength = 0

        # Avoid edges
        if not self.draw_surf.get_rect().collidepoint(left_sensor_2) and self.draw_surf.get_rect().collidepoint(right_sensor_2):
            self.desire_direction += pg.Vector2(0, 1).rotate(self.angle)
            wander_strength = 0
            steer_strength = 4

        elif not self.draw_surf.get_rect().collidepoint(right_sensor_2) and self.draw_surf.get_rect().collidepoint(left_sensor_2):
            self.desire_direction += pg.Vector2(0, -1).rotate(self.angle)
            wander_strength = 0
            steer_strength = 4

        elif not self.draw_surf.get_rect().collidepoint(self.vint(self.position + pg.Vector2(21, 0).rotate(self.angle))):
            self.desire_direction += pg.Vector2(-1, 0).rotate(self.angle)
            wander_strength = 0
            steer_strength = 5

        random_direction = pg.Vector2(cos(radians(random_angle)), sin(radians(random_angle)))

        if self.desire_direction != (0, 0) and wander_strength != 0:
            self.desire_direction = pg.Vector2(self.desire_direction + random_direction * wander_strength).normalize()

        final_desire_direction = self.desire_direction * max_speed
        desire_direction_with_steer = (final_desire_direction - self.velocity) * steer_strength
        acceleration = desire_direction_with_steer if pg.Vector2(desire_direction_with_steer).magnitude() <= steer_strength else pg.Vector2(desire_direction_with_steer.normalize() * steer_strength)
        final_velocity = self.velocity + acceleration * delta_time

        self.velocity = final_velocity if pg.Vector2(final_velocity).magnitude() <= max_speed else pg.Vector2(final_velocity.normalize() * max_speed)
        self.position += self.velocity * delta_time
        self.angle = degrees(atan2(self.velocity[1], self.velocity[0]))
        self.image = pg.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.position

    @staticmethod
    def vint(vector2):
        return int(vector2[0]), int(vector2[1])


class Trail(pg.sprite.Sprite):
    def __init__(self, position, pheromone_type):
        super().__init__()
        self.type = pheromone_type
        self.image = pg.Surface((8, 8))
        self.image.fill(0)
        self.image.set_colorkey(0)
        self.rect = self.image.get_rect(center=position)
        self.strength = 500

    def update(self, delta_time):
        self.strength -= ((delta_time / 10) * FPS) * (60/FPS)
        if self.strength < 0:
            return self.kill()
        trail_strength = self.strength / 500
        self.image.fill(0)
        if self.type == 1:
            pg.draw.circle(self.image, [0, 0, 90 * trail_strength + 10], [4, 4], 4)

        if self.type == 2:
            pg.draw.circle(self.image, [0, 90 * trail_strength + 10, 0], [4, 4], 4)


