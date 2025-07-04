import arcade
import arcade.gui
from views.PauseView import PauseView
from views.GameOverView import GameOverView
import math

# views.MenuView is the file location
# import MenuView takes the class
from views.MenuView import MenuView
from classes.PlayerCharacter import PlayerCharacter
from classes.EnemyCharacter import EnemyCharacter

# Constants - They do not change throughout the whole program
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "My Platformer Game"

SPRITE_NATIVE_SIZE = 32
CHARACTER_SCALING = 2

SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * CHARACTER_SCALING)
UPDATES_PER_FRAME = 4

RIGHT_FACING = 0
LEFT_FACING = 1

# NEW CONSTANTS FOR LESSON 3
TILE_SIZE = 16
ENEMY_SCALING = 2
ITEM_SCALING = 2
GUI_SCALING = 4
TILE_SCALING = 2
GRID_PIXEL_SIZE = TILE_SIZE * TILE_SCALING
GRAVITY = 0.6

# Constants for Lesson 4
MOVEMENT_SPEED = 3 * CHARACTER_SCALING
PLAYER_JUMP_SPEED = 6 * CHARACTER_SCALING

ENEMY_SPEED = 2

MUSIC_PATH = "assets/sounds/bg.wav"
MUSIC_VOLUME = 0

class MyGame(arcade.View):

    def __init__(self,MUSIC_PATH):
        super().__init__()
        self.player = None
        self.tile_map = None
        self.scene = None
        self.end_of_map = 0

        # Camera chapter attributes
        self.screen_center_x = 0
        self.screen_center_y = 0
        self.camera = None
        self.camera_gui = None

        self.physics_engine = None
        self.going = True

        self.game_over = False
        self.max_level = 4
        self.level = 1

        self.enemy_list = None

        self.music_path = MUSIC_PATH
        self.music = None
        self.currently_playing = None

        # GUI manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()


        # Create a button
        self.music_muted = True
        self.mute_button = arcade.gui.UIFlatButton(text="Unmute", width=100)
        self.mute_button.on_click = self.on_click_mute_button

        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(self.mute_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="right",
                anchor_y="bottom",
                child=self.v_box)
        )

    def setup(self):
        self.heart_list = arcade.SpriteList()
        self.weapon_gui_list = arcade.SpriteList()
        self.player = PlayerCharacter(RIGHT_FACING,
                                      CHARACTER_SCALING,
                                      UPDATES_PER_FRAME)

        pos = 10
        for x in range(self.player.health):
            heart = arcade.Sprite("assets/heart_32x32.png")
            heart.top = SCREEN_HEIGHT -20
            heart.left = pos
            self.heart_list.append(heart)
            pos += SPRITE_NATIVE_SIZE +20


        if self.music is not None:
            if self.music.is_playing(self.currently_playing):
                self.music.stop(self.currently_playing)
        self.music = arcade.Sound(self.music_path,streaming=True)
        self.currently_playing = self.music.play(MUSIC_VOLUME,loop=True)
        self.level = 1
        self.load_level(self.level)



    def on_click_mute_button(self, event):
        if self.music_muted:
            self.music_muted = False
            self.mute_button.text = "Mute"
            self.music.set_volume(20, self.currently_playing)
        else:
            self.music_muted = True
            self.mute_button.text = "Unmute"
            self.music.set_volume(0, self.currently_playing)




    def load_level(self, level):
        map_name = "tiled_maps/level{0}.tmx".format(level)

        layer_options = {
            "Terrain": {"use_spatial_hash": True},
            "Traps": {"use_spatial_hash": False},
            "Items": {"use_spatial_hash": True}
        }

        self.tile_map = arcade.load_tilemap(map_name,
                                            scaling=TILE_SCALING,
                                            layer_options=layer_options)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.scene.add_sprite("Player", self.player)
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # this method will be created afterwards
        self.pan_camera_to_user()
        arcade.set_background_color(arcade.color.TURQUOISE_GREEN)

        if "Enemies" in self.tile_map.object_lists:
            enemies_layer = self.tile_map.object_lists["Enemies"]
            for ene in enemies_layer:
                # cartesian conversion to fit positions into the tiles
                cartesian = self.tile_map.get_cartesian(
                    abs(ene.shape[0]), abs(ene.shape[1])
                )
                enemy_type = ene.properties["name"]

                if enemy_type == "chicken":
                    enemy = EnemyCharacter(
                        "chicken", ENEMY_SCALING, UPDATES_PER_FRAME,
                        "assets/Enemies/Chicken/run_sep/",
                        "assets/Enemies/Chicken/hit_sep/", 100
                    )
                elif enemy_type == "bunny":
                    enemy = EnemyCharacter(
                        "bunny", ENEMY_SCALING, UPDATES_PER_FRAME,
                        "assets/Enemies/Bunny/run_sep/",
                        "assets/Enemies/Bunny/hit_sep/", 150,
                        scale_mod=0.773
                    )
                elif enemy_type == "plant":
                    enemy = EnemyCharacter(
                        "plant", ENEMY_SCALING,UPDATES_PER_FRAME,
                        None, "assets/Enemies/Plant/hit_sep/",
                        100, e_idle_path="assets/Enemies/Plant/attack_sep/",
                        scale_mod=0.773, state="idle"
                    )
                else:
                    enemy = False

                if enemy is not False:
                    enemy.center_x = cartesian[0] * GRID_PIXEL_SIZE
                    enemy.center_y = cartesian[1] * GRID_PIXEL_SIZE

                    if "boundary_left" in ene.properties:
                        bound_cart = self.tile_map.get_cartesian(
                            abs(ene.properties["boundary_left"]*TILE_SCALING),
                            abs(ene.shape[1])
                        )
                        enemy.boundary_left = bound_cart[0] * GRID_PIXEL_SIZE

                    if "boundary_right" in ene.properties:
                        bound_cart = self.tile_map.get_cartesian(
                            abs(ene.properties["boundary_right"]*TILE_SCALING),
                            abs(ene.shape[1])
                        )
                        enemy.boundary_right = bound_cart[0] * GRID_PIXEL_SIZE

                    if enemy.state == "running":
                        enemy.change_x = ENEMY_SPEED
                    self.scene.add_sprite("Enemies", enemy)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=GRAVITY,
            walls=self.scene["Terrain"]
        )

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Alternating background colors
        colors = [arcade.color.SKY_BLUE, arcade.color.LIGHT_GREEN]
        num_sections = 10
        section_width = SCREEN_WIDTH / num_sections

        # Get the camera's left edge position
        camera_left = self.camera.position[0]

        for i in range(num_sections):
            color = colors[i % len(colors)]
            arcade.draw_rectangle_filled(
                camera_left + section_width * (i + 0.5), SCREEN_HEIGHT / 2,
                section_width, SCREEN_HEIGHT,
                color
            )

        self.scene.draw()
        self.camera_gui.use()

        self.heart_list.draw()
        self.weapon_gui_list.draw()
        self.manager.draw()

    def on_resize(self, width, height):
        self.camera.resize(width, height)

    def pan_camera_to_user(self, panning_fraction=1.0):
        self.screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        self.screen_center_y = 0
        if self.screen_center_x < 0:
            self.screen_center_x = 0
        elif self.screen_center_x >= self.end_of_map - self.camera.viewport_width:
            self.screen_center_x = self.end_of_map - self.camera.viewport_width
        user_centered = self.screen_center_x, self.screen_center_y
        self.camera.move_to(user_centered, panning_fraction)
        self.camera.use()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.A:
            self.player.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A:
            if self.player.change_x < 0:
                self.player.change_x = 0
        elif key == arcade.key.D:
            if self.player.change_x > 0:
                self.player.change_x = 0
        elif key == arcade.key.P:
            pause = PauseView(self)
            self.window.show_view(pause)

    def on_update(self, delta_time):
        if not self.game_over:
            if self.player.center_x >= self.end_of_map:
                if self.level < self.max_level:
                    self.going = True
                    self.level += 1
                    self.load_level(self.level)
            if self.player.center_x <= 0:
                if self.level > 1:
                    self.going = False
                    self.level -= 1
                    self.load_level(self.level)
            if self.player.center_y < -100:
                self.player.center_x = GRID_PIXEL_SIZE
                self.player.center_y = GRID_PIXEL_SIZE

            if "Traps" in self.tile_map.sprite_lists:
                if len(arcade.check_for_collision_with_list(self.player, self.scene["Traps"])) > 0:
                    self.scene = self.player.take_damage(self.scene, self.heart_list)
                    if self.scene.game_over:
                        self.window.show_view(GameOverView(self))

            if "Enemies" in self.tile_map.object_lists:
                enemy_sprites = self.scene["Enemies"].sprite_list  # Get the SpriteList from scene
                for enemy in enemy_sprites:
                    if arcade.check_for_collision(self.player, enemy):  # Check collision with each enemy
                        # Check if the player is above the enemy and falling
                        if self.player.center_y > enemy.center_y and self.player.change_y < 0:
                            enemy.remove_from_sprite_lists()
                            self.player.change_y = PLAYER_JUMP_SPEED / 2  # Make the player bounce a bit
                        else:
                            self.scene = self.player.take_damage(self.scene, self.heart_list)
                            if self.scene.game_over:
                                self.window.show_view(GameOverView(self))

                for enemy in self.scene["Enemies"]:
                    if len(arcade.check_for_collision_with_list(
                            enemy, self.scene["Terrain"])) > 0:
                        enemy.change_x *= -1
                    if len(arcade.check_for_collision_with_list(
                            enemy, self.scene["Enemies"])) > 0:
                        enemy.change_x *= -1

            self.scene.update_animation(delta_time, ["Enemies"])
            self.scene.update(["Enemies"])

            for enemy in self.scene["Enemies"]:
                if enemy.right < 0 or enemy.left > self.end_of_map:
                    enemy.remove_from_sprite_lists()
                if (enemy.boundary_right and
                        enemy.right > enemy.boundary_right and
                        enemy.change_x > 0):
                    enemy.change_x *= -1

                if (enemy.boundary_left and
                        enemy.left < enemy.boundary_left and
                        enemy.change_x < 0):
                    enemy.change_x *= -1

            self.scene.update_animation(delta_time,
                                        ["Terrain", "Player"])
            self.physics_engine.update()
            self.pan_camera_to_user(panning_fraction=0.12)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu = MenuView(MyGame(MUSIC_PATH))
    window.show_view(menu)
    arcade.run()

if __name__ == "__main__":
    main()