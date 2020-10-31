# BookletParser

 _Parses singlefold booklets into reading order._
 
 This utility is for parsing scans of two-page booklets. That is, booklets made of standard 8.5 x 11 sheets, folded in half and stapled along the spine. Each booklet page is then 5.5" wide by 8.5" tall.
 
 The easy way to archive such a booklet is to remove the staples and feed the stack of sheets through a scanner. However, viewing the result on-screen is awkward. The pages that were adjacent in the booklet are now far distant in the scan, and vise versa. Not to mention, the sheets are sideways.
 
 This utility solves all that by taking the multi-page TIF scan, and creating a copy with the pages divided out, rotated, and arranged in correct reading order.
 
 
 _Usage notes as of 2020-11-01_
 
 Requires wxPython ("wx"), but wx will not install under the latest language version, Python 3.9.0
 
 Install Python 3.8.6, then install wx making sure it "goes with" that version, not any other Python version you may have. The wx install also correctly sets up PIL, another requirement.
 
 Like everything in computers, "it's easy, once you know". We hope this glitch will be fixed in the future.
