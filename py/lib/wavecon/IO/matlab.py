from scipy.io import savemat

from .JSON import clobber

def writeMatFile(data, fileName):
  data = clobber(data)
  savemat(fileName, data, appendmat = True)

  return None
