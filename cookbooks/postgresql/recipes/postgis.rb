case node.platform
when "ubuntu","debian"
  package "postgresql-#{node[:postgresql][:version]}-postgis"
else
  puts "Not implemented yet!"
end
