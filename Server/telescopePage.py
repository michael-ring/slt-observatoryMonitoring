#!/usr/bin/env python3

from yattag import Doc
from pathlib import Path

import powerBoxStatus
import skyAlertStatus
import roofStatus

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
    <h1 id="status-cdk14">Status Testing</h1>
  </header>
  <div>
<h2>Clear Sky Chart</h2>
<p>
<a href=https://www.cleardarksky.com/c/StrfrntObsTXkey.html>
<img src="https://www.cleardarksky.com/c/StrfrntObsTXcsk.gif?c=2361648"></a>
</p>
  <table>
    <tr>
      <th>Last Image</th>
      <th>Pier Camera</th>
      <th>Building Camera</th>
    </tr>
    <tr>
      <td width="33%">
        <a id="selector1" href="https://slt-observatory.space/images/slt-images/subimage.jpg" data-source="https://slt-observatory.space/images/slt-images/subimage.jpg">
          <img alt="Last Image" src="https://slt-observatory.space/images/slt-images/subimage.jpg" />
        </a>
      </td>
      <td width="33%" >
        <a id="selector2" href="https://slt-observatory.space/images/slt-images/image.jpg" data-source="https://slt-observatory.space/images/slt-images/image.jpg">
          <img alt="Pier Camera" src="https://slt-observatory.space/images/slt-images/image.jpg" />
        </a>
      </td>
      <td width="33%" >
        <a id="selector3" href="https://zyssufjepmbhqznfuwcw.supabase.co/storage/v1/object/public/status-assets-public/building-0005/allsky/images/image.jpg">
          <img alt="Building Camera" src="https://zyssufjepmbhqznfuwcw.supabase.co/storage/v1/object/public/status-assets-public/building-0005/allsky/images/image.jpg" />
        </a>
      </td>
    </tr>
  </table>

""")

doc.asis(roofStatus.genDiv('vst'))
doc.asis(powerBoxStatus.genDiv('vst'))
doc.asis(skyAlertStatus.genDiv('vst'))


doc.asis("""
</article>
<script type="text/javascript">
lightGallery(document.getElementById('selector1'), {
    selector: 'this',
    plugins: [],
    licenseKey: '0000-0000-000-0000',
    speed: 500
});
lightGallery(document.getElementById('selector2'), {
    selector: 'this',
    plugins: [],
    licenseKey: '0000-0000-000-0000',
    speed: 500
});
lightGallery(document.getElementById('selector3'), {
    selector: 'this',
    plugins: [],
    licenseKey: '0000-0000-000-0000',
    speed: 500
});
</script>

<footer>
<p>&copy;</p>
<p>Built with <a href="http://getpelican.com" target="_blank">Pelican</a> using <a href="http://bit.ly/flex-pelican" target="_blank">Flex</a> theme
</p>
</footer>  
</main>
</body>
</html>
""")
index = Path(Path(__file__).parent.parent / f'Test/status.html')
index.write_text(doc.getvalue())

