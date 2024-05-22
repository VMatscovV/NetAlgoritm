from matrix import TransportMatrix
from input_transport import input_array_4 as input_array

matrix = TransportMatrix(input_array)

matrix.print_data()

if not matrix.is_task_type_close():
    matrix.make_task_type_closed()

matrix.print_data()

matrix.build_start_plan_north_west_corner_method()

matrix.print_data()

epsilans = []

previous_costs = []

while True:
    print("-"*100, previous_costs)

    matrix.recalculate_main_cost()

    helper = 0

    if matrix.main_cost in previous_costs:
        for i in previous_costs:
            if i == matrix.main_cost:
                helper += 1

    if helper == 5:
        break

    if len(previous_costs) < 5:
        previous_costs.append(matrix.main_cost)
    else:
        previous_costs.pop(0)
        previous_costs.append(matrix.main_cost)

    matrix.calculate_coefficients(epsilans)

    matrix.print_data()

    if matrix.is_all_coefficients_negative():
        break

    print("Minimum coefficient coordinates: ", matrix.maximum_coefficient_coords())
    coords = matrix.build_cycle(False).points_coords
    print(coords)
    epsilans = matrix.change_values_by_cycle(coords)

    matrix.recalculate_main_cost()
    matrix.print_data()
    print("EPSILANS = ", epsilans)
