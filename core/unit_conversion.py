import numexpr as ne

def convert_units(value, property_name, unit, config, molar_mass=None):
    return ne.evaluate(config["units"][property_name][unit], local_dict={'Y': value, 'M': molar_mass})


def temperature_converter(value, unit, config, backward = False):
    if backward:
        if unit == "C" or unit == "°C":
            return ne.evaluate("Y-273.15", local_dict={'Y': value})
        elif unit == "K":
            return ne.evaluate("Y", local_dict={'Y': value})
    else:
        if unit == "C" or unit == "°C":
            return ne.evaluate("Y+273.15", local_dict={'Y': value})
        elif unit == "K":
            return ne.evaluate("Y", local_dict={'Y': value})
