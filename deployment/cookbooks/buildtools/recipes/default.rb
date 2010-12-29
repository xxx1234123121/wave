case node[:platform]
when "debian", "ubuntu"
  package "build-essential"
  package "gfortran"
  package "cmake"
  package "stow"
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
  package "gfortran"
  package "cmake"
end
