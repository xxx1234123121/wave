createlang plpgsql wave
psql -U wave -d wave -f /usr/local/share/postgis/postgis.sql
psql -U wave -d wave -f /usr/local/share/postgis/spatial_ref_sys.sql
psql -U wave -d wave -f db/design/DB.psql
