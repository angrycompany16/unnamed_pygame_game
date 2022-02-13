import math

class Vec():
    def __init__(self, vector: list):
        self.vector = vector

    def __getitem__(self, index: int):
        return self.vector[index]

    def __len__(self) -> int:
        return len(self.vector)

    def __str__(self) -> str:
        # begin the string with a bracket
        s = "["

        # loop through all the elements, except the last one bc it shouldn't have a comma after it
        for i in range(len(self) - 1):
            s += str(self[i])
            s += ", "

        # add the last element of the vector to the end of the string
        s += str(self[len(self) - 1])
        
        # close the brackets and return
        s += "]"
        return s

    def __setitem__(self, index, value):
        self.vector[index] = value
        return self.vector[index]

    # using '' to postpone the evaluation of the annotation. Allows us to return the type of the class
    def __add__(self, other: 'Vec') -> 'Vec':
        if isinstance(other, self.__class__):        
            new = Vec([0] * len(self))

            for i in range(len(self)):
                new[i] =  self[i] + other[i]
            
            return new
        else:
            self.operator_type_error("+", type(self), type(other))

    def __sub__(self, other: 'Vec') -> 'Vec':
        if isinstance(other, self.__class__):        
            # inverting the vector and then adding
            inverse = other * -1
            return self + inverse
        else:
            self.operator_type_error("-", type(self), type(other))

    def __mul__(self, other: 'Vec') -> 'Vec':
        if type(other) is float or type(other) is int:
            new = Vec([0] * len(self))

            for i in range(len(self)):
                new[i] =  self[i] * other
            
            return new
        else:
            self.operator_type_error("*", type(self), type(other))

    def magnitude(self):
        s = 0
        for i in range(len(self)):
            s += math.pow(self[i], 2)

        return math.sqrt(s)

    def sqr_magnitude(self):
        s = 0
        for i in range(len(self)):
            s += math.pow(self[i], 2)

        return s

    @staticmethod
    def normalize(vec: 'Vec') -> 'Vec':
        return vec * (1 / vec.magnitude())

    @staticmethod
    def dot(vec1: 'Vec', vec2: 'Vec') -> 'Vec':
        if len(vec1) is len(vec2):
            result = 0
            
            for i in len(vec1):
                result += vec1[i] * vec2[i]

            return result
        else:
            raise Exception("vec1 is of length {} and vec2 is of length {}, they must be of equal length".format(len(vec1), len(vec2)))

    def operator_type_error(self, operator, type1, type2):
        raise TypeError("unsupported operand type(s) for {}: '{}' and '{}'".format(operator, type1, type2))

    def list(self):
        return self.vector

# Contains some static math methods i like
class Math():
    def __init__():
        pass

    @staticmethod
    def clamp(num, min_val, max_val):
       return max(min(num, max_val), min_val)
