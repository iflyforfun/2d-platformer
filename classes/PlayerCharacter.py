import arcade

RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self, direction, scaling, updates_per_frame):
        super().__init__()

        self.character_face_direction = direction
        self.cur_run_texture = 0
        self.walk_sound_delay = 0.4
        self.walk_sound_last = 0
        self.cur_idle_texture = 0
        self.cur_hit_texture = 0
        self.scale = scaling
        self.updates_per_frame = updates_per_frame

        self.landed = True
        self.health = 3
        self.immune = False
        self.immune_wait = 0

        self.weapon_list = list()

        idle_path = "assets/Virtual Guy/idle_sep/"
        run_path = "assets/Virtual Guy/run_sep/"

        jump_path = "assets/Virtual Guy/Jump (32x32).png"
        fall_path = "assets/Virtual Guy/Fall (32x32).png"

        self.jump_texture = load_texture_pair(jump_path)
        self.fall_texture = load_texture_pair(fall_path)

        self.idle_textures = []
        for i in range(11):
            texture = load_texture_pair(f"{idle_path}tile0{i}.png")
            self.idle_textures.append(texture)

        self.walk_textures = []
        for i in range(12):
            texture = load_texture_pair(f"{run_path}tile0{i}.png")
            self.walk_textures.append(texture)

        hit_path = "assets/Virtual Guy/hit_sep/"
        self.hit_textures = []
        for i in range(7):
            texture = load_texture_pair(f"{hit_path}tile0{i}.png")
            self.hit_textures.append(texture)

    def take_damage(self,scene_info,heart_list):
        if not self.immune:
            self.health -= 1
            heart_list.pop()
            if self.health == 0:
                scene_info.game_over = True
            else:
                scene_info.game_over = False
                self.immune = True
        return scene_info


    def update_animation(self, delta_time: float = 1 / 60):

        # changing direction the player is facing
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        self.cur_run_texture += 1
        self.cur_idle_texture += 1

        if self.cur_run_texture > 11 * self.updates_per_frame:
            self.cur_run_texture = 0
        if self.cur_idle_texture > 10 * self.updates_per_frame:
            self.cur_idle_texture = 0

        run_frame = self.cur_run_texture // self.updates_per_frame
        idle_frame = self.cur_idle_texture // self.updates_per_frame
        direction = self.character_face_direction

        # idle animations first
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_textures[idle_frame][direction]

        # jump animation second
        elif self.change_y > 0:
            self.texture = self.jump_texture[direction]

        # fall animation third
        elif self.change_y < 0:
            self.texture = self.fall_texture[direction]

        # running animation last without any condition
        else:
            self.texture = self.walk_textures[run_frame][direction]

        # check if the player has been hit and is immune so the damage can't stack
        if self.immune is True:
            self.immune_wait += 1
            if self.immune_wait > 12 * self.updates_per_frame:
                self.immune_wait = 0
                self.immune = False

        # getting hit
        if self.immune is True:
            hit_frame = (self.immune_wait // 2) // self.updates_per_frame
            self.texture = self.hit_textures[hit_frame][direction]
            return


