--- 
title: Functional Tests 
post_excerpt: A short summary to follow. 
---

The UCUM functional test corpus is maintained in the [FHIR/Ucum-java repository](https://github.com/FHIR/Ucum-java). You can [view the XML test file](https://github.com/FHIR/Ucum-java/blob/master/src/test/resources/UcumFunctionalTests.xml) or [download it directly](https://raw.githubusercontent.com/FHIR/Ucum-java/master/src/test/resources/UcumFunctionalTests.xml).

Contributions and corrections to the test corpus are welcome through [GitHub issues](https://github.com/FHIR/Ucum-java/issues) or pull requests in that repository. Corrections to this documentation can be submitted to [ucum-org/ucum](https://github.com/ucum-org/ucum).

## Conformance

You may declare conformance to these UCUM functional tests if your implementation accepts the linked XML file as an input, and passes all the test cases it contains. You should always quote the most recent date from the test corpus's history when claiming conformance. You may qualify the conformance to particular kinds of cases if your functionality does not cover all the tests. Note that conformance to these tests does not equate to conformance to UCUM itself - though one could reasonably claim to be compliant with UCUM if one is conformant to these tests.

This file is copyright © 2008 - 2009 Grahame Grieve and other contributors:

  - Gunther Schadow
  - Lloyd Mackenzie

## License

This source is licensed for public use under the [Eclipse Public License](http://www.eclipse.org/legal/epl-v10.html).

## History

  - 18-Aug 2014: update current source - it is not valid
  - 18-June 2014: Fixes for various issues, including trac \#159
  - 31-May 2010: updated with fixes to a couple of original conversion tests (Thanks to Christof Gessner). Extended the conversion tests considerably - should be easier to track down conversion issues
  - 10-Feb 2009: First Version. Ucum validation Tests, display name generation tests, conversion tests, and initial multiplication test
