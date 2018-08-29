NAME=schdl-spec
DEPENDS=

.PHONY: all
all: $(NAME).pdf $(NAME).html

$(NAME).html: $(NAME).rst $(DEPENDS)
	rst2html --math-output "MathJax https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js" $< > $@

$(NAME).pdf: $(NAME).tex
	while xelatex $< | grep 'Rerun' >/dev/null; do :; done

$(NAME).tex: $(NAME).rst $(DEPENDS)
	rst2xetex --documentoptions="letterpaper,10pt" $< > $@

.PHONY: clean
clean:
	rm -f $(NAME).pdf $(NAME).html $(NAME).tex $(NAME).aux $(NAME).out \
	      $(NAME).log
