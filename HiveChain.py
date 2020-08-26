from beem import Hive
from beem.nodelist import NodeList


class HiveChain:
    """docstring for Chain"""
    # Setup node list for Hive
    # Create Hive chain obj

    def __init__(self):
        self.nodelist = NodeList()
        self.nodelist.update_nodes()
        self.hive_nodes = self.nodelist.get_hive_nodes()
        self.chain = Hive(node=self.hive_nodes)
        self.chain.set_default_nodes(self.hive_nodes)
