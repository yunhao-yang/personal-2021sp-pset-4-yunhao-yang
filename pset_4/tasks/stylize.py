import luigi
from csci_utils.luigi.target import SuffixPreservingLocalTarget
from .data import DownloadModel, DownloadImage

class Stylize:
    model = None
    image = None

    def requires(self):
        return {
            'image': None,
            'model': None,
        }

    def output(self):
        # return SuffixPreservingLocalTarget of the stylized image
        raise NotImplementedError()