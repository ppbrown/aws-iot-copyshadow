
NAME=com.bolthole.iotcopyshadow
VERSION=1.0.1

SRCS=iotcopyshadow.py


recipedir/recipe.yaml:	Makefile recipe-tmpl.yaml
	rm -rf recipedir
	mkdir recipedir
	sed -e 's/NAME/'$(NAME)'/' \
	-e 's/VERSION/'$(VERSION)'/' \
	 recipe-tmpl.yaml >recipedir/recipe.yaml

localstage:	$(SRCS)
	rm -rf artifactdir
	mkdir artifactdir
	mkdir -p artifactdir/$(NAME)/$(VERSION)
	cp $(SRCS) artifactdir/$(NAME)/$(VERSION)

localdeploy:	recipedir/recipe.yaml localstage
	sudo /greengrass/v2/bin/greengrass-cli deployment create \
	  --recipeDir recipedir --artifactDir artifactdir \
	--merge $(NAME)=$(VERSION)

restart:	
	sudo /greengrass/v2/bin/greengrass-cli component restart \
	--names=$(NAME)

clean:
	rm -rf recipedir artifactdir

remove:
	sudo /greengrass/v2/bin/greengrass-cli deployment create \
	  --remove=$(NAME)

tailmain:
	sudo tail -f /greengrass/v2/logs/greengrass.log
