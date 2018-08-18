---
layout: page
title: Scorecard
icon: list
---

<div id="messages"></div>

This scoreboard lists my current progress towards completion of my **dissertation**. The current tasks status is as follows:

<!-- Big numbers status with counts -->
<ul class="taskCounts">
    <li id="inProgressCount">In Progress: <span class="count">0</span></li>
    <li id="doneCount">Completed: <span class="count">0</span></li>
    <li id="readyCount">To Do: <span class="count">0</span></li>
</ul>

<!-- Progress Bar contains a stacked bar with in-progress and done tasks -->
<div id="progressBar">
    <span id="inProgressBar"></span>
    <span id="doneBar"></span>
</div>

The following listings show all tasks in progress, still to do, and already completed. The tasks are GitHub issues, so the link will take you to GitHub for more details about the task.

## Tasks in Progress

<ul id="inProgressList" class="taskList"></ul>

## Still To Do

<ul id="readyList" class="taskList"></ul>

## Tasks Completed

<ul id="doneList" class="taskList"></ul>

<!-- this loads the javascript for the scorecard app -->
{% include scorecard.html %}
