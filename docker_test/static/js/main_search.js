var MAX_UPLOAD_SIZE_MB = 100;
var MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024;
var extensions = ['mp4', 'flv', 'avi', 'wmv', 'mov']

function checkFile() {
    var file = document.getElementById('upload-file');
    var extension = file.value.split('.').pop();
    if(file.files[0] && file.files[0].size < MAX_UPLOAD_SIZE && extensions.indexOf(extension) > -1){
        return true;
    }

    document.getElementById('notification').innerHTML = 'Invalid video. Please a select a video (' + extensions + ') at most ' + 
                                                            MAX_UPLOAD_SIZE_MB + 'MB';
    return false;
}