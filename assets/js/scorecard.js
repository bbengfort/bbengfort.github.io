/*
 * scorecard.js
 * A simple application that keeps track of the progress of a project.
 */

// Fetches all issues associated with the dissertation milestone with the
// correct GitHub API call headers. Set the callbacks for success and fail
// when the issues are retrieved.
function getIssues(onSuccess, onError) {
  var milestone = 1;
  var url = "https://api.github.com/repos/bbengfort/printing-press/issues";

  $.ajax({
    type: "GET",
    url: url,
    dataType: 'json',
    data: {"milestone": milestone, "state": "all"},
    beforeSend: function(xhr) {
      xhr.setRequestHeader("Accept", "application/vnd.github.v3+json");
    },
    success: onSuccess,
    error: onError
  });
}

// Add all of the issues to the page and update the status bar.
function updateIssues(data, status, xhr) {
  var counts = {"ready": 0, "inProgress": 0, "done": 0};
  $.each(data, function(idx, item) {

    // Make the list link item to add to the page.
    var ref = $("<a>")
      .attr("href", item.url)
      .text(item.title);
    var li = $("<li>").append(ref);

    if (item.state == "closed") {
      // Handle "done" items
      counts["done"] += 1;
      $("#doneList").append(li);
      return true;
    }

    if (hasLabel(item, "in progress")) {
      // Handle "in progress" items
      counts["inProgress"] += 1;
      $("#inProgressList").append(li);
      return true;
    }

    // Handle "ready items"
    counts["ready"] += 1;
    $("#readyList").append(li)
  });

  // Update the progess bar
  var total = counts["ready"] + counts["inProgress"] + counts["done"];
  inProgressPcent = (counts["inProgress"] / total) * 100;
  donePcent = (counts["done"] / total) * 100;
  setProgressBar(inProgressPcent, donePcent);

  // Update the counts
  $.each(counts, function(key, val) {
    $("#" + key + "Count .count").text(val);
  });
}

// Display an error message when we can't access the GitHub API.
function githubError(xhr, status, err) {
  console.log(xhr);
  var errMsg = $("<p>")
    .addClass("error")
    .text("Couldn't load issues from GitHub: " + xhr.status + " " + xhr.statusText);

  $("#messages").append(errMsg);
}

// Set stacked progress bar percent with inProgress and Done percentages.
function setProgressBar(inProgress, done) {
  // Check to make sure we don't break the bar
  var total = inProgress + done;
  if (total > 100 || total < 0) {
    console.log("cannot update progress bar to " + total + "%");
    return
  }

  // Get the bar elements
  var inProgressBar = $("#inProgressBar");
  var doneBar = $("#doneBar");

  // Update the CSS properties of the bars
  inProgressBar.css("width", inProgress +"%");
  doneBar.css("width", done + "%");

  // Label the bars if we have enough space
  function labelBar(bar, amount) {
    if (amount > 8) {
      bar.text(amount.toFixed(1) + "%");
      bar.css("padding", "8px");
    } else {
      bar.empty();
      bar.css("padding", "0");
    }
  }

  labelBar(inProgressBar, inProgress);
  labelBar(doneBar, done);
}

// Check if a GitHub issue has a label or not
function hasLabel(issue, label) {
  for (i=0; i < issue.labels.length; i++) {
    if (issue.labels[i].name == label) {
      return true;
    }
  }
  return false;
}

// Executes fetch issues when the document is ready.
$(document).ready(function() {
  getIssues(updateIssues, githubError);
});
