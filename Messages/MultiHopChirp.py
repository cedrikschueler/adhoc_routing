from Messages.RoutingMessage import RoutingMessage
import struct

class MultiHopChirp(RoutingMessage):

    def __init__(self):
        '''
        Format:

        Origin - Ipv4 - Int
        Hop - Ipv4 - Int
        CreationTime - Double - Float
        SquNr - Unsigned Int - Unsigned Int

        Position:
        X - Double - Float
        Y - Double - Float
        Z - Double - Float
        Vx - Double - Float
        Vy - Double - Float
        Vz - Double - Float

        GammaMob - Double - Float
        Value - Double - Float
        HopCount - Integer - Int

        @iidIddddddddi
        '''
        fmt = "@iidIddddddddi"
        super(MultiHopChirp, self).__init__(fmt)

    def serialize(self, data: dict) -> bytearray:
        values = (
            data["Origin"],
            data["Hop"],
            data["CreationTime"],
            data["SquNr"],
            data["X"],
            data["Y"],
            data["Z"],
            data["Vx"],
            data["Vx"],
            data["Vz"],
            data["GammaMob"],
            data["Value"],
            data["HopCount"]
        )
        return struct.pack(self.fmt, *values)

    def deserialize(self, data: bytearray) -> dict:
        Origin, Hop, CreationTime, SquNr, X, Y, Z, Vx, Vy, Vz, GammaMob, Value, HopCount = struct.unpack(self.fmt, data)
        return {
            "Origin": Origin,
            "Hop": Hop,
            "CreationTime": CreationTime,
            "SquNr": SquNr,
            "X": X,
            "Y": Y,
            "Z": Z,
            "Vx": Vx,
            "Vy": Vy,
            "Vz": Vz,
            "GammaMob": GammaMob,
            "Value": Value,
            "HopCount": HopCount
        }

    def length(self) -> int:
        return 92

if __name__ == "__main__":
    testDict = {
        "Origin": 2130706433,
        "Hop": 2130706433,
        "CreationTime": 0,
        "SquNr": 1337,
        "X": 500.0,
        "Y": 500.0,
        "Z": 250.0,
        "Vx": 5.0,
        "Vy": 4.2,
        "Vz": 0.01,
        "GammaMob": 0.42,
        "Value": 1.0,
        "HopCount": 32
    }

    MH = MultiHopChirp()
    ser = MH.serialize(testDict)
    deser = MH.deserialize(ser)
