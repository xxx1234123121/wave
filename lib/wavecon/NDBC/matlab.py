from scipy.io import savemat

from .JSON import clobber

def writeMatFile( NDBCdata, varName, fileName ):
  NDBCdata = clobber( NDBCdata )
  savemat( fileName, {varName: NDBCdata}, appendmat = True )

  return None
