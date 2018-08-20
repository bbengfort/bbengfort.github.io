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

<table>
    <thead>
        <th>Date</th>
        <th>Deadline</th>
    </thead>
    <tbody>
        <tr>
            <td>SEPTEMBER 10, 2018</td>
            <td>Application for Graduation</td>
            <!-- All Grad Students: Final date to submit the Application for Graduation in order to graduate this semester/term. -->
        </tr>
        <tr>
            <td>SEPTEMBER 24, 2018</td>
            <td>Nomination of Dissertation Committee Form</td>
            <!-- Doctoral Students: Final date to submit Nomination of Dissertation Committee Form to the Office of the Registrar.  Committee form must be submitted at least 6 weeks before the scheduled defense. -->
        </tr>
        <tr>
            <td>NOVEMBER 9, 2018</td>
            <td>Dissertation Forms</td>
            <!-- Doctoral Students: Final date to submit: dissertation via ETD System and electronic publication form, to the Office of the Registrar.
            Dissertation directors to submit signed Report of Examining Committee form to the Office of the Registrar. -->
        </tr>
    </tbody>
</table>

The following listings show all tasks in progress, still to do, and already completed. The tasks are GitHub issues, so the link will take you to GitHub for more details about the task.

## Tasks in Progress

<ul id="inProgressList" class="taskList"></ul>

## Still To Do

<ul id="readyList" class="taskList"></ul>

## Tasks Completed

<ul id="doneList" class="taskList"></ul>

<!-- this loads the javascript for the scorecard app -->
{% include scorecard.html %}
