case node[:platform]
when "debian", "ubuntu"
  package "build-essential"
  package "gfortran"
  package "cmake"
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
  package "gfortran"
  package "cmake"
end
