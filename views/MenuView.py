import arcade
import arcade.gui

class MenuView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()   # vertical arrangement

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color(arcade.color.BANANA_MANIA)

        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit Game", width=200)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        # attach on_click_start method code to start button
        start_button.on_click = self.on_click_start
        quit_button.on_click = self.on_click_quit

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_hide_view(self):
        self.manager.disable()

    def on_click_start(self, event):
        print("Game Start:", event)
        self.game_view.setup()
        self.window.show_view(self.game_view)

    def on_click_quit(self, event):
        print("Quit Game:", event)
        arcade.exit()

    def on_draw(self):
        self.window.clear()
        self.manager.draw()





