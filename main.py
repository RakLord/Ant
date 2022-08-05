from config import *
from ant import Ant


def main():
    pg.init()
    pg.display.set_caption("Ants")

    if FULLSCREEN:
        current_resolution = (pg.display.Info().current_h, pg.display.Info().current_h)
        screen = pg.display.set_mode(current_resolution, pg.SCALED)
        pg.mouse.set_visible(False)
    else:
        screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

    cur_w, cur_h = screen.get_size()
    home = (cur_w / 2, cur_h / 2)

    ants = pg.sprite.Group()
    pheromones = pg.sprite.Group()

    for n in range(ANTS):
        ants.add(Ant(screen, home))

    clock = pg.time.Clock()
    fps_checker = 0

    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.K_ESCAPE:

                return

        delta_time = clock.tick(FPS) / 100

        pheromones.update(delta_time)
        ants.update(delta_time, pheromones=pheromones)

        screen.fill(0)

        pheromones.draw(screen)

        ants.draw(screen)

        pg.display.update()

        fps_checker += 1
        if fps_checker >= FPS:
            print(f"FPS: {round(clock.get_fps(), 1)} | DT: {delta_time}")
            fps_checker = 0


if __name__ == '__main__':
    main()
    pg.quit()
    exit()


