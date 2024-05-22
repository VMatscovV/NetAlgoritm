from input_func import *

F = in_1.pop(0)
Lim = in_1


maximum = 0


x1_max = -1
x2_max = -1

minimum = 1000

x1_min = -1
x2_min = -1

for x1 in range(0, 101):
    x1 = x1 / 10

    for x2 in range(0, 101):
        x2 = x2 / 10

        count = 0

        for i in Lim:
            if i[2] == "<":
                count += (x1 * i[0] + x2 * i[1]) <= i[3]
            else:
                count += (x1 * i[0] + x2 * i[1]) >= i[3]

        if count == 3:
            z = x1 * F[0] + x2 * F[1]
            if maximum < z:
                maximum = z
                x1_max = x1
                x2_max = x2
            if minimum > z:
                minimum = z
                x1_min = x1
                x2_min = x2

        print(x1)
        print(x2)
        print(count)


if maximum == 0:
    print("Нет решения на области определения")

else:
    if x1_max >= 10 or x2_max >= 10:
        print("Максимум не существует")

    else:
        print(f"max = {maximum}")
        print(f"x1 = {x1_max}")
        print(f"x2 = {x2_max}")

    print(f"min = {minimum}")
    print(f"x1 = {x1_min}")
    print(f"x2 = {x2_min}")
