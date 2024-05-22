class TransportMatrix:
    def __init__(self, raw_input_array):

        self.suppliers = []
        for i in range(1, len(raw_input_array)):
            self.suppliers.append(raw_input_array[i][0])

        self.clients = raw_input_array[0][1:]

        self.transportation_costs = \
            [row[1:len(raw_input_array)+1] for row in raw_input_array[1:len(raw_input_array[0])+1]]

        self.transportation_volumes = []
        v = self.transportation_costs[0].copy()
        for i in range(len(v)):
            v[i] = 0
        for i in range(len(self.transportation_costs)):
            self.transportation_volumes.append(v.copy())

        self.main_cost = 0

        self.coefficients_suppliers = []
        self.coefficients_clients = []

        self.empty_cells_coefficients = []
        v = self.transportation_costs[0].copy()
        for i in range(len(v)):
            v[i] = None
        for i in range(len(self.transportation_costs)):
            self.empty_cells_coefficients.append(v.copy())

    def is_task_type_close(self):
        return sum(self.suppliers) == sum(self.clients)

    def make_task_type_closed(self):
        if sum(self.suppliers) > sum(self.clients):
            self.clients.append(sum(self.suppliers) - sum(self.clients))

            for i in range(len(self.suppliers)):
                self.transportation_costs[i].append(0)
                self.transportation_volumes[i].append(0)
                self.empty_cells_coefficients[i].append(None)

        elif sum(self.suppliers) < sum(self.clients):
            self.suppliers.append(sum(self.clients) - sum(self.suppliers))

            self.transportation_costs.append([])
            self.transportation_volumes.append([])
            self.empty_cells_coefficients.append([])
            for i in range(len(self.clients)):

                self.transportation_costs[-1].append(0)
                self.transportation_volumes[-1].append(0)
                self.empty_cells_coefficients[-1].append(None)

    def recalculate_main_cost(self):
        self.main_cost = 0
        for i in range(len(self.transportation_volumes)):
            for j in range(len(self.transportation_volumes[0])):
                self.main_cost += self.transportation_costs[i][j] * self.transportation_volumes[i][j]

    def build_start_plan_minimum_element_method(self):
        # Using minimum element method

        closed_columns = []
        closed_rows = []

        current_suppliers = self.suppliers.copy()
        current_clients = self.clients.copy()

        def take_minimum_cost(columns, rows):
            current_min = float("inf")
            current_coord = None
            for i in range(len(self.transportation_costs)):
                if i in rows:
                    continue
                for j in range(len(self.transportation_costs[0])):
                    if j in columns:
                        continue
                    if self.transportation_costs[i][j] < current_min:
                        current_min = self.transportation_costs[i][j]
                        current_coord = [i, j]

            return current_coord

        while True:
            minimum_cords = take_minimum_cost(closed_columns, closed_rows)
            if minimum_cords is None:
                break
            supplier_id, client_id = minimum_cords[0], minimum_cords[1]

            self.transportation_volumes[supplier_id][client_id] = min(current_suppliers[supplier_id], current_clients[client_id])

            current_suppliers[supplier_id] -= self.transportation_volumes[supplier_id][client_id]
            current_clients[client_id] -= self.transportation_volumes[supplier_id][client_id]

            if current_suppliers[supplier_id] == 0:
                closed_rows.append(supplier_id)
            if current_clients[client_id] == 0:
                closed_columns.append(client_id)

    def build_start_plan_north_west_corner_method(self):

        current_suppliers = self.suppliers.copy()
        current_clients = self.clients.copy()

        supplier_id, client_id = [0, 0]

        while True:
            self.transportation_volumes[supplier_id][client_id] = min(current_suppliers[supplier_id],
                                                                      current_clients[client_id])

            current_suppliers[supplier_id] -= self.transportation_volumes[supplier_id][client_id]
            current_clients[client_id] -= self.transportation_volumes[supplier_id][client_id]

            if current_suppliers[supplier_id] == 0:
                supplier_id += 1
            if current_clients[client_id] == 0:
                client_id += 1

            if supplier_id >= len(self.transportation_volumes) and client_id >= len(self.transportation_volumes[0]):
                break

    def reset_coefficients(self):
        self.coefficients_suppliers = []
        self.coefficients_clients = []

        for i in range(len(self.suppliers)):
            self.coefficients_suppliers.append(None)

        for i in range(len(self.clients)):
            self.coefficients_clients.append(None)

        for i in range(len(self.empty_cells_coefficients)):
            for j in range(len(self.empty_cells_coefficients[0])):
                self.empty_cells_coefficients[i][j] = None

    def take_linear_equations(self, epsilans):
        result = []
        eps_buffer = []

        for i in range(len(self.transportation_volumes)):
            for j in range(len(self.transportation_volumes[0])):

                if self.transportation_volumes[i][j] != 0:
                    result.append([j, i, self.transportation_costs[i][j]])

        if len(result) < len(self.suppliers) + len(self.clients) - 1:
            print("AHTUNG", epsilans)

        for i in eps_buffer:
            epsilans.append(i)

        return result

    def calculate_coefficients(self, epsilans):

        self.reset_coefficients()

        linear_equations = self.take_linear_equations(epsilans)

        print(len(linear_equations), linear_equations)

        coef_helper_clients = [None] * len(self.clients)
        coef_helper_suppliers = [None] * len(self.suppliers)

        current_check = 0
        current_check_family = "CLIENTS"
        checked = {"CLIENTS": [], "SUPPLIERS": []}

        self.coefficients_suppliers[0] = 0

        while (None in self.coefficients_suppliers) or (None in self.coefficients_clients):
            print(self.coefficients_clients, self.coefficients_suppliers)
            print(linear_equations)
            for equation in linear_equations:

                if (self.coefficients_clients[equation[0]] is not None) and (self.coefficients_suppliers[equation[1]] is None):
                    self.coefficients_suppliers[equation[1]] = self.coefficients_clients[equation[0]] - equation[2]
                elif (self.coefficients_clients[equation[0]] is None) and (self.coefficients_suppliers[equation[1]] is not None):
                    self.coefficients_clients[equation[0]] = self.coefficients_suppliers[equation[1]] + equation[2]

            if self.coefficients_clients == coef_helper_clients and self.coefficients_suppliers == coef_helper_suppliers:

                isolated_clients = []
                isolated_suppliers = []

                for i in range(len(self.coefficients_clients)):
                    if self.coefficients_clients[i] is None:
                        isolated_clients.append(i)
                for i in range(len(self.coefficients_suppliers)):
                    if self.coefficients_suppliers[i] is None:
                        isolated_suppliers.append(i)

                if len(linear_equations) == len(self.clients) + len(self.suppliers) - 1:
                    linear_equations.pop(-1)

                if current_check_family == "CLIENTS":
                    flag = True
                    if current_check not in isolated_clients:
                        current_check += 1
                    else:
                        for i in range(len(self.coefficients_suppliers)):
                            if [i, current_check] not in checked["CLIENTS"] and flag:
                                checked["CLIENTS"].append([i, current_check])
                                linear_equations.append([current_check, i, self.transportation_costs[i][current_check]])
                                flag = False
                                continue
                            if i == len(self.coefficients_suppliers)-1:
                                if current_check == len(self.coefficients_clients):
                                    current_check_family = "SUPPLIERS"
                                    current_check = 0
                                else:
                                    current_check += 1
                elif current_check_family == "SUPPLIERS":
                    flag = True
                    if current_check not in isolated_suppliers:
                        current_check += 1
                    else:
                        for i in range(len(self.coefficients_clients)):
                            if [current_check, i] not in checked["SUPPLIERS"] and flag:
                                checked["SUPPLIERS"].append([current_check, i])
                                linear_equations.append([i, current_check, self.transportation_costs[current_check][i]])
                                flag = False
                                continue
                            if i == len(self.coefficients_clients)-1:
                                if current_check == len(self.coefficients_suppliers):
                                    current_check_family = "SUPPLIERS"
                                    current_check = 0
                                else:
                                    current_check += 1

                print("VERY BAD", isolated_clients, isolated_suppliers)
                print("CHECKED:", checked, "CURRENT_CHECK_FAMILY:", current_check_family, "CURRENT_CHECK:", current_check)


            coef_helper_clients = self.coefficients_clients.copy()
            coef_helper_suppliers = self.coefficients_suppliers.copy()

        for i in linear_equations:
            if [i[1], i[0]] not in epsilans:
                epsilans.append([i[1], i[0]])

        for i in range(len(self.empty_cells_coefficients)):
            for j in range(len(self.empty_cells_coefficients[0])):
                if self.transportation_volumes[i][j] == 0 and [i, j] not in epsilans:

                    self.empty_cells_coefficients[i][j] =\
                        self.coefficients_clients[j] - self.coefficients_suppliers[i] - self.transportation_costs[i][j]

    def is_all_coefficients_negative(self):
        for i in range(len(self.empty_cells_coefficients)):
            for j in range(len(self.empty_cells_coefficients[0])):
                if self.empty_cells_coefficients[i][j]:
                    if self.empty_cells_coefficients[i][j] >= 0:
                        return False
        return True

    def maximum_coefficient_coords(self):
        max_coef = float("-inf")
        max_coef_coord = None

        for i in range(len(self.empty_cells_coefficients)):
            for j in range(len(self.empty_cells_coefficients[0])):

                if self.empty_cells_coefficients[i][j] is not None:
                    if self.empty_cells_coefficients[i][j] > max_coef:

                        max_coef = self.empty_cells_coefficients[i][j]
                        max_coef_coord = [i, j]

        return max_coef_coord

    def build_cycle(self, start_with_columns_flag, start_coords=None, print_flag=True):

        class CycleRoute:
            def __init__(self, start_point=(0, 0), value=0):
                self.points_coords = [start_point, ]
                self.value = []
                self.used_rows = []
                self.used_columns = []
                self.close_status = False

            def add_point(self, new_point, new_point_value):

                if self.last_point()[1] == new_point[1]:
                    self.used_columns.append(new_point[1])
                if self.last_point()[0] == new_point[0]:
                    self.used_rows.append(new_point[0])

                self.points_coords.append(new_point)
                self.value.append(new_point_value)

            def fork(self, new_points, new_points_values):
                result = []

                for i in range(len(new_points)):
                    new_route = CycleRoute()

                    new_route.points_coords = self.points_coords.copy()
                    new_route.value = self.value.copy()
                    new_route.used_rows = self.used_rows.copy()
                    new_route.used_columns = self.used_columns.copy()
                    new_route.add_point(new_points[i], new_points_values[i])

                    result.append(new_route)

                return result

            def last_point(self):
                return self.points_coords[-1]

            def first_point(self):
                return self.points_coords[0]

            def close(self):
                self.close_status = True

            def calculate_value(self):
                result = 0
                for i in range(len(self.value) // 2):
                    result += self.value[i*2] - self.value[i*2+1]

                return result

            def is_cycle_successfully_ends(self, target_value):
                return (self.first_point()[0] == self.last_point()[0]) and \
                       (self.first_point()[1] == self.last_point()[1]) and \
                       ((self.calculate_value() == target_value) or not print_flag)

            def print(self):
                if print_flag:
                    print("Route: ", self.points_coords)
                    print("Value: ", self.value)
                    print("Used rows: ", self.used_rows)
                    print("Used columns: ", self.used_columns)
                    print("Close status: ", self.close_status)
                    print()

        def take_available_rows(coords, start_point, used_rows):
            available_rows = []

            for j in range(len(self.transportation_volumes[0])):
                if coords[0] in used_rows:
                    continue
                if j == coords[1]:
                    continue
                if self.empty_cells_coefficients[coords[0]][j] is not None or (not print_flag and self.transportation_volumes[0][j] == 0):
                    if coords[0] != start_point[0] or j != start_point[1]:
                        continue
                available_rows.append([coords[0], j])

            return available_rows

        def take_available_columns(coords, start_point, used_columns):
            available_columns = []

            for i in range(len(self.transportation_volumes)):
                if coords[1] in used_columns:
                    continue
                if i == coords[0]:
                    continue
                if self.empty_cells_coefficients[i][coords[1]] is not None or (not print_flag and self.transportation_volumes[i][coords[1]] == 0):
                    if coords[1] != start_point[1] or i != start_point[0]:
                        continue
                available_columns.append([i, coords[1]])

            return available_columns

        def cycle_status(routes_array, target_value):
            is_all_closed = True
            for i in range(len(routes_array)):
                if routes_array[i].is_cycle_successfully_ends(target_value):
                    return "SUCCESSES"
                if not routes_array[i].close_status:
                    is_all_closed = False
            if is_all_closed:
                return "FAIL"
            else:
                return "AGAIN"

        if start_coords is None:
            start_coords = self.maximum_coefficient_coords()
        target_value = self.empty_cells_coefficients[start_coords[0]][start_coords[1]]

        for h in range(2):

            routes_array = [CycleRoute(start_coords, self.transportation_costs[start_coords[0]][start_coords[1]])]

            if start_with_columns_flag:
                h = 0-1
            else:
                h = 0
            while True:
                new_routes = []
                delete_routes = []

                h += 1

                for route in range(len(routes_array)):
                    if h % 2 == 0:
                        points = take_available_columns(routes_array[route].last_point(), start_coords, routes_array[route].used_columns)
                    else:
                        points = take_available_rows(routes_array[route].last_point(), start_coords, routes_array[route].used_rows)
                    if len(points) == 0:
                        routes_array[route].close()
                    if len(points) == 1:
                        point = points[0]
                        if not routes_array[route].close_status:
                            routes_array[route].add_point(point, self.transportation_costs[point[0]][point[1]])

                    if len(points) > 1:
                        if not routes_array[route].close_status:
                            values = []
                            for i in points:
                                values.append(self.transportation_costs[i[0]][i[1]])
                            new_routes.append(routes_array[route].fork(points, values))
                            delete_routes.append(route)

                for i in reversed(range(len(delete_routes))):
                    routes_array.pop(delete_routes[i])
                for i in new_routes:
                    for j in i:
                        routes_array.append(j)

                if print_flag:
                    for route in routes_array:
                        print("Value = ", route.calculate_value())
                        route.print()
                    print("Cycle status: ", cycle_status(routes_array, target_value))
                    print("-"*40)

                main_status = cycle_status(routes_array, target_value)
                if main_status == "SUCCESSES":
                    for i in range(len(routes_array)):
                        if routes_array[i].is_cycle_successfully_ends(target_value):
                            return routes_array[i]
                elif main_status == "FAIL":
                    start_with_columns_flag = not start_with_columns_flag
                    break
                elif main_status == "AGAIN":
                    continue
        return None

    def change_values_by_cycle(self, points_coords):

        epsilans = []

        to_transport = float("inf")
        for i in range(1, len(points_coords)-1, 2):
            if self.transportation_volumes[points_coords[i][0]][points_coords[i][1]] < to_transport:
                to_transport = self.transportation_volumes[points_coords[i][0]][points_coords[i][1]]

        for i in range(1, len(points_coords)-1, 2):
            self.transportation_volumes[points_coords[i][0]][points_coords[i][1]] -= to_transport
            self.transportation_volumes[points_coords[i-1][0]][points_coords[i-1][1]] += to_transport

        for i in range(len(points_coords)-1):
            if self.transportation_volumes[points_coords[i][0]][points_coords[i][1]] == 0:
                epsilans.append([points_coords[i][0], points_coords[i][1]])

        epsilans.pop(-1)
        return epsilans

    def print_data(self):

        print("Supplies: ", self.suppliers)
        print("Clients: ", self.clients)

        print("Transportation costs: ")
        for i in range(len(self.transportation_costs)):
            print(self.transportation_costs[i])

        print("Transportation volumes: ")
        for i in range(len(self.transportation_volumes)):
            print(self.transportation_volumes[i])

        print("Task type: ", end='')
        if self.is_task_type_close():
            print("close")
        else:
            print("open")

        print("Main cost: ", self.main_cost)

        print("Coefficients: ", self.coefficients_suppliers, self.coefficients_clients)

        print("Empty cells coefficients: ")
        for i in range(len(self.empty_cells_coefficients)):
            print(self.empty_cells_coefficients[i])

        print("-"*80)
