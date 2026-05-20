import numpy as np

#Normalize helper function
def normalize(vector):
    magnitude = np.linalg.norm(vector)

    if magnitude == 0:
        raise ValueError("Cannot normalize a zero vector")

    return vector / magnitude