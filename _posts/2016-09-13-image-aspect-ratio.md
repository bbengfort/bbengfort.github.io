---
layout: post
title:  "Modifying an Image's Aspect Ratio"
date:   2016-09-13 14:19:14 -0400
categories: snippets
---

When making slides, I generally like to use [Flickr](https://www.flickr.com/) to search for images that are licensed via [Creative Commons](https://creativecommons.org/) to use as backgrounds. My slide deck tools of choice are either [Reveal.js](http://lab.hakim.se/reveal-js/#/) or [Google Slides](https://www.google.com/slides/about/). Both tools allow you to specify an image as a background for the slide, but for Google Slides in particular, if the aspect ratio of the image doesn't match the aspect ratio of the slide deck, then weird things can happen.

For a long time, I'd been manually cropping images in Preview. I would decide which was the long dimension based on the aspect ratio I was using (e.g. 16x9) and trim the image along that dimension to the desired ratio. I could then upload to the background with no weird scaling or centering occurring. Making my slides for PyData, however, I realized this was inefficient - and anyway I was running out of time! Therefore I decided to use the [Python Image Library (PIL)](http://www.pythonware.com/products/pil/) to do this automatically for me on the command line:

<script src="https://gist.github.com/bbengfort/d49ea52d7b73897785dd619685be310b.js"></script>

This script allows you to pass an aspect ratio as a `WxH` string, where W is the width integer and H is the height integer. The default is 16x9 as per my slides at the time. It then opens the Image using PIL, computes the image width and height, then determines the width and height difference from the ratio. If the difference is bigger, that amount is cropped off _evenly_ from both sides. The new image is then saved as a copy so the original isn't destroyed.

Here is an example image of [Shanghai city](https://flic.kr/p/bmM7Xv) by [barnyz](https://www.flickr.com/photos/75487768@N04/), used under a [CC BY-NC-ND 2.0](https://creativecommons.org/licenses/by-nc-nd/2.0/) creative commons license:

![Original image before cropping]({{ site.base_url }}/assets/images/2016-09-13-city-image-original.jpg)

In order to crop this image to the 16x9 aspect ratio we run the script as follows:

```
$ python img2aspect.py -a 16x9 city.jpg
```

This saves a file called `city-16x9.jpg` in the same directory as `city.jpg`. As you can see the resulting image is cropped evenly from the top and the bottom to bring the height dimension into alignment with the aspect:

![Image cropped using the tool]({{ site.base_url }}/assets/images/2016-09-13-city-image-aspect-16x9.jpg)

Note that this result is because an analysis of the dimensions of the original with respect to the aspect ratio showed that the height was out of alignment with the desired aspect ratio, not the width. If we had passed in a very long picture, then the width would have been cropped.
