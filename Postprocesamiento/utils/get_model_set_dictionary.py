import pyomo.environ as pyo

def get_model_set_dictionary(model: pyo.Model) -> dict:
    set_dict = {}
    for set in model.component_objects(pyo.Set):
        if set.dim() == 0:
            for instance in list(set):
                if instance not in set_dict:
                    set_dict[instance] = set.name
        else:
            continue
    return set_dict