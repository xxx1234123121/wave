case node[:platform]
when "debian", "ubuntu"
  package "libatlas-amd64sse3-dev"
  package "libfftw3-dev"
  package "libsuitesparse-dev"
  package "libhdf5-serial-dev"
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
  package "hdf5"
end
