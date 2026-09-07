from pathlib import Path
def make_tree(data, config, filelist):
    tree = {}
    for i in range(len(data)):
        try:
            for item in data[i]:
                name = item[0]
                composition = item[1][1]
                composition_unit = item[1][0]
                thermal_property = item[2]
                if thermal_property[0] not in config["properties"]:
                    continue
                if tree.get(thermal_property[0]) is None:
                    tree[thermal_property[0]] = {}
                if composition_unit == "weight percent":
                    x = []
                    for j in range(len(config["materials"][name])):
                        x.append(composition[j] / config["composition"][config["materials"][name][j]])
                    composition = [i / sum(x) for i in x]
                elif composition_unit == "mass fraction":
                    x = []
                    for j in range(len(config["materials"][name])):
                        x.append(composition[j] / config["composition"][config["materials"][name][j]])
                    composition = [i / sum(x) for i in x]
                composition_key = tuple(round(i, 2) for i in composition)
                if tree[thermal_property[0]].get(name) is None:
                    tree[thermal_property[0]][name] = {}
                if tree[thermal_property[0]][name].get(composition_key) is None:
                    tree[thermal_property[0]][name][composition_key] = []
                x = {"correlation": thermal_property[1], "unit": thermal_property[2], "temperature_range": thermal_property[3], "weight": thermal_property[4], "selected": False, "index": i + 1}
                tree[thermal_property[0]][name][composition_key].append(x)
        except Exception as e:
            raise ValueError(f"Error processing data at {Path(filelist[i]).name}: {e}")
    return tree