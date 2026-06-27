---
layout: post
title: Group pictures
excerpt_separator: <!--more-->

---

Pictures by Paolo Soletta

The 360 degree image can be seen with the FSP viewer (download [here](https://www.fsoft.it/FSPViewer/download/))

{% assign group_images = site.static_files | where_exp: "file", "file.path contains '/img/group_picture'" %}

{% for image in group_images %}
![{{ image.basename }}]({{ image.path | relative_url }}){: width="100%" }
{% endfor %}

