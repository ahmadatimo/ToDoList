
// for Stylish UI only!!

function openAddForm() {
    document.getElementById('addTaskOverlay').style.display = 'block';
}

function closeAddForm() {
    document.getElementById('addTaskOverlay').style.display = 'none';
}

function openDeleteForm() {
    document.getElementById('deleteTaskOverlay').style.display = 'block';
}

function closeDeleteForm() {
    document.getElementById('deleteTaskOverlay').style.display = 'none';
}

function openEditForm() {
    document.getElementById('editTaskOverlay').style.display = 'block';
}

function closeEditForm() {
    document.getElementById('editTaskOverlay').style.display = 'none';
}

function openFinishForm(){
    document.getElementById("finishTaskOverlay").style.display = 'block';
}

function closeFinishForm(){
    document.getElementById("finishTaskOverlay").style.display = 'none';
}

function toggleAddCompletionTime() {
    const status = document.getElementById('status').value;
    const completionTimeField = document.getElementById('completionTimeFieldAdd');
    if (status === 'Done') {
        completionTimeField.style.display = 'block';
    } else {
        completionTimeField.style.display = 'none';
    }
}

function toggleEditCompletionTime() {
    const status = document.getElementById('status_edit').value;
    const completionTimeField = document.getElementById('completionTimeFieldEdit');
    if (status === 'Done') {
        completionTimeField.style.display = 'block';
    } else {
    completionTimeField.style.display = 'none';
    }
}