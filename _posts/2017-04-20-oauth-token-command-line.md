---
layout: post
title:  "OAuth Tokens on the Command Line"
date:   2017-04-20 10:26:32 -0400
categories: snippets
---

This week I discovered I had a problem with my Google Calendar &mdash; events accidentally got duplicated or deleted and I needed a way to verify that my primary calendar was correct. Rather than painstakingly go through the web interface and spot check every event, I instead wrote a Go console program using the [Google Calendar API](https://developers.google.com/google-apps/calendar/quickstart/go) to retrieve events and save them in a CSV so I could inspect them all at once. This was great, and very easy using Google's Go libraries for their APIs, and the quick start was very handy.

My calendar is private, therefore in order to access it from the command line, I had to authenticate with Google using OAuth2. This is an external application workflow that is browser based, an application that wants to authenticate Google's service first redirects the client to Google with a token that allows Google to verify the application. The user logs in with Google, accepts the access the level the application wants, and Google sends the user back to the application with a token. That token, signed with the application secret allows the application to access Google on behalf of the user.

So, how do you do this type of authentication in the terminal? Basically, the console program prints out the link (or uses the `$GOOS` specific `open` command) and the user manually goes to the website. Google then provides the token in the browser, which the user has to copy and paste back into `stdin` on the command line. The good news is that if this token is cached somewhere, then this only has to be done once for multiple requests until the token expires or the user deletes it.

The Calendar API quickstart provided several functions for this, first looking to see if the token was cached on disk in a specific place in the user's home directory; and then if not available, performed the web authentication and cached the token locally. There are, however, a lot of moving parts to this including the configuration for where to store the cached token, as well as the application credentials stored in a file called `client_secret.json`. Rather than hardcode these things, I created an `Authentication` struct that managed all aspects of authentication and token gathering, and I present it to you here:

<script src="https://gist.github.com/bbengfort/ee6d3bda44b8cc8d10a26f66be9ced70.js"></script>

The primary entry point to this struct is the `auth.Token()` method, which retrieves the token from the cache, or starts the web authentication process to cache the token if it doesn't exist. This revolves around the key `auth.CachePath()` and `auth.ConfigPath()` that compute the default locations for the token cache and the `client_secret.json` file in a hidden directory in the user's home directory. The `Authentication` struct also provides `Load()`, `Save()` and `Delete()` functions for managing the cache directly.

This can be used to create an API client as follows:

```go
// Initialize authentication
auth := new(Authentication)

// Load the configuration from client_secret.json
config, err := auth.Config()
if err != nil {
	log.Fatal(err.Error())
}

// Load the token from the cache or force authentication
token, err := auth.Token()
if err != nil {
	log.Fatal(err.Error())
}

// Create the API client with a background context.
ctx := context.Background()
client = config.Client(ctx, token)

// Create the google calendar service
gcal, err = calendar.New(client)
if err != nil {
	log.Fatal("could not create the google calendar service")
}
```

And the service can be used to get the next 10 events on the calendar like so:

```go
// Create the time to get events from.
now := time.Now().Format(time.RFC3339)

// Get the events list from the calendar service.
events, err := gcal.Events.List("primary")
                          .ShowDeleted(false)
                          .SingleEvents(true)
                          .TimeMin(now)
                          .MaxResults(10)
                          .OrderBy("startTime")
                          .Do()

if err != nil {
    log.Fatal("unable to retrieve upcoming events: %v", err)
}

// Loop over the events and print them out.
for _, i := range events.Items {
    var when string
    // If the DateTime is an empty string,
    // the event is an all day event
    if i.Start.DateTime != "" {
        when = i.Start.DateTime
    } else {
        when = i.Start.Date
    }
    fmt.Printf("%s (%s)\n", i.Summary, when)
}
```

This is actually a complete example of using the Calendar API from the quickstart guide &mdash; most of the work comes from the interaction with OAuth2. But the good news is that the `Authentication` struct will work with most Google APIs, so long as you download the correct `client_secret.json`!
