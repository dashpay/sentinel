# basically just parse & make it easier to access the MN data from the output of
# "masternodelist full"


class Masternode:
    def __init__(self, collateral, mnobj):
        self.outpoint = collateral
        self.mnobj = mnobj

    @property
    def status(self):
        return self.mnobj["status"]
