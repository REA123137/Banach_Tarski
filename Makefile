# Two Balls — the Banach-Tarski paradox, animated.

QUALITY ?= -qh          # -ql preview · -qm · -qh 1080p60 · -qk 4K
SCENE   ?=

.PHONY: all preview scene list check clean deps

all:                      ## render every scene at $(QUALITY)
	./render.sh $(QUALITY)

preview:                  ## render every scene fast, for checking timing
	./render.sh -ql

scene:                    ## render one scene: make scene SCENE=S12Circle
	./render.sh $(QUALITY) $(SCENE)

list:                     ## list every renderable scene
	@grep -Hn '^class \w*(Scene)' banach_tarski/scenes/*.py \
	  | sed 's/:class /  ·  /; s/(Scene)://'

check:                    ## the mathematics the film asserts on screen
	@python3 -m banach_tarski.selfcheck

deps:                     ## system libraries manim needs, on Debian/Ubuntu
	sudo apt-get install -y libcairo2-dev libpango1.0-dev pkg-config ffmpeg
	pip install -r requirements.txt

clean:
	rm -rf media
