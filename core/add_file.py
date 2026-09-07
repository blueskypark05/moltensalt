import json

def AddFile(file_path, config):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to add file: {file_path}\n\n{e}")
    try:
        data_info = [data["source"], data["url"]]
        data_export = []
        info_str = []
        for material_dict in data["experiment"]:
            name = material_dict["name"]
            info_list = []
            for composition_dict in material_dict["composition"]:
                composition = [composition_dict["unit"],[]]
                for material in config["materials"][name]:
                    composition[1].append(composition_dict.get(material,0))
                for thermal_dict in composition_dict["thermal_properties"]:
                    info_list.append(thermal_dict["property"])
                    data_value = [thermal_dict["property"], thermal_dict["value"], thermal_dict["unit"], thermal_dict["temperature_range"], thermal_dict.get("weight", 100)]
                    data_export.append([name, composition, data_value])
            info_str.append(name + " - " + ", ".join(info_list))
        data_info.append(", ".join(info_str))

    except KeyError as e:
        raise ValueError(f"Missing required key in file: {file_path}\n\n{e}")
    except Exception as e:
        raise ValueError(f"Unexpected error occurred while processing file: {file_path}\n\n{e}")
    return data_info, data_export