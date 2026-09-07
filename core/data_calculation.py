from core.unit_conversion import convert_units, temperature_converter
import numpy as np
import numexpr as ne


def calculate_raw_data(data, min_temp, max_temp, config, step=0.01):
    export_data = []
    for property_name in data.keys():
        for name in data[property_name].keys():
            x = []
            for com in data[property_name][name].keys():
                correlation_list = data[property_name][name][com]
                for correlation in correlation_list:
                    if not correlation["selected"]:
                        continue
                    try:
                        temp_range = correlation["temperature_range"].split(" ")[0].split("-")
                        temp_unit = correlation["temperature_range"].split(" ")[1]
                        loc_temp = [temperature_converter(float(temp), temp_unit, config) for temp in temp_range]
                        loc_min_temp = max(loc_temp[0], min_temp)
                        loc_max_temp = min(loc_temp[1], max_temp)
                        if loc_min_temp > loc_max_temp:
                            continue
                        out_temp = np.arange(loc_min_temp, loc_max_temp+step/2, step)
                        loc_temp = temperature_converter(out_temp, temp_unit, config, backward=True)
                    except Exception as e:
                        raise ValueError(f"Error processing temperature at {correlation['index']}: {e}")
                    try:
                        molar_mass = sum([com[i] * config["composition"][config["materials"][name][i]] for i in range(len(com))])
                    except Exception as e:
                        raise ValueError(f"Error calculating molar mass at {correlation['index']}: {e}")
                    try:
                        value = ne.evaluate(correlation["correlation"], local_dict={"T": loc_temp, "M":molar_mass, "e":np.e})
                    except Exception as e:
                        raise ValueError(f"Error evaluating correlation at {correlation['index']}: {e}")
                    try:
                        value = convert_units(value, property_name, correlation["unit"], config, molar_mass)
                        value = np.asanyarray(value, dtype=float)
                        if value.ndim == 0:
                            value = np.full(out_temp.shape, value.item(), dtype=float)
                        elif value.shape != out_temp.shape:
                            raise ValueError(f"Temperature and result lengths do not match at {correlation['index']}.")
                    except Exception as e:
                        raise ValueError(f"Error converting units at {correlation['index']}: {e}")
                    
                    x.append([out_temp, value, rf"{name}{com}, {correlation['index']}"])
            if not x:
                continue
            x.append([rf"{property_name} ({config["base_units"][property_name]})", rf"{property_name} vs temperature", [min_temp, max_temp]])
            export_data.append(x)
    return export_data
