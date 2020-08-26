from beem import Steem
from beem.nodelist import NodeList


class SteemChain:
    """docstring for Chain"""
    # Setup node list for Steemit
    # Create Steem chain obj

    def __init__(self):
        self.nodelist = NodeList()
        self.nodelist.update_nodes()
        self.steem_nodes = self.nodelist.get_steem_nodes()
        self.chain = Steem(node=self.steem_nodes)
        self.chain.set_default_nodes(self.steem_nodes)
