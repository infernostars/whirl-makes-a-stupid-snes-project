
shopt -s dotglob
rm -rf  build/*
shopt -u dotglob

python  scripts/preprocess.py

ca65 -g src/main.asm -o build/cart.o
ld65 -C src/lorom.cfg -o build/cart.smc build/cart.o --dbgfile build/cart.dbg

