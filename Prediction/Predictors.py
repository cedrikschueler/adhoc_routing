from abc import ABC, abstractmethod
import numpy as np

class PredictionMethod(ABC):
    Np: int

    def __init__(self, Np):
        self.Np = Np

    @abstractmethod
    def fit(self, historicalPositions: [np.array], steeringVector: np.array = np.empty(0),
            plannedWaypoints: [np.array] = []) -> None:
        pass

    @abstractmethod
    def predict(self) -> np.array:
        pass

class BATMobilePredictor(PredictionMethod):
    P: np.array
    tU: float
    wp_reached_range: float
    '''
    Class parameters:
    :param self.P: Position as np.array in format (x, y, z)
    :param self.tU: Timer update interval in seconds
    :param self.reached_range: Range in meter to consider a waypoint as reached

    Inherited parameters:
    :param self.Np: Prediction Lookahead
    '''

    def __init__(self, Np: int, tU: float, wp_reached_range: float, v_max_kmh: float):
        super(BATMobilePredictor, self).__init__(Np)
        self.tU = tU
        self.wp_reached_range = wp_reached_range
        self.v_mpMs = v_max_kmh / 3600  # Convert to meter per millisecond

    def fit(self, historicalPositions: [np.array], v_steer: np.array = np.empty(0), plannedWaypoints: [np.array] = []):

        m_updateInterval_ms = self.tU * 1000
        _currentTime_ms = historicalPositions[-1, 0]
        predictedData = []
        historyData = historicalPositions.copy()

        if (len(historyData) > 0):
            # {
            lastValidData: np.array = historyData[-1].copy()
            currentData: np.array = lastValidData.copy()

            if self.Np == 0:
                predictedData.append(currentData)
            else:
                time_ms: int = int(_currentTime_ms / m_updateInterval_ms) * m_updateInterval_ms
                for i in range(0, self.Np):
                    time_ms += m_updateInterval_ms
                    if not v_steer.size == 0:
                        # Predict with steering Vector
                        # currentData = predictWithSteeringVector(currentData, time_ms)
                        raise Exception("Not implemented yet!")
                    elif plannedWaypoints and not np.any(np.isnan(plannedWaypoints[0])):
                        # Predict with Waypoints
                        # currentData = predictWithTarget(currentData, time_ms)
                        currentData_pos = self.predictWithTarget(currentData, time_ms, plannedWaypoints[0])
                        if np.linalg.norm(currentData_pos - plannedWaypoints[0]) < self.wp_reached_range:
                            plannedWaypoints.pop(0)
                    else:
                        # Predict with history
                        # predictWithHistory(historyData, time_ms)
                        currentData_pos = self.predictWithHistory(historyData, time_ms)

                    currentData[0] = time_ms
                    currentData[1:] = currentData_pos
                    predictedData.append(currentData)
                    historyData = np.vstack((historyData, currentData))  ## Push back current Data
                    historyData = historyData[1:, :]  # Pop first row

        self.P = predictedData[-1][1:]  # Last entry is the desired position?

    def predictWithTarget(self, _currentData, time_ms, target):
        position = _currentData[1:].copy()
        nextData = position + (target - position) / (np.linalg.norm(
            target - position)) * (time_ms - _currentData[0]) * self.v_mpMs

        return nextData

    def predictWithHistory(self, _historyData, _nextTime_ms):
        historyData = _historyData
        if len(historyData) == 1:
            return historyData[-1, 1:]
        else:
            lastValidData = _historyData[-1]
            positionIncrement = np.array([0.0, 0.0, 0.0])
            totalWeigth: float = 0.0
            for i in range(1, len(_historyData)):
                currentData = _historyData[i]
                lastData = _historyData[i - 1]

                weigth: float = 1.0
                increment = (currentData[1:] - lastData[1:]) * weigth / (currentData[0] - lastData[0])
                positionIncrement += increment
                totalWeigth += weigth
            positionIncrement = positionIncrement / totalWeigth

            return lastValidData[1:] + positionIncrement * (_nextTime_ms - lastValidData[0])

    def predict(self) -> np.array:
        '''
        Returns the predicted position as np.array in format (x, y, z)
        :return: Position
        '''
        return self.P

class InterpolatedBatman(BATMobilePredictor):
    def __init__(self, Np: int, tU: float, wp_reached_range: float, v_max_kmh: float, stepSize: float = 0.1):
        super(InterpolatedBatman, self).__init__(Np, tU, wp_reached_range, v_max_kmh)
        self.tU = tU
        self.wp_reached_range = wp_reached_range
        self.stepSize = stepSize

    def fit(self, historicalPositions: [np.array], v_steer: np.array = np.empty(0), plannedWaypoints: [np.array] = []):

        m_updateInterval_ms = self.tU * 1000
        _currentTime_ms = historicalPositions[-1, 0]
        predictedData = []
        historyData = historicalPositions.copy()

        if (len(historyData) > 0):
            # {
            lastValidData: np.array = historyData[-1].copy()
            currentData: np.array = lastValidData.copy()

            if self.Np == 0:
                predictedData.append(currentData)
            else:
                time_ms: int = int(_currentTime_ms / m_updateInterval_ms) * m_updateInterval_ms
                for i in range(0, self.Np):
                    time_ms += m_updateInterval_ms
                    if not v_steer.size == 0:
                        # Predict with steering Vector
                        # currentData = predictWithSteeringVector(currentData, time_ms)
                        raise Exception("Not implemented yet!")
                    elif (len(plannedWaypoints) == 1 and not np.any(np.isnan(plannedWaypoints[0]))) or (
                            len(plannedWaypoints) > 1 and not (
                            np.any(np.isnan(plannedWaypoints[0])) or np.any(np.isnan(plannedWaypoints[1])))):
                        # Predict with Waypoints
                        # currentData = predictWithTarget(currentData, time_ms)
                        merged_version: bool = True

                        if merged_version:
                            if (len(plannedWaypoints) > 1 and not (
                                    np.any(np.isnan(plannedWaypoints[0])) or np.any(np.isnan(plannedWaypoints[1])))):
                                currentData_pos = self.predictWithTargetInterpol(historyData, time_ms,
                                                                                 plannedWaypoints[0],
                                                                                 plannedWaypoints[1])
                            else:
                                # Use BATMobile fallback
                                currentData_pos = self.predictWithTarget(currentData, time_ms, plannedWaypoints[0])
                        else:
                            currentData_pos = self.predictWithTargetInterpol(historyData, time_ms, plannedWaypoints[0],
                                                                             plannedWaypoints[1] if len(
                                                                                 plannedWaypoints) > 1 else
                                                                             plannedWaypoints[0])

                        if np.linalg.norm(currentData_pos - plannedWaypoints[0]) < self.wp_reached_range:
                            plannedWaypoints.pop(0)
                    else:
                        # Predict with history
                        # predictWithHistory(historyData, time_ms)
                        currentData_pos = self.predictWithHistory(historyData, time_ms)

                    currentData[0] = time_ms
                    currentData[1:] = currentData_pos
                    predictedData.append(currentData)
                    historyData = np.vstack((historyData, currentData))  ## Push back current Data
                    historyData = historyData[1:, :]  # Pop first row

        self.P = predictedData[-1][1:]  # Last entry is the desired position?

    def predictWithTargetInterpol(self, _historyData, time_ms, p2, p3):
        p0 = _historyData[0, 1:]
        p1 = _historyData[-1, 1:]

        a = -0.5 * p0 + 1.5 * p1 - 1.5 * p2 + 0.5 * p3
        b = p0 - 2.5 * p1 + 2 * p2 - 0.5 * p3
        c = -0.5 * p0 + 0.5 * p2
        d = p1
        nextData: np.array  # = np.array([0.0, 0.0, 0.0])
        for step in np.arange(0, 1.01,
                              self.stepSize):  # Checks on how many percent of one timer Update Interval the position progresses. Maximum is 100% self.tU
            x = step * self.tU / 1000  # Go to seconds here..
            if (np.linalg.norm(a * x ** 3 + b * x ** 2 + c * x + d - p1) > np.linalg.norm(self.v_mpMs * self.tU)) or (
                    step == 1.0):
                nextData = a * x ** 3 + b * x ** 2 + c * x + d
                break
        return nextData

class SlopePredictor(PredictionMethod):
    P: np.array
    tU: float
    slope: np.array
    t: float

    def __init__(self, Np: int, tU: float):
        super(SlopePredictor, self).__init__(Np)
        self.tU = tU

    def fit(self, historicalPositions: [np.array], steeringVector: np.array = np.empty(0),
            plannedWaypoints: [np.array] = []) -> None:
        self.slope = np.array([0, 0, 0], dtype='float64')
        for i in range(1, len(historicalPositions)):
            self.slope += historicalPositions[i][1:] - historicalPositions[i - 1][1:]
        self.slope /= max(len(historicalPositions) - 1, 1)
        self.P = historicalPositions[-1][1:]

    def predict(self) -> np.array:
        return self.P + self.tU * self.Np * self.slope

class NaivePredictor(PredictionMethod):
    P: np.array

    def __init__(self, Np: int):
        super(NaivePredictor, self).__init__(Np)

    def fit(self, historicalPositions: [np.array], steeringVector: np.array = np.empty(0),
            plannedWaypoints: [np.array] = []) -> None:
        historicalPositions = historicalPositions[1:]   # Time information not needed for this method
        self.P = historicalPositions[-1]

    def predict(self) -> np.array:
        return self.P