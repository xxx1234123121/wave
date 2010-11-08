case node[:platform]
when 'debian', 'ubuntu'
  package 'gfortran-4.5'
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
  package 'gfortran'
end
