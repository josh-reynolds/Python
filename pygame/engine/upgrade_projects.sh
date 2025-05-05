#!/run/current-system/sw/bin/bash

# propagate current engine version to all projects and report version
# note the #! - this was written and expected to run on a NixOS system
# adjust as necessary

directories="brikz bugz cave futbol huevos invader pawng rabbit_run racer thud"

for i in $directories
do
	echo $i
	cp ./engine.py "../$i/"
	grep "__version__" "../$i/engine.py"
done
