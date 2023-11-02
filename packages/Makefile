# Rules and targets in Makefile1

up-all:
	@echo "Uping API, Vector and Discord"
	# To execute the default target from Makefile2 in another folder, use $(MAKE) -C path/to/directory
	$(MAKE) -f vector_server/Makefile up
	@echo "Uping ML"
	$(MAKE) -f ml/Makefile up
	@echo "Uping Discord"
	$(MAKE) -f discord/Makefile up
	@echo "Uping Complete"

down-all:
	@echo "Downing API, Vector and Discord"
	# To execute the default target from Makefile2 in another folder, use $(MAKE) -C path/to/directory
	$(MAKE) -f discord/Makefile down
	@echo "Downing ML"
	$(MAKE) -f ml/Makefile down
	@echo "Downing Vector"
	$(MAKE) -f vector_server/Makefile down
	@echo "Downing Complete"


restart-all:
	@echo "Restarting API, Vector and Discord"
	$(MAKE) -f vector_server/Makefile restart
	@echo "Restarting ML"
	$(MAKE) -f ml/Makefile restart
	@echo "Restarting Discord"
	$(MAKE) -f discord/Makefile restart
	@echo "Restarting Complete"

build-all:
	@echo "Building API, Vector and Discord"
	$(MAKE) -f vector_server/Makefile build
	@echo "Building ML"
	$(MAKE) -f ml/Makefile build
	@echo "Building Discord"
	$(MAKE) -f discord/Makefile build
	@echo "Building Complete"

.PHONY: up-all down-all build-all