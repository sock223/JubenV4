import pyglet
import sys
sys.setrecursionlimit(1000000)  # 例如这里设置为一百万

window = pyglet.window.Window(resizable=True)

@window.event
def on_draw():
    if player.get_texture():
        player.get_texture().blit(0, 0)
    else:
        pyglet.app.exit()

if __name__ == "__main__":
    player = pyglet.media.Player()
    source = pyglet.media.load("/Users/yibo/Desktop/JuBenAI2/juben/NotImportant/111.mp4")

    player.queue(source)

    if source and source.video_format:
        width = source.video_format.width
        height = source.video_format.height
        window.set_size(width,height)
    window.set_location(-100,0)
    player.play()


    pyglet.app.run()

