// ADDING TASKS
var form = document.getElementById('add-task-form');
var taskList = document.getElementById('task-list');
form.addEventListener('submit', (event) => {
  event.preventDefault();
  // Grab data we need from submit form
  const title = document.getElementById('new-task-title').value.trim();
  const description = document.getElementById('new-task-description').value.trim();
  const data = {
    title: title,
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
    alert('An error occurred while adding the task');
  });
});


// DELETING TASKS
// Delete buttons only correctly implemented when page is reloaded
var delButtons = document.querySelectorAll('.del-button');
// Then, add an event listener for each button
delButtons.forEach((button) => {
  button.addEventListener('click', (event) => {
    event.preventDefault();
    // Grab data we need: task's unique ID
    const taskId = event.target.dataset.taskId;
    const data = {
      taskId: taskId
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
      alert('An error occurred while deleting the task');
      });
    });
  });