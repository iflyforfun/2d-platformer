import arcade
import arcade.gui
from views.MenuView import MenuView


class GameOverView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()   # vertical arrangement

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color(arcade.color.BANANA_MANIA)

        restart_button = arcade.gui.UIFlatButton(text="Restart Game", width=200)
        self.v_box.add(restart_button.with_space_around(bottom=20))

        menu_button = arcade.gui.UIFlatButton(text="Main Menu", width=200)
        self.v_box.add(menu_button.with_space_around(bottom=20))

        # attach on_click_start method code to start button
        restart_button.on_click = self.on_click_restart
        menu_button.on_click = self.on_click_menu

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_hide_view(self):
        self.manager.disable()

    def on_click_restart(self, event):
        self.clear()
        print("Restart: ", event)
        self.game_view.setup()
        self.window.show_view(self.game_view)

    def on_click_menu(self, event):
        self.clear()
        print("Return to Menu: ", event)
        self.window.show_view(MenuView(self.game_view))

    def on_draw(self):
        self.clear()
        self.manager.draw()





