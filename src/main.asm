                .p816
                .smart
                .linecont +

                .include "macros.inc"
                .include "registers.inc"

                .include "header.asm"

                ; Asset inclusion (labels exported by preprocessor)
                .include "generated/palette.asm"
                .include "generated/tiles.asm"

                VRAM_CHARS = $0000
                VRAM_BG1   = $1000

                .segment "CODE"

                start:
                    .include "init.asm"

	                lda #>VRAM_BG1
	                sta BG1SC
	                lda #VRAM_CHARS
	                sta BG12NBA

                    lda #$80
                    sta VMAIN
                    ldx #VRAM_CHARS
                    stx VMADDL
                    ldx #0
                    @charset_loop:
                    lda f:CHARACTER_TILES, x
                    sta VMDATAL
                    inx
                    lda f:CHARACTER_TILES, x
                    sta VMDATAH
                    inx
                    cpx #(CHARACTER_TILES_END - CHARACTER_TILES)
                    bne @charset_loop

	                TILE_X = 1
	                TILE_Y = 1
	                ldx #(VRAM_BG1 + (TILE_Y * 32) + TILE_X)
	                stx VMADDL
	                lda #$01 ; tile number
	                sta VMDATAL
	                stz VMDATAH

                    loadPalette CHARACTER_PALETTE_0
                    setAXY16

                    stz BGMODE

                    ldx #0
                    ; Show BG1
                    lda #$0001
                    sta TM

                    lda #$0f
                    sta INIDISP

                busywait:
                    bra busywait

                nmi:
                    bit RDNMI

                _rti:
                    rti

