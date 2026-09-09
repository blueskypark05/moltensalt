from core.unit_conversion import convert_units, temperature_converter
import numpy as np
import numexpr as ne


def _calculate_correlation(property_name, name, composition, correlation, config, step, temperature_bounds=None):
    correlation_index = correlation["index"]

    try:
        temp_range, temp_unit = correlation["temperature_range"].split()
        start_temp, end_temp = map(float, temp_range.split("-"))

        start_temp = temperature_converter(start_temp, temp_unit, config)
        end_temp = temperature_converter(end_temp, temp_unit, config)

        if temperature_bounds is not None:
            min_temp, max_temp = temperature_bounds
            start_temp = max(start_temp, min_temp)
            end_temp = min(end_temp, max_temp)

        if start_temp > end_temp:
            return None

        out_temp = np.arange(start_temp, end_temp + step / 2, step)
        calculation_temp = temperature_converter(out_temp, temp_unit, config, backward=True)
    except Exception as e:
        raise ValueError(f"Error processing temperature at {correlation_index}: {e}")

    try:
        materials = config["materials"][name]
        molar_mass = sum(composition[i] * config["composition"][materials[i]] for i in range(len(composition)))
    except Exception as e:
        raise ValueError(f"Error calculating molar mass at {correlation_index}: {e}")

    try:
        value = ne.evaluate(correlation["correlation"], local_dict={"T": calculation_temp, "M": molar_mass, "e": np.e})
    except Exception as e:
        raise ValueError(f"Error evaluating correlation at {correlation_index}: {e}")

    try:
        value = convert_units(value, property_name, correlation["unit"], config, molar_mass)
        value = np.asanyarray(value, dtype=float)

        if value.ndim == 0:
            value = np.full(out_temp.shape, value.item(), dtype=float)
        elif value.shape != out_temp.shape:
            raise ValueError("Temperature and result lengths do not match.")
    except Exception as e:
        raise ValueError(f"Error converting units at {correlation_index}: {e}")

    label = rf"{name}{composition}, {correlation_index}"
    return out_temp, value, label


def calculate_raw_data(data, min_temp, max_temp, config, step=0.01):
    export_data = []
    for property_name in data.keys():
        for name in data[property_name].keys():
            x = []
            for composition in data[property_name][name].keys():
                correlation_list = data[property_name][name][composition]
                for correlation in correlation_list:
                    if not correlation["selected"]:
                        continue

                    result = _calculate_correlation(property_name, name, composition, correlation, config, step, temperature_bounds=(min_temp, max_temp))
                    if result is None:
                        continue

                    out_temp, value, label = result
                    x.append([out_temp, value, label])

            if not x:
                continue

            x.append([rf"{property_name} ({config["base_units"][property_name]})", rf"{property_name} vs temperature", [min_temp, max_temp]])
            export_data.append(x)

    return export_data


def calculate_composition_data(data, min_temp, max_temp, config, step=0.01):
    export_data = []
    for property_name in data.keys():
        for name in data[property_name].keys():
            for composition in data[property_name][name].keys():
                correlation_list = data[property_name][name][composition]
                x = []
                y = []

                for correlation in correlation_list:
                    if not correlation["selected"]:
                        continue

                    result = _calculate_correlation(property_name, name, composition, correlation, config, step)
                    if result is None:
                        continue

                    out_temp, value, label = result
                    x.append([out_temp, value, label])
                    y.append([out_temp, value, correlation["weight"]])

                if not x:
                    continue

                all_temp = np.arange(min(item[0][0] for item in y), max(item[0][-1] for item in y) + step / 2, step)
                weighted_sum = np.zeros_like(all_temp, dtype=float)
                weight_sum = np.zeros_like(all_temp, dtype=float)

                for item in y:
                    item_interp = np.interp(all_temp, item[0], item[1], left=np.nan, right=np.nan)
                    valid = ~np.isnan(item_interp)
                    weighted_sum[valid] += item_interp[valid] * item[2]
                    weight_sum[valid] += item[2]

                x.append([all_temp, weighted_sum / weight_sum, rf"{name}{composition}, weighted average"])
                x.append([rf"{property_name}{composition} ({config["base_units"][property_name]})", rf"{property_name} vs temperature", [min_temp, max_temp]])
                export_data.append(x)

    return export_data
