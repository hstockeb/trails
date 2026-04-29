from engine import methods
from engine.backends.base import Backend

_METHOD_MAP = {
    "lighten": methods.lighten.blend,
    "maximum": methods.maximum.blend,
    "average": methods.average.blend,
    "comet": methods.comet.blend,
}


class CPUBackend(Backend):
    def blend(self, accumulator, frame, method, frame_index, total_frames):
        fn = _METHOD_MAP[method]
        return fn(
            accumulator,
            frame,
            frame_index=frame_index,
            total_frames=total_frames,
        )
