import math

def get_vector_from_heading_angle(heading):
    vector = []
    vector.append(math.sin(math.radians(heading)))
    vector.append(0)
    vector.append(math.cos(math.radians(heading)))
    return vector

def get_heading_angle_from_vector(vector):
    return math.degrees(math.atan2(vector[0], vector[2]))

def vector_add(vectorA, vectorB):
    result = []
    result.append(vectorA[0]+vectorB[0])
    result.append(vectorA[1]+vectorB[1])
    result.append(vectorA[2]+vectorB[2])
    return result

def vector_subtract(vectorA, vectorB):
    result = []
    result.append(vectorA[0]-vectorB[0])
    result.append(vectorA[1]-vectorB[1])
    result.append(vectorA[2]-vectorB[2])
    return result

def vector_scale(vector, scale):
    result = []
    result.append(vector[0]*scale)
    result.append(vector[1]*scale)
    result.append(vector[2]*scale)
    return result

def get_vector_between_points(pointA, pointB):
    vector = []
    vector.append(pointB[0] - pointA[0])
    vector.append(pointB[1] - pointA[1])
    vector.append(pointB[2] - pointA[2])
    return vector

def get_vector_length(vector):
    return math.sqrt(vector[0]*vector[0]+vector[1]*vector[1]+vector[2]*vector[2])
    
def vector_normalise(vector):
    vector_length = get_vector_length(vector)
    result = []
    if vector_length > 0.0:
        result.append(vector[0] / vector_length)
        result.append(vector[1] / vector_length)
        result.append(vector[2] / vector_length)
    else:
        result.append(vector[0])
        result.append(vector[1])
        result.append(vector[2])
    return result

def get_distance_between_points(pointA, pointB):
    return get_vector_length(get_vector_between_points(pointA, pointB))