// User should always be able to just type away when the page
// loads and get a new task going
document.getElementById('new-task-description').focus();

// ADDING TASKS - "Create"
var form = document.getElementById('add-task-form');
var taskList = document.getElementById('task-list');
form.addEventListener('submit', (event) => {
  event.preventDefault();
  // Grab data we need from submit form
//   const title = document.getElementById('new-task-title').value.trim();
  const description = document.getElementById('new-task-description').value.trim();
  const data = {
    // title: title,
    description: description
  };

  // Invoke add_task method from views.py
  fetch('/add_task', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // TODO Longer-term, make more dynamic
      // Some work on this has been done: see "dynamicTasks.html" in archive
      location.reload();
    } else {
      alert('Failed to add task: ' + data.message);
    }
  })
  .catch(error => {
    console.error(error);
    alert('An error occurred while adding the task.');
  });
});


// DELETING TASKS - "Delete"
// Delete buttons only correctly implemented when page is reloaded
var delButtons = document.querySelectorAll('.del-button');
// Then, add an event listener for each button
delButtons.forEach((button) => {
  button.addEventListener('click', (event) => {
    event.preventDefault();
    // Grab data we need: task's unique ID
    const taskID = event.target.dataset.taskId;
    const data = {
      taskID: taskID
    }

    // Invoke delete_task method from views.py
    fetch('/delete_task', {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // TODO Longer-term, make more dynamic
        location.reload();
      } else {
        alert('Failed to delete task. Please refresh the page and try again.');
      }
    })
    .catch(error => {
      console.error(error);
      alert('An error occurred while deleting the task.');
      });
    });
  });


// EDITING TASKS - "Update"
// Edit buttons only correctly implemented when page is reloaded
// TODO Make this a little smarter: user can change the innerText of the
//  button and relying on it for logic is a little silly, but works
//  for now
var editButtons = document.querySelectorAll('.edit-button');
editButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
        event.preventDefault();

        if (event.target.dataset.state === "edit") {
          // Hide the finish task button: done editing button will use the same 
          // check mark symbol, so want to avoid confusing the user, as well as not 
          // having to deal with the situation where they hit the finished button
          // while editing the task
          const taskID = event.target.dataset.taskId; // Unique task ID
          const finishTaskID = "finish_task_" + taskID;
          const finishTaskButton = document.getElementById(finishTaskID);
          finishTaskButton.style.display = 'none'; // Get rid of it!

          // Now, make it known that the button is in a different state, and
          // show the user this as well by changing symbol shown
          event.target.dataset.state = "doneEditing";
          event.target.innerText = "✓";

          // Change the task being shown as a <p> element into an
          //  editable <form> with an <input> child          
          var existingTaskTextElement = document.getElementById("task_text_" + taskID);
          
          // Create new element, a form which will have an input child
          var newFormElement = document.createElement("form");
          newFormElement.setAttribute("id", "edit-task-form-" + taskID);
          newFormElement.setAttribute("class", "edit-task-form");

          // Format the input child element
          var formInputElement = document.createElement("input");
          formInputElement.setAttribute("type", "text");
          formInputElement.setAttribute("id", "edit-task-input-" + taskID);
          
          // Fill the input field with the existing task's original text
          formInputElement.value = existingTaskTextElement.innerText;
          
          // Finalize form element, then *replace* task text element
          //  with this new form, and then focus on the form
          newFormElement.appendChild(formInputElement);
          existingTaskTextElement.parentNode.replaceChild(newFormElement,
                                                          existingTaskTextElement);
          formInputElement.focus();
        } else if (event.target.dataset.state === "doneEditing") {
            // Invoke edit_task method from views.py
            const taskID = event.target.dataset.taskId; // Unique task ID
            const formInputElement = document.getElementById("edit-task-input-" + taskID);
            const newTaskText = formInputElement.value;
            const data = {
                taskID: taskID,
                newTaskText: newTaskText
            };

            fetch('/edit_task', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // TODO Longer-term, make more dynamic
                    location.reload();
                } else {
                    alert('Failed to edit task. Please refresh the page and try again.');
                }
            })
            .catch(error => {
                console.error(error);
                alert('An error occurred while editing the task.');
            });
        }
    });
});


// COMPLETING TASKS - also "Update"
// This one is fairly simple: just strike through the text, then send a signal
// to the backend indicating that the task has been completed, so that when the
// user returns, the task is still finished (the whole point of the backend).
var finButtons = document.querySelectorAll('.finish-button');
// Then, add an event listener for each button
finButtons.forEach((button) => {
  button.addEventListener('click', (event) => {
    event.preventDefault();
    // Strike through text of the task
    const taskID = event.target.dataset.taskId;
    
    const data = {
      taskID: taskID
    }

    // Invoke complete_task method from views.py
    fetch('/complete_task', {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Strike through text of task
        var taskText = document.getElementById("task_text_" + taskID);
        if (taskText.classList.contains("struck-through")) {
          taskText.classList.remove("struck-through");
        } else {
          taskText.classList.add("struck-through");
        }
      } else {
        alert('Failed to set task to complete. Please refresh the page and try again.');
      }
    })
    .catch(error => {
      console.error(error);
      alert('An error occurred while setting the task to completed.');
      });
    });
  });