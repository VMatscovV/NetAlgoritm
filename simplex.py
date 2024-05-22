import sys
from input_func import *


def printer(F_answer, X_answers):
    print("F = ", F_answer, sep="")

    for i in range(len(X_answers)):
        print('x', i + 1, " = ", X_answers[i], sep="")


def FindNonesInArray(arr):
    nbase = []
    for i in range(len(arr)):
        if arr[i] is None:
            nbase.append(i)
    return nbase


def ArrayAddBasisValue(arr):
    flag = False
    resizedArr = [0] * (len(arr) + 1)
    for i in range(len(arr)):

        if arr[i] == '<' or arr[i] == '>':
            flag = True
            resizedArr[i] = 1

        if flag:
            if arr[i] == '<' or arr[i] == '>':
                resizedArr[i + 1] = '='
            else:
                resizedArr[i + 1] = arr[i]
        else:
            resizedArr[i] = arr[i]

    return resizedArr


def IsColumnAllNulls(numOfCol, table):
    for i in range(len(table)):
        if table[i][numOfCol] != 0:
            return False

    return True


def isNegativeInLine(lineType, numOfLine, table):
    if lineType == "col":
        for i in range(len(table)):
            if table[i][numOfLine] < 0:
                return True
        return False
    elif lineType == "row":
        for i in range(len(table)):
            if table[numOfLine][i] < 0:
                return True
        return False


def FindTheSmallestNegative(lineType, numOfLine, table):
    smallestNum = 0
    numOfAlterLine = 0
    if lineType == "col":
        for i in range(len(table)):
            if table[i][numOfLine] < smallestNum:
                smallestNum = table[i][numOfLine]
                numOfAlterLine = i
        return numOfAlterLine
    elif lineType == "row":
        for i in range(len(table)):
            if table[numOfLine][i] < smallestNum:
                smallestNum = table[numOfLine][i]
                numOfAlterLine = i
        return numOfAlterLine


def FindSmallestOrBiggestInLine(line, mode):
    if mode == '-':
        pivot = sys.maxsize
    elif mode == '+':
        pivot = (-sys.maxsize - 1)
    else:
        print("Некорректный режим")
        return

    index = -1
    for i in range(len(line)):
        if line[i] is not None:
            if mode == '-':
                if line[i] < pivot:
                    pivot = line[i]
                    index = i
            elif mode == '+':
                if line[i] > pivot:
                    pivot = line[i]
                    index = i

    return index


def PullCreator(func, length):
    pull = [0] * length
    for i in range(length):
        if func[i] == "max" or func[i] == "min":
            return pull
        pull[i] = func[i]


def FunCounter(fun):
    funCount = 0
    for i in range(len(fun)):
        if fun[i] == "max" or fun[i] == "min":
            break
        else:
            funCount += 1
    return funCount


def ArrayPrinter(arr):
    for i in range(len(arr)):
        print(arr[i])


class Simplex:

    def __init__(self, function, limits):
        self.function = function
        self.limits = limits

        self.__inequalityCount = 0
        self.__signBase = []
        self.__basisHimSelf = []
        self.__countMainFun = FunCounter(self.function)
        self.__globalFun = 0
        self.__basisPull = []
        self.__deltas = []
        self.__isResolvable = True

        self.__simplexTable = []

    def Main(self):

        self.__CanonShow()

        self.__StartTableMaker()

        self.__CheckAndUpdateSimplexTable()

        if not self.__isResolvable:
            print("Решение задачи не существует, так как есть строка с отрицательным b, "
                  "без отрицательных значений в самой строке")
        else:
            self.__UniversalDeltaSolution()

            self.__Optimizer()

            if not self.__isResolvable:
                if self.function[-1] == "max":
                    print("Решения не существует, все значения в ", "n",
                          "-м столбце отрицательны", sep="")
                    print()
                elif self.function[-1] == "min":
                    print("Решения не существует, все значения в столбце положительны")
                    print()
            else:
                F_Xes = self.__AnswerConstructor()

                printer(F_Xes[0], F_Xes[1])

    def __CanonShow(self):
        for i in range(len(self.limits)):

            if self.limits[i][-2] == '>':
                self.__signBase.append('>')
                for j in range(len(self.limits[i])):
                    if self.limits[i][j] != '>':
                        self.limits[i][j] = (self.limits[i][j] * (-1))
            elif self.limits[i][-2] == '<':
                self.__signBase.append('<')
            else:
                self.__signBase.append('=')

            if self.limits[i][-2] != '=':
                self.limits[i] = ArrayAddBasisValue(self.limits[i])
                self.__inequalityCount += 1

        print("Меняем знаки у ограничений с ≥, путём умножения на -1,"
              "для каждого ограничения с неравенством добавляем "
              "дополнительные переменные и приводим к каноническому виду:")
        ArrayPrinter(self.limits)
        print()

        return

    def __StartTableMaker(self):

        globalFun = self.__countMainFun + self.__inequalityCount

        self.__simplexTable = [[0] * (globalFun + 1) for _ in range(len(self.limits))]

        self.__basisPull = PullCreator(self.function, globalFun)

        for i in range(len(self.__simplexTable)):
            NullFlag = False
            for j in range(len(self.__simplexTable[i])):
                if j != (len(self.__simplexTable[i]) - 1):
                    if j < self.__countMainFun:
                        self.__simplexTable[i][j] = self.limits[i][j]
                    elif IsColumnAllNulls(j, self.__simplexTable) and (NullFlag is False) and (
                            self.__signBase[i] != '='):
                        self.__simplexTable[i][j] = 1
                        NullFlag = True
                else:
                    self.__simplexTable[i][-1] = self.limits[i][-1]
                    break

        if self.__inequalityCount == len(self.limits):
            for i in range(len(self.__basisPull)):
                if self.__basisPull[i] == 0:
                    self.__basisHimSelf.append(i)
        else:
            self.__basisHimSelf = [None] * len(self.limits)

            for i in range(len(self.__basisPull)):
                if self.__basisPull[i] == 0:
                    isNum_Num_Row = self.__FindOnlyOneNumInCol(i)
                    if isNum_Num_Row[0] and isNum_Num_Row[1] == 1:
                        self.__basisHimSelf[isNum_Num_Row[2]] = i

            NoneBase = FindNonesInArray(self.__basisHimSelf)

            if len(NoneBase) > 0:
                print(self.__basisHimSelf)
                print("Не хватает базисных переменных. Попробую найти их среди основных переменных.")
                for i in range(len(NoneBase)):
                    for j in range(len(self.__simplexTable[i])):
                        find = self.__FindOnlyOneNumInCol(j)
                        if find[0]:
                            if NoneBase[i] == find[2]:
                                if find[1] == 1:
                                    self.__basisHimSelf[NoneBase[i]] = j
                                    break
                                else:
                                    for k in range(len(self.__simplexTable[NoneBase[i]])):
                                        self.__simplexTable[NoneBase[i]][k] = self.__simplexTable[NoneBase[i]][k] / \
                                                                              find[1]

                                    self.__basisHimSelf[NoneBase[i]] = j
                                    break

                NoneBase = FindNonesInArray(self.__basisHimSelf)

                if len(NoneBase) > 0:
                    print("Базис всё ещё не определён... Применим исключение Гаусса!")
                    for i in range(len(NoneBase)):
                        for j in range(len(self.__simplexTable[i])):
                            if not self.__isNumInBasis(j):
                                self.UpdateTableCore(NoneBase[i], j)
                                break

        print("Началная симплекс таблица:")
        print("C =", self.__basisPull)
        ArrayPrinter(self.__simplexTable)
        print("Базисные переменные определенны(если +1):")
        print(self.__basisHimSelf)
        print()

        return

    def __isNumInBasis(self, num):
        for i in range(len(self.__basisHimSelf)):
            if self.__basisHimSelf is not None:
                if self.__basisHimSelf[i] == num:
                    return True
        return False

    def __FindOnlyOneNumInCol(self, colNum):
        numHimSelf = None
        numCount = 0
        rowNum = None
        for i in range(len(self.__simplexTable)):
            if self.__simplexTable[i][colNum] != 0:
                numCount += 1
                numHimSelf = self.__simplexTable[i][colNum]
                rowNum = i

        if numCount == 1:
            return True, numHimSelf, rowNum
        else:
            return False, numHimSelf, rowNum

    def __CheckAndUpdateSimplexTable(self):
        while isNegativeInLine("col", -1, self.__simplexTable):

            numOfNeedRow = FindTheSmallestNegative("col", -1, self.__simplexTable)
            if isNegativeInLine("row", numOfNeedRow, self.__simplexTable):
                numOfNeedCol = FindTheSmallestNegative("row", numOfNeedRow, self.__simplexTable)

                self.UpdateTableCore(numOfNeedRow, numOfNeedCol)
            else:
                self.__isResolvable = False
                break

        return

    def UpdateTableCore(self, numOfNeedRow, numOfNeedCol):
        updatedTable = [el[:] for el in self.__simplexTable]

        self.__basisHimSelf[numOfNeedRow] = numOfNeedCol

        for i in range(len(self.__simplexTable[numOfNeedRow])):
            updatedTable[numOfNeedRow][i] = self.__simplexTable[numOfNeedRow][i] / self.__simplexTable[numOfNeedRow][
                numOfNeedCol]

        for i in range(len(self.__simplexTable)):
            for j in range(len(self.__simplexTable[i])):
                if i != numOfNeedRow:
                    updatedTable[i][j] = updatedTable[i][j] - (
                            updatedTable[numOfNeedRow][j] * self.__simplexTable[i][numOfNeedCol])

        print("Обновлённая симплекс таблица:")
        self.__simplexTable = updatedTable
        ArrayPrinter(self.__simplexTable)
        print("Базисные переменные(если +1):")
        print(self.__basisHimSelf)
        print("Обнолено через адрес: Столбец:", numOfNeedCol, "Строка:", numOfNeedRow)
        print()

        return

    def __UniversalDeltaSolution(self):
        self.__deltas = [0] * len(self.__basisPull)
        for i in range(len(self.__basisPull)):
            for j in range(len(self.__simplexTable)):
                self.__deltas[i] += self.__basisPull[self.__basisHimSelf[j]] * self.__simplexTable[j][i]
            self.__deltas[i] -= self.__basisPull[i]

        self.__deltas.append(0)
        for i in range(len(self.__simplexTable)):
            self.__deltas[-1] += self.__basisPull[self.__basisHimSelf[i]] * self.__simplexTable[i][-1]
        self.__deltas[-1] -= self.__basisPull[-1]

        print("Текущие дельты:", self.__deltas)
        print()

        return

    def __OptimaCheck(self):
        self.__deltas[-1] = 0
        for i in range(len(self.__deltas)):
            if self.function[-1] == "max":
                if self.__deltas[i] < 0:
                    return False
            elif self.function[-1] == "min":
                if self.__deltas[i] > 0:
                    return False
        return True

    def Q_relationFinder(self, index):
        Q = [0] * len(self.__simplexTable)
        for i in range(len(self.__simplexTable)):
            if self.__simplexTable[i][index] > 0:
                Q[i] = self.__simplexTable[i][-1] / self.__simplexTable[i][index]
            else:
                Q[i] = None

        return FindSmallestOrBiggestInLine(Q, '-')

    def __Optimizer(self):
        numOfNeedCol = None
        while not self.__OptimaCheck():
            print("План не оптимален:")
            print()
            if self.function[-1] == 'max':
                numOfNeedCol = FindSmallestOrBiggestInLine(self.__deltas, '-')
            elif self.function[-1] == 'min':
                numOfNeedCol = FindSmallestOrBiggestInLine(self.__deltas, '+')

            numOfNeedRow = self.Q_relationFinder(numOfNeedCol)

            if numOfNeedRow == -1:
                self.__isResolvable = False
                break

            self.UpdateTableCore(numOfNeedRow, numOfNeedCol)

            self.__UniversalDeltaSolution()

        if self.__isResolvable:
            print("План оптимален")
            print()

        return

    def __AnswerConstructor(self):
        plan = [0] * len(self.__basisPull)
        for i in range(len(self.__basisHimSelf)):
            plan[self.__basisHimSelf[i]] = self.__simplexTable[i][-1]

        F_answer = 0
        for i in range(len(plan)):
            F_answer += plan[i] * self.__basisPull[i]

        X_answers = [0] * (len(self.function) - 1)

        for i in range(len(X_answers)):
            X_answers[i] = plan[i]

        return F_answer, X_answers


F = in_5.pop(0)

Limits = in_5

claculator = Simplex(F, Limits)
claculator.Main()
