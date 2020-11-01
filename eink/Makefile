.PHONY: eink

default: eink

eink:
	watch -n 300 "scp draw-eink.py raspberrypi:eink.perrygeo.com/ && ssh raspberrypi 'cd eink.perrygeo.com && ./draw-eink.py'"
