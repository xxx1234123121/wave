case node[:platform]
when "debian", "ubuntu"
  package "gfortran"
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
  package "gfortran"
end
