from scipy.io import savemat

from .JSON import clobber

def writeMatFile( data, varName, fileName ):
  data = clobber( data )
  savemat( fileName, {varName: data}, appendmat = True )

  return None
