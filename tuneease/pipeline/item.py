class Item(object):
    def __init__(self, name, start, end, vel=0, pitch=0, track=0, value=""):
        self.name = name
        self.start = start  # start step
        self.end = end  # end step
        self.vel = vel
        self.pitch = pitch
        self.track = track
        self.value = value

    def __repr__(self):
        return (
            f"Item(name={self.name:>10s}, start={self.start:>4d}, end={self.end:>4d}, "
            f"vel={self.vel:>3d}, pitch={self.pitch:>3d}, track={self.track:>2d}, "
            f"value={self.value:>10s})\n"
        )

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.start == other.start
            and self.pitch == other.pitch
            and self.track == other.track
        )
