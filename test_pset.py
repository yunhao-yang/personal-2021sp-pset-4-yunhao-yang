#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pset_4` package."""
from unittest import TestCase
import pset_4.tasks.data as data
import pset_4.tasks.stylize as stylize
import pset_4.tasks.target as target
from luigi.contrib.s3 import S3Target
import os


class DataTests(TestCase):
    def test_downloader(self):
        """
        Tests for download super class
        """
        x = data.Downloader()
        try:
            x.requires()
        except NotImplementedError:
            assert True
        try:
            x.output()
        except NotImplementedError:
            assert True

    def test_downloadmodel(self):
        """
        Test for download model
        """
        x = data.DownloadModel(model="candy.pth")
        assert type(x.requires()) == data.SavedModel
        assert type(x.output()) == target.SuffixPreservingLocalTarget
        x.run()
        out_file = os.path.join(x.LOCAL_ROOT, x.SHARED_RELATIVE_PATH, x.model)
        assert os.path.exists(out_file)

    def test_downloadimage(self):
        """
        Test for download model
        """
        x = data.DownloadImage(image="luigi.jpg")
        assert type(x.requires()) == data.ContentImage
        assert type(x.output()) == target.SuffixPreservingLocalTarget
        x.run()
        out_file = os.path.join(x.LOCAL_ROOT, x.SHARED_RELATIVE_PATH, x.image)
        assert os.path.exists(out_file)

    def test_external(self):
        """
        Test for external
        """
        x1 = data.ContentImage(image='luigi.jpg')
        x2 = data.SavedModel(model='candy.pth')
        assert type(x1.output()) == S3Target
        assert type(x2.output()) == S3Target

    def test_stylize(self):
        """
        Test for stylize
        """
        s = stylize.Stylize(image='luigi.jpg', model='candy.pth')
        r = s.requires()
        assert type(r) == list
        assert type(r[0]) == data.DownloadModel
        assert type(r[1]) == data.DownloadImage

        s.run()
        assert os.path.exists(s.out_image_file)

        p = s.program_args()
        assert type(p) == list
        assert p[0] == 'python'