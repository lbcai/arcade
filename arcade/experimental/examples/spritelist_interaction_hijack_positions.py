"""
Example showing how we can interact with spritelist using shaders.

We simply hijack the position buffer of the spritelist and
fill it with new data generated by a transform shader.
"""
import math
import arcade

NUM_COINS = 500


class HijackSpritePositions(arcade.Window):

    def __init__(self):
        super().__init__(720, 720, "Hijack Sprite Positions", resizable=True)
        self.time = 0

        # Genreate lots of coins. We don't care about the initial positions
        # since our shader is setting those
        self.coins = arcade.SpriteList()
        for _ in range(NUM_COINS):
            self.coins.append(
                arcade.Sprite(
                    ":resources:images/items/coinGold.png",
                    scale=0.5,
                )
            )
        # Ensure the internal buffers are up to date (size etc)
        self.coins.write_sprite_buffers_to_gpu()

        # This shader simply generate some new positions
        self.position_program = self.ctx.program(
            vertex_shader="""
            #version 330

            // The current time to add some movement
            uniform float time;
            // The bendyness value accelerating rotations
            uniform float bend;

            // The current size of the screen
            uniform vec2 size;

            // The new positions we are writing into a new buffer
            out vec2 out_pos;

            void main() {
                // gl_VertexID is the sprite position in the spriteslist.
                // We can use that to value to create unique positions with
                // some simple math.
                float vertId = float(gl_VertexID);
                out_pos = size / 2.0 + vec2(
                    sin(vertId + time + vertId * bend),
                    cos(vertId + time + vertId * bend)
                ) * vertId;
            }
            """
        )
        self.position_program["size"] = self.get_size()

    def on_draw(self):
        self.clear()

        # Write the new positions directly into the position
        # buffer of the spritelist. A little bit rude, but it works.
        self.coins.geometry.transform(
            self.position_program,
            self.coins.buffer_positions,
            vertices=len(self.coins),
        )
        self.coins.draw()

    def on_update(self, delta_time: float):
        self.time += delta_time
        # Keep updating the current time to animation the movement
        self.position_program["time"] = self.time / 4
        # Update the bendyness value
        self.position_program["bend"] = math.cos(self.time) / 400

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.position_program["size"] = width, height


HijackSpritePositions().run()
