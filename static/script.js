// Fetch and display tasks
function loadTasks() {
    fetch("/tasks")
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("taskList");
            list.innerHTML = "";
            data.forEach(task => {
                const li = document.createElement("li");
                li.className = "list-group-item d-flex justify-content-between align-items-center";
                li.innerHTML = `
                    ${task.task} <small class="text-muted">${task.created_at}</small>
                    <button class="btn btn-danger btn-sm" onclick="deleteTask('${task.id}')">Delete</button>
                `;
                list.appendChild(li);
            });
        });
}

// Add task
function addTask() {
    const task = document.getElementById("taskInput").value;
    if (task.trim()) {
        fetch("/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task })
        }).then(() => {
            document.getElementById("taskInput").value = "";
            loadTasks();
            loadChart();
        });
    }
}

// Delete task
function deleteTask(id) {
    fetch(`/tasks/${id}`, { method: "DELETE" })
        .then(() => {
            loadTasks();
            loadChart();
        });
}

// Load chart
function loadChart() {
    fetch("/chart-data")
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("taskChart").getContext("2d");
            if (window.taskChart) {
                window.taskChart.destroy();
            }
            window.taskChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Tasks Added",
                        data: data.counts,
                        borderColor: "blue",
                        backgroundColor: "lightblue",
                        fill: true
                    }]
                }
            });
        });
}

// Initial load
loadTasks();
loadChart();
