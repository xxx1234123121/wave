Vagrant::Config.run do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "WaveLab"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # config.vm.box_url = "http://dl.dropbox.com/u/72178/dist/ubuntu64.box"

  # Boot with a GUI so you can see the screen. (Default is headless)
  # config.vm.boot_mode = :gui

  # Assign this VM to a host only network IP, allowing you to access it
  # via the IP.
  # config.vm.network "33.33.33.10"

  # Forward a port from the guest to the host, which allows for outside
  # computers to access the VM, whereas host only networking does not.
  # config.vm.forward_port "http", 80, 8080

  config.ssh.host = "localhost"
  config.ssh.max_tries = 5
  config.vm.forward_port "ssh", 22, 2222

  # Share an additional folder to the guest VM. The first argument is
  # an identifier, the second is the path on the guest to mount the
  # folder, and the third is the path on the host to the actual folder.
  # config.vm.share_folder "v-data", "/vagrant_data", "../data")

  # Enable provisioning with chef solo, specifying a cookbooks path (relative
  # to this Vagrantfile), and adding some recipes and/or roles.
  #
  config.vm.provisioner = :chef_solo
  config.chef.cookbooks_path = "cookbooks"
  config.chef.add_recipe("main")

  configFile = File.open(
    File.join(File.expand_path(File.dirname(__FILE__)), 'deploy-config.json'),
    'r'
  )
  config.chef.json.merge!(JSON.load(configFile))
  configFile.close()

  # Enable provisioning with chef server, specifying the chef server URL,
  # and the path to the validation key (relative to this Vagrantfile).
  #
  # config.vm.provisioner = :chef_server
  # config.chef.chef_server_url = "http://api.opscode.com/organizations/organization"
  # config.chef.validation_key_path = "kiip-validator.pem"
  #
  # If you're using the OpsCode platform, you'll have to set this as well.
  # If you're using your own chef server, you may have to set it, but it depends
  # on how your Chef server is configured.
  # config.chef.validation_client_name = "organization-validator"
end
