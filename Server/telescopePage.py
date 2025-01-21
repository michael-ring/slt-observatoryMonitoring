#!/usr/bin/env python3

import sys
import traceback
from yattag import Doc
from pathlib import Path

try:
  from Common.config import rootserver,logger,runningOnServer
except Exception as e:
  print(e)
  raise(e)

import powerBoxStatus
import skyAlertStatus
import roofStatus
import imageStatus
import schedulerStatus
import allSkyStatus

def handle_exception(exc_type, exc_value, exc_traceback):
  if issubclass(exc_type, KeyboardInterrupt):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    return
  logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


doc, tag, text = Doc().tagtext()
doc.asis("""
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="HandheldFriendly" content="True" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="" />
  <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,400;0,700;1,400&family=Source+Sans+Pro:ital,wght@0,300;0,400;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="https://slt-observatory.space/theme/stylesheet/style.min.css">
  <link id="pygments-light-theme" rel="stylesheet" type="text/css" href="https://slt-observatory.space/theme/pygments/github.min.css">
  <link rel="stylesheet" type="text/css" href="https://slt-observatory.space/theme/font-awesome/css/fontawesome.css">
  <link rel="stylesheet" type="text/css" href="https://slt-observatory.space/theme/font-awesome/css/brands.css">
  <link rel="stylesheet" type="text/css" href="https://slt-observatory.space/theme/font-awesome/css/solid.css">
  <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
  <link rel="icon" href="favicon.ico" type="image/x-icon">
  <meta name="author" content="Michael Ring" />
  <meta name="description" content="" />
  <meta property="og:site_name" content="Sufficiently Large Telescope Observatory"/>
  <meta property="og:type" content="blog"/>
  <meta property="og:title" content="Sufficiently Large Telescope Observatory"/>
  <meta property="og:description" content=""/>
  <meta property="og:locale" content="en_US"/>
  <meta property="og:url" content="https://slt-observatory.space"/>
  <title>Sufficiently Large Telescope Observatory &ndash; Status CDK14</title>
  <link type="text/css" rel="stylesheet" href="css/lightgallery.css" />
</head>
""")

doc.asis("""
<style>
 main article {
    max-width:1024px
  } 
</style>
<script src="https://code.jquery.com/jquery-3.7.1.slim.js"></script>
<body class="light-theme">
<script src="js/lightgallery.min.js"></script>
<aside>
  <div>
    <a href="https://slt-observatory.space/"><img src="https://slt-observatory.space/theme/img/profile.png" alt="" title="">
    </a>
    <h1>
      <a href="https://slt-observatory.space/"></a>
    </h1>
    <p>Home of the SLT Team</p>
    <nav>
      <ul class="list">
            <li>
              <a target="_self"
                 href="https://slt-observatory.space/pages/worum-geht-es.html#worum-geht-es">
                Worum geht es?
              </a>
            </li>
      </ul>
    </nav>
  </div>
</aside>
<main>
<article class="single">
  <header>
    
    <h1 id="status-vst">Status VST</h1>
  </header>
  <div>
<h2>Clear Sky Chart</h2>
<p style="width:1000px;">
<a href=https://www.cleardarksky.com/c/StrfrntObsTXkey.html>
<img src="https://www.cleardarksky.com/c/StrfrntObsTXcsk.gif?c=2012437"></a>
</p>
<h2>Liveview</h2>
<p style="width:1000px;">
<table>
  <thead>
    <tr>
      <th width="33%">Last Image</th>
      <th width="33%">Pier Camera</th>
      <th width="33%">Building Camera</th>
    </tr>
  </thead>
  <tbody>
    <tr id="tr-td">
      <td data-src="https://slt-observatory.space/images/vst-images/subimage.jpg">
        <img src="https://slt-observatory.space/images/vst-images/subimage.jpg"/>
      </td>
      <td data-src="https://slt-observatory.space/images/vst-images/image.jpg">
        <img src="https://slt-observatory.space/images/vst-images/image.jpg"/>
      </td>
      <td data-src="https://zyssufjepmbhqznfuwcw.supabase.co/storage/v1/object/public/status-assets-public/building-0005/allsky/images/image.jpg">
        <img src="https://zyssufjepmbhqznfuwcw.supabase.co/storage/v1/object/public/status-assets-public/building-0005/allsky/images/image.jpg"/>
      </td>
    </tr>
  </tbody>
</table>
<table>
  <thead>
    <tr>
      <th width="33%">NOAA CloudCoverage</th>
      <th width="33%">NOAA Radar</th>
      <th width="33%"></th>
    <tr>
  </thead>
  <tbody>
    <tr id="tr-td2">
      <td data-src="https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/sp/GEOCOLOR/GOES16-SP-GEOCOLOR-600x600.gif">
        <img src="https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/sp/GEOCOLOR/GOES16-SP-GEOCOLOR-600x600.gif"/>
      </td>
      <td data-src="https://radar.weather.gov/ridge/standard/KSJT_loop.gif">
        <img src="https://radar.weather.gov/ridge/standard/KSJT_loop.gif"/>
      </td>
      <td>
      </td>
    </tr>
  </tbody>
</table>
</p>
<!-- begin include status-vst.include -->
<!-- unprocessed version -->
<!-- end include status-vst.include -->

</div>
""")
if not runningOnServer():
  try:
    doc.asis(roofStatus.genDiv('slt'))
  except Exception as e:
    logger.exception(e)
    print(e)
    pass
  try:
    doc.asis(powerBoxStatus.genDiv('slt'))
  except Exception as e:
    logger.exception(e)
    traceback.format_exc()
    pass
  try:
    doc.asis(skyAlertStatus.genDiv('slt'))
  except Exception as e:
    logger.exception(e)
    traceback.format_exc()
    pass
  try:
    allSkyStatus.renderVideo('slt')
  except Exception as e:
    logger.exception(e)
    traceback.format_exc()
  try:
    doc.asis(schedulerStatus.genDiv('slt'))
  except Exception as e:
    logger.exception(e)
    traceback.format_exc()
  try:
    doc.asis(imageStatus.genDiv('slt'))
  except Exception as e:
    logger.exception(e)
    traceback.format_exc()

#doc.asis(roofStatus.genDiv('vst'))
#doc.asis(powerBoxStatus.genDiv('vst'))
#doc.asis(skyAlertStatus.genDiv('vst'))
#doc.asis(schedulerStatus.genDiv('vst'))
#doc.asis(imageStatus.genDiv('vst'))

if runningOnServer():
  doc.asis(roofStatus.genDiv('vst'))
  doc.asis(powerBoxStatus.genDiv('vst'))
  doc.asis(skyAlertStatus.genDiv('vst'))
  doc.asis(schedulerStatus.genDiv('vst'))
  doc.asis(imageStatus.genDiv('vst'))

  doc.asis(roofStatus.genDiv('slt'))
  doc.asis(powerBoxStatus.genDiv('slt'))
  doc.asis(skyAlertStatus.genDiv('slt'))
  doc.asis(schedulerStatus.genDiv('slt'))
  doc.asis(imageStatus.genDiv('slt'))

  doc.asis(roofStatus.genDiv('cdk14'))
  doc.asis(schedulerStatus.genDiv('cdk14'))
  doc.asis(imageStatus.genDiv('cdk14'))

doc.asis("""
<script>
  lightGallery(document.getElementById('tr-td'));
  lightGallery(document.getElementById('tr-td2'));
  lightGallery(document.getElementById('selector'), {selector: '.sub',});
  lightGallery(document.getElementById('selector'), {selector: '.allsky',});
</script>
</article>

<footer>
<p>&copy;</p>
<p>Built with <a href="https://getpelican.com" target="_blank">Pelican</a> using <a href="https://bit.ly/flex-pelican" target="_blank">Flex</a> theme
</p>
</footer>  
</main>
</body>
</html>
""")
if runningOnServer() == False:
  index = Path(Path(__file__).parent.parent / f'Test/status.html')
  index.write_text(doc.getvalue())
