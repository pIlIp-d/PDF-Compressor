import os
import subprocess

from Compressor import *
from Project.Compressor.CompressException import CompressException


class CPdfSqueezeCompressor(Compressor):

    def __init__(self, origin_path, dest_path, cpdfsqueeze_path):
        super().__init__(origin_path, dest_path)
        self.cpdfsqueeze_path = cpdfsqueeze_path

    def compress(self):
        command = ""
        # execute .exe with wine when not on Windows
        if not "nt" == os.name:
            command += "wine"
        # run program at path
        command += self.cpdfsqueeze_path
        # to compress file from origin_path to dest_path (given as parameters)
        command += '"'+self.origin_path+'" "'+self.dest_path+'"'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except Exception:
            raise CompressException("CPdfSqueezeCompressor")
