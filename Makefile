XSLTPROC=java -jar build/saxon8.jar
PYTHON?=python3
SAXON=build/saxon8.jar
SPEC_STYLES=build/v3dt-v3pub.xsl build/xml-verbatim.xsl build/v3dt-schema.xsl build/v3pub-locations.ent
HTML_STYLES=build/V3mLayoutHTML20.xsl build/v3m00.ent build/largegraphics.xml

.PHONY: all check clean

all: ucum.html ucum-cs.units ucum-ci.units ucum-essence.xml

ucum.html: ucum.xml $(HTML_STYLES) $(SAXON)
	$(XSLTPROC) -o $@ ucum.xml build/V3mLayoutHTML20.xsl

ucum.xml: ucum-source.xml $(SPEC_STYLES) $(SAXON)
	$(XSLTPROC) -o $@ ucum-source.xml build/v3dt-v3pub.xsl

ucum-essence.xml: ucum-source.xml build/ucum-winnow.xsl $(SAXON)
	$(XSLTPROC) -o $@ ucum-source.xml build/ucum-winnow.xsl

ucum-cs.units: ucum-source.xml build/ucum-oldfile.xsl $(SAXON)
	$(XSLTPROC) -o $@ ucum-source.xml build/ucum-oldfile.xsl case="sensitive"

ucum-ci.units: ucum-source.xml build/ucum-oldfile.xsl $(SAXON)
	$(XSLTPROC) -o $@ ucum-source.xml build/ucum-oldfile.xsl case="insensitive"

check:
	$(PYTHON) -B -m unittest discover -s tests

clean:
	rm -f *~ ucum.xml ucum-cs.units ucum-ci.units ucum.html ucum-essence.xml

