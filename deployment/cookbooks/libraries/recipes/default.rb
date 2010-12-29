case node[:platform]
when "debian", "ubuntu"
  package "libatlas-amd64sse3-dev"
  package "libfftw3-dev"
  package "libsuitesparse-dev"
  package "libhdf5-serial-dev"
  package "libproj-dev"
  package "libgdal1-dev"
  package "proj-bin"
  package "gdal-bin"
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
  package "hdf5"
end
