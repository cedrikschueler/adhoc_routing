from Messages.RoutingMessage import RoutingMessage
import struct

class MultiHopChirp(RoutingMessage):

    def __init__(self):
        '''
        Format:

        Origin - Ipv4 - Int
        SquNr - Unsigned Int - Unsigned Int

        Position:
        X - Float
        Y - Float
        Z - Float
        Vx - Float
        Vy - Float
        Vz - Float

        GammaMob - Float
        Value - Float
        HopCount - Int

        =IHffffffffH
        '''
        fmt = "=IHffffffffH"
        super(MultiHopChirp, self).__init__(fmt)

    def serialize(self, data: dict) -> bytearray:
        values = (
            data["Origin"],
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
        Origin, SquNr, X, Y, Z, Vx, Vy, Vz, GammaMob, Value, HopCount = struct.unpack(self.fmt, data)
        return {
            "Origin": Origin,
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
        return 40

if __name__ == "__main__":
    testDict = {
        "Origin": 2130706433,
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
    print(len(ser))
    deser = MH.deserialize(ser)
    print(deser)
