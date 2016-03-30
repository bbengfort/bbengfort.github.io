---
layout: post
title:  "Simple Password Generation"
date:   2016-03-30 09:07:21 -0400
categories: snippets
---

I was talking with [@looselycoupled](https://github.com/looselycoupled) the other day about how we generate passwords for use on websites. We both agree that every single domain should have its own password (to prevent one crack ruling all your Internets). However, we've both evolved on the method over time, and I've written a simple script that allows me to generate passwords using methodologies discussed in this post.

In particular I use the generator to create passwords for [pwSafe](http://pwsafe.info/), the tool I currently use for password management (due to its use of the [open source database format](https://raw.githubusercontent.com/jpvasquez/PasswordSafe/master/docs/formatV3.txt) created by [Bruce Schneier](https://www.schneier.com/blog/archives/2005/06/password_safe.html)). It is my hope that this script can be embedded directly into pwSafe, or at least allow me to write directly to the database; but for now I just copy and paste with the `pbcopy` utility.

The point of this post, though, is not the generator (though I hope it can be useful). The point of the post is that because I do not believe in security through _obscurity_ or _obfuscation_ I want to expose my techniques to criticism and testing publicly. I believe that an approach to security must be ongoing, living, and continuous. While the foundation of security revolves around some _shared secret_ (a key, a password) that must not be made public, the way that secret is used should be open and constantly inspected for flaws.

So although this post isn't really about anything and is quite simple, it does put my money where my mouth is, philosophically speaking. If you're reading this, I hope you read with a critical eye and report any flaws you spot in the [comments of the snippet on GitHub Gist](https://gist.github.com/bbengfort/02fa5be3413d494e282bf3ddb0e3f3a5#comments).

## Previous Approaches

My original approach was pretty simple: keep three versions of the same password in a variety of strengths:

    password
    p4ssw0rd
    p4$$w0rd

In order to generate domain specific passwords, just append a few characters from the site. So for example, for Facebook, Gmail, and PayPal you might use `passwordfb`, `p4ssw0rdgmail`, and `p4$$w0rdpp` respectively, in order of increasing "security". The benefit of this approach is simple, memorable passwords that meet a variety of security features required by websites.

Of course, the flaws are numerous here. All passwords should have the same level of security, using a variety of characters. Additionally the use of a discoverable pattern could make a targeted attack easy. The real problem for me, however, was that on sites that required a routine password change (which should be done anyway). This method does not lend flexibility. However, it does highlight the trade-off between ease of use and security, however, which led my to my next approach.

The next approach did the same thing, but instead of adding letters and symbols, I used a long, correct sentence inspired by the [xkcd Password Strength comic](https://xkcd.com/936/). A characteristic of the domain is simply fit into the base sentence:

    base: "Silly banana, happy elephant."
    facebook: "Silly facebook, happy elephant."

This allowed me to change the password by moving the domain phrase around or performing other manipulations, while also having longer, more secure passwords that I could easily remember. Still, having a template seemed like a bad idea.

## Password Management

After a while, however, I finally started using pwSafe and started generating random passwords for each site. This is clearly the best way to do things but in all honesty - the [most important thing to secure is your email and any social auth accounts](http://www.wired.com/2012/11/ff-mat-honan-password-hacker/). To that end, I set up [2 factor authentication](http://lifehacker.com/5938565/heres-everywhere-you-should-enable-two-factor-authentication-right-now) using [Google Authenticator](https://en.wikipedia.org/wiki/Google_Authenticator) as much as I could, and text messaging where I couldn't.

I don't think I'm paranoid, this just seems like good Internet hygiene. The appendix includes a list of the sites that I use 2 factor authentication and please let me know if there are any others I should include.

The issue, of course, is that I'm paranoid that I'll lose or misplace my pwSafe master key, have the database corrupted, or otherwise be locked out of my accounts. I want a methodology that creates passwords that are as secure as possible that I can also reproduce on my own. The password should be domain specific, unique, long, and contain a variety of characters.

## Reproducible Methodology

So here's the idea:

1. Create a master password
2. Create a password string by concatenating the master, the base url of the site, and some salt or incrementing value.
3. Hash the password string
4. Encode the hash and use as password.

Now all you have to remember is the master password and the salt or incrementing value on a per-domain basis.

Issues:

1. What encoding scheme do you choose? Some sites require special characters and numbers, others cannot accept them. The domain of the characters is now also reduced to 16 chars for hex encoding, or 64 chars for base64 (even if you use one with special characters like hexbin).
2. How do you verify the master password (ensuring there was no typo).
3. How do you remember the salt? Perhaps something device specific like a UUID?

I'm sure there are more issues here as well.

However, I'm hoping this is good enough when combined with 2FA, this password is just a first step, and gives me the ability to reproduce the sequence of characters for crucial sites in case the pwSafe database is corrupted. For most sites, I'll simply use a randomly generated password and rely on the "forgot password" link.

<script src="https://gist.github.com/bbengfort/02fa5be3413d494e282bf3ddb0e3f3a5.js"></script>

## Conclusion

So in this post, I've presented a simple, reproducible method for generating somewhat secure passwords that I intend to use in combination with two factor authentication. It is my hope that these passwords are long enough, unique to the domain, but able to be generated on demand.

This is a list of the sites that I have set up 2 factor authentication with, for reference.

- Google and Gmail Accounts
- Apple ID
- GitHub
- Facebook
- Twitter
- PayPal
- Heroku
- AWS
- LinkedIn 
