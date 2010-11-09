case node[:platform]
when 'debian', 'ubuntu'
  package 'python2.7'
  package 'python2.7-dev'
  package 'python-setuptools'
else
  puts <<-EOS.undent
    Warning: Python deployment is not tested outside of Debian-based systems!
      In particular, the installation of the pip python package manager may fail!
  EOS
  package 'python'
end
