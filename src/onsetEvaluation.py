import numpy as np

class Evaluator:

    def __init__(self):

        self.windowTolerance = 0.04

    def process(self, target, approx):

        numTruePositives = 0
        numFalseNegatives = 0
        correctOnsetDistances = np.array([])

        for i in range(len(target)):

            absError = np.abs(target[i] - approx)
            indices = np.where(absError < self.windowTolerance)[0]

            # We have an onset in the window
            if len(indices) > 0:
                numTruePositives += 1
                # Find closest onset in window and measure distance
                idx = absError.argmin()
                correctOnsetDistances = np.append(correctOnsetDistances, absError[idx])
            else: # No onset in the tolerance window = missed onset
                numFalseNegatives += 1

        # Count false positives 
        numFalsePositives = approx.size - numTruePositives

        # Precision drops with increasing false positives
        precision = numTruePositives / float(numTruePositives + numFalsePositives)
        # Recall drops with increasing false negatives
        recall = numTruePositives / float(numTruePositives + numFalseNegatives)
        fMeasure = 2 * precision * recall / (precision + recall)

        outputDic = {   
                        'numTruePositives' : numTruePositives,
                        'numFalseNegatives' : numFalseNegatives,
                        'numFalsePositives' : numFalsePositives,
                        'precision' : precision,
                        'recall' : recall,
                        'fMeasure' : fMeasure,
                        'correctOnsetDistances' : correctOnsetDistances,
                        'meanDistance' : np.mean(correctOnsetDistances),
                        'stdDistance' : np.std(correctOnsetDistances)}

        return outputDic
