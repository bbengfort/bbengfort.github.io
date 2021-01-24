---
categories: observations
date: "2017-07-06T08:15:13Z"
title: On the Tracks with Rails
---

[![Kahu Screenshot](/images/2017-07-06-kahu-screenshot.png)](/images/2017-07-06-kahu-screenshot.png)

I'm preparing to move into a new job when I finish my dissertation hopefully later this summer. The new role involves web application development with Rails and so I needed to get up to speed. I had a web application requirement for my research so I figured I'd knock out two birds with one stone and build that [app with Rails](https://github.com/bbengfort/kahu) (a screenshot of the app is above, though of course this is just a front-end and doesn't really tell you it was built with Rails).

Now I'm by no means a web developer; I can create simple apps as universal UIs using Bootstrap and simple frameworks. I'm more likely to generate databases or APIs that much better front-end developers access. That said, I knew that if I did this project using Django, it would have probably taken me a day, maybe a day and half to get everything the way I wanted it. I knew there would be some learning curve to Rails, and so I figured I'd take three days over the July 4th holiday to knock this up. A week later ... here are my impressions and lessons learned.

### The Good

I'm not one of those evangelical developers that focuses on one tool or technology. My understanding of Ruby (thanks to [@looselycoupled](https://github.com/looselycoupled)) was that Matz created it to be fun for developers to code in. I totally get this from the pure Ruby side of things. Rails also seems like it is designed to get relative novice programmers up and running, building _professional_ websites as quickly as possible. In no particular order, here are some of my good vibes about Ruby and Rails.

#### RSpec and tests in tutorials

I'm not exactly a BDD or TDD guy, but I do write tests when I code (it's not just because I'm a professional, tests allow me to program fearlessly). I've always enjoyed the RSpec style testing that has a natural DSL for describing tests, their contexts, and matching. In fact, I use [Ginkgo](http://onsi.github.io/ginkgo/) for RSpec style testing in Go (haven't found one for Python yet, but if anyone has anything, let me know!)

Even more importantly than RSpec being cool, is the fact that Rails itself lends itself to generating tests and even more than that, most tutorials I encountered also included tests. I've always had a hard time testing web apps with Django, but I found it extremely easy and even enjoyable to test the Rails app.

#### 5.minutes.ago

This astounded me, and it took me a while to figure out what was happening. Basically this line of code returns a timestamp that is 5 minutes in the past. How?! Well, everything in Ruby is an object including numbers. Therefore the number 5 has a method called `minutes` (also `minute` for `1.minute.ago`) that converts the number into some kind of time delta. Then that thing has a method that subtracts it from `Time.now`. Mind blown. This reveals the fact that most objects in Ruby have a huge number of instance methods, presumably added via a huge number of mixins. This system is pretty neat, if possibly not the most performant thing in the world.

#### Assets and the front-end

One thing that always bothered me about Django was that static assets were only very loosely related to the application; Django focused on the backend details. Rails apps on the other hand put the front-end first, generating stylesheets and javascript on demand and building them with the asset pipeline for delivery. The front-end feels like a major component of a Rails app, not just the HTML rendering bits.

This also has a lot to do with the built-in compiling for SASS and CoffeeScript in the asset pipeline by the Rails app. Unlike a Python app, gems are available for the front-end tools I use every day. Rather than download JavaScripts and stylesheets, I instead gem installed them and included them in my requirements. It was much easier to get jQuery, Bootstrap, Underscore, etc. this way. The big win was really [gmaps4rails](https://github.com/apneadiving/Google-Maps-for-Rails) &mdash; it was a snap to get those maps up and running in the app!

#### Secrets

I don't really know how `secrets.yml` works, but I'm glad it's there and I hope that it's doing some fancy hiding of variables. I have my API keys and passwords etc in the environment, and I'm used to loading them into the configuration using `ENV` (or rather, `os.environ`). Something about `secrets.yml` just rubs me the right way though.

#### RESTful by design

The `resources` route configuration is amazing. While I'm very used to creating RESTful APIs, I recognize that REST was originally intended for HTML documents and resources. Couple this directly with controller methods such as `index`, `create`, `update`, `destroy` it made the application extremely intuitive to create and design.

### The Bad

At the risk of sounding simply annoyed because Ruby isn't my favorite programming language or Rails isn't my web framework of choice, I do want to point out some struggles I had that I don't think were related to the learning curve.

#### Autoloader and requiring files

By far my biggest challenge was creating the geoip component of the app, which was a client that queried another API for the latitude and longitude of a given IP address. Here was the problem: I built that component in plain Ruby in about 20 minutes. I could run the Ruby script from the command line. Then I tried to add it to Rails and &hellip; it couldn't find my _dependencies_.

So first off, I knew that in order to get the app to find my library file or anything outside of a directory I needed to add it to the configuration. E.g. if I was going to create a directory, `app/services` then in `config/application.rb` I needed to do something like:

```ruby
config.autoload_paths += [
  "#{config.root}/app/services",
]
```

Additionally, I have to name the files as the lower snake case version of the class name. E.g. put `GeoipService` in a file called `services/geoip.rb`. So this is a bit annoying, and I think using `require` is much more obvious.

However, when the app gives you a `NameError: uninitialized constant Faraday` or `NameError: uninitialized constant HTTParty` (the two libraries I tried to use to make web requests), things get annoying. Was it in my `Gemfile`? Yes. Did I run `bundle install`? Yes. Did I run `bundle exec bin/rails server`? Yes. Do I have any idea how to deal with the autoloader? No.

I finally got it by putting my client script in `lib` and having that script `require` the library. This seemed to make Rails happy enough. Why? No idea.

#### Is it Ruby?

Having been warned by @looselycoupled that Rails and Ruby are different, I learned Ruby first, using the [Codecademy Ruby Tutorial](https://www.codecademy.com/learn/ruby) (mostly because this is what we tell our students to do and I wanted to try it out). That went well and I think I got a pretty good grasp on Ruby. In fact, I felt comfortable enough with Ruby to write some scripts -- at this point I just need to know more about the standard library and useful third party libraries to be effective.

On to Rails &mdash; wait is that Ruby? Rails describes itself as a &ldquo;Ruby-like domain specific language for developing web applications&rdquo; and I think they're right. Much of the syntax in a Rails app is sugar that exploits a number of nice qualities about Ruby. I can easily see how it may be difficult for a Rails developer to write a Ruby library, or even move on to other programming languages. I can also see how it is super difficult for a programmer in another language to figure out web applications with Rails.

#### What's in the model?

While I do like the migrations database management in Rails, I constantly finding myself asking where the model definition was. Properties are not specified explicitly in an `ActiveRecord` subclass, instead they're reflected from the database (as far as I can tell). So once a migration was created I had to remember if I created the `is_admin` or `admin` boolean field since it wasn't on the model I was working in. I became very reliant on `db/schema.rb` to tell me about the database!

#### Auth from scratch

I used the [Clearance gem by Thoughtbot](https://github.com/thoughtbot/clearance/) for user authentication, but it still felt like I had to roll a lot of the authentication from scratch. I'm sure Rails has some sort of CMS gem (and a lot of my choices were informed by the web app that I have to learn to hack on), but I was surprised that there was nothing there by default. I think that in the Rails world, if you're building web apps all the time you have very specific preferences about what you want to do with Auth; unfortunately I believe this is one place things should be standardized. It took a lot of my time and created anxiety that someone was going to hack into my app and ruin my research.

### The Ugly

Last a few comments that aren't necessarily bad and not necessarily good.

#### Wizardry is mysterious

Based on my conversations with other Rails developers and reading StackOverflow questions, it seems that everyone agrees that Rails is magic and does a lot of magical things. Unfortunately, magic is, by its nature, mysterious. There were many times I couldn't figure out what was going on because there were obfuscations or methods designed to create simple syntax.

Here is what I figured out: everything is a method, but a method doesn't have to have parentheses to be called, and hashes don't have to have braces. Therefore a line of code like

```
command something with this and that
```

Is easily possible, but `something with this and that` could be either:

1. arguments to the command method
2. a hash that's being passed to the command
3. a block or a description of a block

And really the only way to tell is to pay close attention to the commas and colons in the line of code (which is also not helped by symbols). This combined with monkey patching meant that I couldn't easily find method definitions to override them or ways to create my own methods.

I think experience will help, and certainly the compact, expressiveness of code is nice, but magic is mysterious.

#### Where is that file again?

All I have to say is this: my Rails code base seems to be 300 files with 50 lines of code in each file. My directory structure is so big (and things are so similarly named) that it was hard to find stuff.

## Conclusion

It's been a while since I learned a new programming language, and I love to learn new things. Ruby is really a joy to program in, though I think Python suits my scripting requirements a bit better. Rails is a solid framework for web development. I think that I'll do fine working with Rails at the new company.

However, I would probably not encourage my students to start with Ruby as a first language or Rails for web development (unless they intended to be professional web developers, which my students rarely are). I think once you're in that world it's a bit tricky to get out of it and the magic means that you're not necessarily learning programming fundamentals. Still, it is a professional grade tool for web developers, and I'm glad it exists.
