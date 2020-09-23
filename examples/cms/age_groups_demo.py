from models.cms.core.CMSConfigBuilder import CMSConfigBuilder
from models.cms.core.CMS_Object import *
from models.cms.core.CMS_Operator import EMODL
from models.cms.utils.Groups import CMSGroup, CMSGroupManager

if __name__ == "__main__":
    g = CMSGroup(
        species={"S": 1000, "I": 200, "R": 300},
        parameters={"alpha": 10, "beta": 20},
        name="0_5"
    )

    g1 = CMSGroup(
        species={"S": 200, "I": 10, "R": 5},
        parameters={"alpha": 3, "beta": 4},
        name="5_10"
    )

    g2 = CMSGroup(
        species={"S": 500, "I": 30, "R": 7},
        parameters={"alpha": 5, "beta": 9},
        name="10_15"
    )

    cb = CMSConfigBuilder.from_defaults()
    m = CMSGroupManager(
        groups=(g, g1),
        cb=cb
    )

    # create species
    m.create_species()

    # create reactions
    m.create_item(Reaction("infection-latent", m.species.S, m.species.R, EMODL.MULTIPLY("lambda", EMODL.SUBTRACT(m.parameters.alpha, "3"), m.species.S)))

    # create observes
    m.create_item(Observe("all-s", EMODL.ADD(m.species.S)), across_group=True)

    # test: check results
    model = m.cb.to_model()
    print(model)

