cookbook_path     File.join(File.expand_path(File.dirname(__FILE__)), "cookbooks/")
json_attribs      File.join(File.expand_path(File.dirname(__FILE__)), "deploy-config.json")
log_level         :info
Chef::Log::Formatter.show_time = true
