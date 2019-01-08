# encoding: utf-8
import os
import io
import errno
import glob
import configparser
import logging
from PyPDF2 import PdfFileReader, PdfFileWriter

class MergePDF:

  def __init__(self):
    self.cfilename = "config.ini"
    self.config = configparser.ConfigParser()
    self.load_config()
    self.create_logger()
    self.config_log()

  def create_logger(self):
    self.logger = logging.getLogger('MergePDF')
    self.logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    handler = logging.FileHandler('merge.log', encoding = "UTF-8")
    handler.setLevel(logging.INFO)
    if self.isDebug():
      handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # add the handlers to the logger
    self.logger.addHandler(handler)
    self.logger.addHandler(ch)

  def create_config(self):
    cfgfile = open(self.cfilename,'w')
    try:        
      self.config.add_section('MERGE')
      self.config.set('MERGE', 'outputfile', '')
      self.config.set('MERGE', 'debug', 'False')      
      self.config.write(cfgfile)
    finally:
      cfgfile.close()
    
  def load_config(self):        
    if not os.path.isfile(self.cfilename):
      self.create_config()
    
    if not os.path.isfile(self.cfilename):
      raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.cfilename)

    self.config.read(self.cfilename, encoding='utf-8')    
    self.debug = self.config["MERGE"].getboolean("debug", False)
    self.outputfile = str(self.config["MERGE"]["outputfile"])    
    self.outputfile = self.get_output_filename()

  def get_output_filename(self):
    if self.outputfile:
      return self.outputfile
        
    return "merged.pdf"
    
  def config_log(self):
    if not self.isDebug():
      return

    self.logger.setLevel(logging.DEBUG)
    for key in self.config["MERGE"]:
      self.logger.debug("Config %s: %s", key, self.config["MERGE"][key])
    
    self.logger.debug("Config outputfile: %s", self.outputfile)

  def isDebug(self):
    return self.debug

  def merge_pdf_files(self):
    self.logger.info("Iniciando merge do PDF.")
    paths = glob.glob("*.pdf")
    pdf_writer = PdfFileWriter()

    for path in paths:
      self.logger.debug("Incluíndo arquivo %s .", path)
      pdf_reader = PdfFileReader(path, strict=False)
      for page in range(pdf_reader.getNumPages()):
          pdf_writer.addPage(pdf_reader.getPage(page))

    with open(self.outputfile, 'wb') as fh:
      pdf_writer.write(fh)

    self.logger.info("Finalizando merge do PDF.")
 
  def limpar_ambiente(self):
    self.logger.info('Removendo arquivo PDF ordenado.')
    if os.path.isfile(self.outputfile):
      os.remove(self.outputfile)

  def run(self):
    self.limpar_ambiente()
    self.merge_pdf_files()

if __name__ == '__main__':
    exp = MergePDF()
    exp.run()
