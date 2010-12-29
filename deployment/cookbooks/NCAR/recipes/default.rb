log "Installing NCAR NCL and PyNIO"

case node[:platform]
when "ubuntu"
  # NCL is a large monolithic package that deals with graphics production and
  # data access.  PyNIO is the python library that interfaces to the NCL data
  # access routines.  Nice software, but terrible distribution system.
  # Terrible build system.  Using pre-compiled binaries and manual installation
  # here---but a better solution is needed.  Perhaps packaging these into a
  # *.deb package? 
  unless File.directory?('/opt/ncl')
    remote_file "/tmp/ncl.tar.gz" do
      source "http://dl.dropbox.com/u/72178/dist/ncl_ncarg-5.2.1.Linux_Debian_x86_64_gcc412.tar.gz"
    end

    execute "mkdir -p /opt/ncl"
    execute "tar xzf /tmp/ncl.tar.gz -C /opt/ncl"
    execute "stow -d /opt -t /usr/local ncl"
  end

  unless File.directory?('/opt/PyNIO')
    remote_file "/tmp/pynio.tar.gz" do
      source "http://dl.dropbox.com/u/72178/dist/PyNIO-Debian-Patched-1.4.0.tar.gz"
    end

    execute "mkdir -p /opt"
    execute "tar xzf /tmp/pynio.tar.gz -C /opt"
    execute "ln -sf /opt/PyNIO /usr/local/lib/python2.7/dist-packages/PyNIO"
  end
else
  puts "Warning: The waveconnect deployment is only battle tested on Ubuntu!"
end
