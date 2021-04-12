from .target import SuffixPreservingLocalTarget
"""
I wrote target.py file in csci_utils package, and got it running locally.
However I couldn't get it run on travis. So I have to hack it here to
make it run on travis.
"""

from .data import DownloadModel, DownloadImage
from luigi.contrib.external_program import ExternalProgramTask
from luigi import Parameter, format
import os


class Stylize(ExternalProgramTask):
    model = Parameter()
    image = Parameter()
    LOCAL_ROOT = os.path.abspath('data')
    MODEL_RELATIVE_PATH = 'saved_models'
    IMAGE_RELATIVE_PATH = 'images'

    def program_args(self):
        """

        :return: the command to execute neural_style
        """
        model_file = '{}/{}/{}'.format(self.LOCAL_ROOT, self.MODEL_RELATIVE_PATH, self.model)
        image_file = '{}/{}/{}'.format(self.LOCAL_ROOT, self.IMAGE_RELATIVE_PATH, self.image)
        command = """python -m neural_style eval --content-image {} --model {} --output-image {} --cuda 0""".format(
            image_file, model_file, self.temp_output_path)

        return command.split(" ")

    def output(self):
        """

        :return: output image
        """
        self.out_image_file = '{}/{}/out_{}'.format(self.LOCAL_ROOT, self.IMAGE_RELATIVE_PATH, self.image)
        return SuffixPreservingLocalTarget(self.out_image_file, format=format.Nop)

    def run(self):
        """

        :return: output image which is written atomically
        """
        # You must set up an atomic write!
        # (use self.output().path if you can't get that working)
        with self.output().temporary_path() as self.temp_output_path:
            super().run()

    def requires(self):
        """
        requires both image and model to be downloaded
        :return: list
        """
        return [DownloadModel(self.model), DownloadImage(self.image)]
