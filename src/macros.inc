
				.macro setA8
					sep #$20
				.endmacro

				.macro setA16
					rep #$20
				.endmacro

				.macro setAXY8
					sep #$30
				.endmacro

				.macro setAXY16
					rep #$30
				.endmacro

				.macro setXY8
					sep #$10
				.endmacro

				.macro setXY16
					rep #$10
				.endmacro

				.macro letColor red, green, blue
					.if (.paramcount <> 3)
					.error  "Too few parameters for letColor"
					.endif
					.local color
					color = (((blue) << 10) | ((green) << 5) | (red))
					lda #.lobyte(color)
					sta CGDATA
					lda #.hibyte(color)
					sta CGDATA
				.endmacro

                ; exits with AXY in 16 bit mode
                .macro loadPalette pallette
                    stz CGADD
                    setAXY8
                    .repeat 8, i
                        lda f:pallette+i
                        sta CGDATA
                    .endrepeat
                    setAXY16
                .endmacro