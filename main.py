from game import game_environment, player

game = game_environment.GameEnvironment()
player = player.Player('player', 0, 0, 1)

player.print()
game.add_element(player)

while True:
    player.move()
    game.draw_elements_on_canvas()
    game.render()
