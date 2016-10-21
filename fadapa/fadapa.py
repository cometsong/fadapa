"""
Python module to parse FastQC output data.
"""
from __future__ import print_function

import zipfile
import re


class Fadapa(object):
    """
    Returns a parsed data object for given fastqc data file
    """

    def __init__(self, file_name, **kwargs):
        """
        :arg file_name: Name of fastqc_data text file, or of fastqc zipfile.
        :type file_name: str.
        """

        self._content = []
        self.file_name = file_name
        self._modules = self.modules()
        self.basic_stats = self.basic_stats()
        fq_data_file_name = 'fastqc_data.txt'
        self._m_mark = '>>'
        self._m_end = '>>END_MODULE'
        if  zipfile.is_zipfile(file_name):
            with zipfile.ZipFile(file_name, mode='r') as fqz:
                for file in fqz.namelist():
                    if re.search(fq_data_file_name, file):
                        fq_data_file = file
                self._content = fqz.open(fq_data_file, 'r').read().splitlines()
        else:
            self._content = open(file_name, **kwargs).read().splitlines()

    def summary(self):
        """
        Returns a list of all modules present in the content.
        Module begins  with  _m_mark ends with _m_end.

        :return: List of modules and their status.

        Sample module:

        >>Basic Statistics	pass
        #Measure	Value
        Filename	sample1.fastq
        >>END_MODULE

        """
        modules = [line.split('\t') for line in self._content
                   if self._m_mark in line and self._m_end not in line]
        data = [[i[2:], j] for i, j in modules]
        data.insert(0, ['Module Name', 'Status'])
        return data

    def content(self):
        """
        Print the contents of the given file.

        :return: None
        """
        for line in self._content:
            print(line)

    def raw_data(self, module):
        """
        Returns raw data lines for a given module name.

        :arg module: Name of module as returned by summary function.
        :type module: str.
        :return: List of strings which consists of raw data of module.
        """
        s_pos = next(self._content.index(x) for x in self._content
                     if module in x)
        e_pos = self._content[s_pos:].index(self._m_end)
        raw_data = self._content[s_pos:s_pos+e_pos+1]
        return raw_data

    def clean_data(self, module):
        """
        Returns a cleaned data for the given module.

        :arg module: name of module
        :type module: str
        :return List of strings containing the clean data of module.
        """
        data = [list(filter(None, x.split('\t')))
                for x in self.raw_data(module)[1:-1]]
        data[0][0] = data[0][0][1:]
        return data

    def basic_stats(self):
        """return dict of items in basic Statistics"""
        return {stat: value for stat, value in
                self.clean_data('Basic Statistics')[1:]
               }

    def modules(self):
        """parse module names from super.summary()"""
        module_names = [module[0] for module in self.summary()[1:]]
        return module_names

