import os
from luigi import ExternalTask, Parameter, Task, LocalTarget, format
from luigi.contrib.s3 import S3Target
"""
I wrote target.py file in csci_utils package, and got it running locally.
However I couldn't get it run on travis. So I have to hack it here to
make it run on travis.
"""
from .target import SuffixPreservingLocalTarget


class Downloader(Task):
    """
    Super class serves as parent to DownloadModel and DownloadImage.
    Children classes can reuse the functions
    """
    S3_ROOT = "s3://yyhpset4/pset_4/saved_models"
    LOCAL_ROOT = os.path.abspath('data')

    def requires(self):
        # Depends on the SavedModel ExternalTask being complete
        # i.e. the file must exist on S3 in order to copy it locally
        raise NotImplementedError()

    def output(self):
        raise NotImplementedError()

    def run(self):
        """
        Reads remote file and atomically write it to disk
        """
        out_fd = self.output()
        out_dir = os.path.join(self.LOCAL_ROOT, self.SHARED_RELATIVE_PATH)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        in_fd = self.input()

        with in_fd.open('r') as fd:
            result = fd.read()
            with out_fd.open('w') as o_fd:
                o_fd.write(result)


class DownloadModel(Downloader):
    SHARED_RELATIVE_PATH = 'saved_models'
    model = Parameter()  # luigi parameter

    def requires(self):
        """
        requires save model
        """
        return SavedModel(self.model)

    def output(self):
        out_file = os.path.join(self.LOCAL_ROOT, self.SHARED_RELATIVE_PATH, self.model)
        return SuffixPreservingLocalTarget(out_file, format=format.Nop)


class DownloadImage(Downloader):
    SHARED_RELATIVE_PATH = 'images'

    image = Parameter()  # Luigi parameter

    def requires(self):
        """
        Requires Content Image
        """
        # Depends on the ContentImage ExternalTask being complete
        return ContentImage(self.image)

    def output(self):
        out_file = os.path.join(self.LOCAL_ROOT, self.SHARED_RELATIVE_PATH, self.image)
        return SuffixPreservingLocalTarget(out_file, format=format.Nop)


class ContentImage(ExternalTask):
    IMAGE_ROOT = "s3://yyhpset4/pset_4/images"  # Root S3 path, as a constant

    # Name of the image
    image = Parameter()  # Filename of the image under the root s3 path

    def output(self):
        """
        :return: S3 Target on remote server
        """
        return S3Target('{}/{}'.format(self.IMAGE_ROOT, self.image),
                        format=format.Nop)


class SavedModel(ExternalTask):
    MODEL_ROOT = "s3://yyhpset4/pset_4/saved_models"  # Root S3 path, as a constant

    model = Parameter()  # Filename of the model

    def output(self):
        """
        :return: S3 Target on remote server
        """
        return S3Target('{}/{}'.format(self.MODEL_ROOT, self.model),
                        format=format.Nop)
