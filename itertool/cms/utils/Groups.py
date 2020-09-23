import collections
import copy
from enum import Enum

from models.cms.core.CMS_Object import Observe, Reaction, list_all_objects
from models.cms.core.CMS_Operator import EMODL


class CMSGroup:
    def __init__(self, species, parameters, name):
        self.species = species
        self.parameters = parameters
        self.name = name


class CMSGroupManager:
    def __init__(self, groups, cb):
        self.groups = []
        self.available_species = set()
        self.available_parameters = set()
        self.species = None
        self.ag_species = None
        self.parameters = None
        self.cb = cb

        for g in groups:
            self.add_group(g)

    def create_species(self):
        for g in self.groups:
            for species, value in g.species.items():
                # print("{}_{} = {}".format(species, g.name, value))
                self.cb.add_species('{}_{}'.format(species, g.name), str(value) if value else value)

    def add_group(self, group):
        self.available_species = self.available_species.union(group.species.keys())
        self.available_parameters = self.available_parameters.union(group.parameters.keys())
        self.groups.append(group)
        self.species = Enum('Species', list(self.available_species))
        self.parameters = Enum('Parameters', list(self.available_parameters))

    def create_item(self, obj, across_group=False):
        if not across_group:
            for group in self.groups:
                o = copy.deepcopy(obj)
                g = self.transform_emodl(o, group.name)
                self.add_to_config_builder(g, group.name)
        else:
            g = self.transform_emodl(obj)
            self.add_to_config_builder(g)

    def add_to_config_builder(self, g, group_name=None):
        if isinstance(g, Observe):
            self.cb.observe.append(g)
        elif isinstance(g, Reaction):
            g.name = '{}-{}'.format(g.name, group_name)
            self.cb.reaction.append(g)

    def transform_emodl(self, element, group_name=None):
        all_objects = list_all_objects()
        if type(element) in EMODL.all_operators() or type(element) in all_objects:
            for attr, value in element.__dict__.items():
                if not isinstance(value, str) and isinstance(value, collections.Iterable):
                    if group_name:
                        setattr(element, attr, list(map(lambda e: self.transform_emodl(e, group_name), value)))
                    else:
                        result = list(map(lambda e: self.transform_emodl(e), value))
                        values = []
                        for v in result:
                            if isinstance(v, list):
                                values.extend(v)
                            else:
                                values.append(v)

                        setattr(element, attr, values)
                else:
                    setattr(element, attr, self.transform_emodl(value, group_name))
            return element

        if isinstance(element, self.species) or isinstance(element, self.parameters):
            if group_name:
                return "{}_{}".format(element.name, group_name)
            else:
                g = []
                for group in self.groups:
                    g.append(self.transform_emodl(element, group.name))

                return g

        return element