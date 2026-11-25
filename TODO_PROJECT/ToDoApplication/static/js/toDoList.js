$(document).ready(function() {
  var editTaskId = null;
  var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
  $.ajaxSetup({ headers: { "X-CSRFToken": csrfToken } });

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function(char) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
    });
  }
  function createTaskUI(tasks) {
    var list = $("#task-list").empty();
    if (!tasks.length) {
      list.append("<li class='list-group-item'>No tasks found.</li>");
      return;
    }
    $.each(tasks, function(_, task) {
      var item = $("<li>", { id: "task-" + task.id, class: "list-group-item" });
      var row = $("<div>", { class: "row align-items-center" });
      var details = $("<div>", { class: "col-md-8" });
      details.append($("<h4>").text(task.task_title));
      details.append($("<p>").text(task.task_description));
      details.append($("<p>").text("Priority: " + task.task_priority));
      details.append($("<p>").text("Status: " + task.task_status));
      var buttons = $("<div>", { class: "col-md-4 text-end" });
      buttons.append($("<button>", { type: "button", class: "btn btn-primary me-2 editTaskBtn", "data-task-id": task.id, text: "Edit Task" }));
      buttons.append($("<button>", { type: "button", class: "btn btn-danger delete-task-btn", "data-task-id": task.id, text: "Delete" }));
      item.append(row.append(details, buttons));
      list.append(item);
    });
  }
  function loadTasks() {
    $.getJSON("/get_task_list/").done(function(response) { createTaskUI(response.tasks); });
  }
  function loadFiltered(url, data) {
    $.getJSON(url, data).done(function(response) { createTaskUI(response.tasks); });
  }
  function clearForm() {
    $("#titleInput, #descriptionInput").val("");
    $("#prioritySelect, #statusSelect").val("");
    $(".error").empty();
  }
  function openTaskForm(taskId) {
    editTaskId = taskId;
    clearForm();
    $("#taskModalLabel").text(taskId ? "Edit Task" : "Add Task");
    $(".submitBtn").text(taskId ? "Save Changes" : "Add Task");
    $(".statusSelection").toggle(!!taskId);
    if (!taskId) { $("#taskModal").modal("show"); return; }
    $.getJSON("/get_or_edit_task/" + taskId + "/").done(function(task) {
      $("#titleInput").val(task.title);
      $("#descriptionInput").val(task.description);
      $("#prioritySelect").val(task.priority);
      $("#statusSelect").val(task.status);
      $("#taskModal").modal("show");
    });
  }

  loadTasks();
  $("#addTaskBtn").on("click", function() { openTaskForm(null); });
  $(document).on("click", ".editTaskBtn", function() { openTaskForm($(this).data("task-id")); });
  $(document).on("click", ".delete-task-btn", function() { $("#confirmDeleteBtn").data("task-id", $(this).data("task-id")); $("#deleteTaskModal").modal("show"); });
  $("#confirmDeleteBtn").on("click", function() {
    var id = $(this).data("task-id");
    $.post("/delete_task/" + id + "/").done(function() { $("#deleteTaskModal").modal("hide"); loadTasks(); });
  });
  $("#taskForm").on("submit", function(event) {
    event.preventDefault();
    $(".error").empty();
    var data = { title: $("#titleInput").val().trim(), description: $("#descriptionInput").val(), priority: $("#prioritySelect").val(), status: $("#statusSelect").val() };
    if (!data.title) { $("#titleError").text("Title is required."); return; }
    if (!data.priority) { $("#priorityError").text("Choose a priority."); return; }
    if (editTaskId && !data.status) { $("#statusError").text("Choose a status."); return; }
    var url = editTaskId ? "/get_or_edit_task/" + editTaskId + "/" : "/add_task/";
    $.post(url, data).done(function() { $("#taskModal").modal("hide"); $("#priority-filter, #status-filter").val("0"); loadTasks(); }).fail(function(xhr) {
      var errors = xhr.responseJSON && xhr.responseJSON.errors;
      if (errors) { $.each(errors, function(field, message) { $("#" + field + "Error").text(message); }); }
    });
  });
  $("#priority-filter").on("change", function() { $("#status-filter").val("0"); loadFiltered("/filter_task_priority/", { priority: $(this).val() }); });
  $("#status-filter").on("change", function() { $("#priority-filter").val("0"); loadFiltered("/filter_task_status/", { status: $(this).val() }); });
});
