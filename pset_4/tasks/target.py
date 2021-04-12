from luigi.local_target import LocalTarget, atomic_file
import os
import random
import string
from contextlib import contextmanager

"""
I wrote this file in csci_utils package, and got it running locally.
However I couldn't get it run on travis. So I have to hack it here to
make it run on travis.
"""
class suffix_preserving_atomic_file(atomic_file):
    def generate_tmp_path(self, path):
        """

        :param path: path of the original file
        :return: temp file that preservse suffix
        """
        f_splitted = os.path.split(path)
        dirname = f_splitted[0]

        # create a tmp file with random characters
        randstr_len = 10
        while True:
            randstr = "".join(
                random.choice(string.ascii_uppercase) for _ in range(randstr_len)
            )
            tmp_filename = os.path.join(
                dirname, "{}.{}".format(randstr, f_splitted[1])
            )
            if not os.path.exists(tmp_filename):
                break
        return tmp_filename

class BaseAtomicProviderLocalTarget(LocalTarget):
    # Allow some composability of atomic handling
    atomic_provider = atomic_file

    def open(self, mode='r'):
        """

        :param mode:
        :return: similar to super, except for using atomic_provider
        """
        # leverage super() as well as modifying any code in LocalTarget
        # to use self.atomic_provider rather than atomic_file
        rwmode = mode.replace('b', '').replace('t', '')
        if rwmode == 'w':
            self.makedirs()
            return self.format.pipe_writer(self.atomic_provider(self.path))

        elif rwmode == 'r':
            fileobj = FileWrapper(io.BufferedReader(io.FileIO(self.path, mode)))
            return self.format.pipe_reader(fileobj)

        else:
            raise Exception("mode must be 'r' or 'w' (got: %s)" % mode)

    @contextmanager
    def temporary_path(self):
        # NB: unclear why LocalTarget doesn't use atomic_file in its implementation
        self.makedirs()
        with self.atomic_provider(self.path) as af:
            yield af.tmp_path


class SuffixPreservingLocalTarget(BaseAtomicProviderLocalTarget):
    atomic_provider = suffix_preserving_atomic_file
